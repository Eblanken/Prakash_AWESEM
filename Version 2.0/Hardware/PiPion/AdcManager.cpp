/*
 * File: AdcManager.cpp
 * ------------------------------
 * Author: Erick Blankenberg
 * Date:   8/12/2018
 *
 * Description:
 *  This is the implementation of the Adc management methods. See the
 *  header file for description and intended use.
 *  
 * Note:
 *  This implementation uses interval timers to sample from the ADC, 
 *  a faster implementation would use continuous conversion and interrupts.
 */

#include "AdcManager.hpp"
#include "DacManager.hpp"
#include "Arduino.h"
#include "ADC.h"
#include "CircularBuffer.h"
#include "IntervalTimer.h"

//----------------------- Private Variables ---------------------

IntervalTimer                                         AdcSampleTimer;
#define CIRCULAR_BUFFER_INT_SAFE
CircularBuffer<sampleBuffer, ADC_BUFFERSIZE>          AdcBuffer;
ADC                                                   Adc;
float                                                 adcSampleFrequency = 5000;
#ifdef ADC_DEBUG
bool lastOn = false;
#endif

//----------------------- Public Functions ----------------------

#define MICROSFROMFREQ(frequency) (1000000.0 / frequency)

/*
 * Description:
 *  Constructor for the adc manager class.
 */
void Adc_init() {
  pinMode(ADC_PIN, INPUT);
  AdcSampleTimer.priority(ADC_SAMPLEPRIORITY);
  Adc.enableInterrupts(ADC_0);
  Adc.setAveraging(ADC_AVERAGES);
  Adc.setResolution(8);
  #ifdef ADC_DEBUG
  pinMode(ADC_DEBUG_PIN, OUTPUT);
  #endif
}

/*
 * Description:
 *  Returns a pointer to the most recent sampleBuffer struct.
 * 
 * Returns:
 *  Pointer to the latest and greatest.
 */
sampleBuffer Adc_getLatestBuffer() {
  return AdcBuffer.pop(); // TODO very inefficient handling of data            
}

/*
 * Description:
 *  Returns whether or not any data is ready to be taken.
 *  
 * Returns:
 *  True if there is data available, false otherwise.
 */
bool Adc_bufferReady() {
  return AdcBuffer.size() > 0;
}

/*
 * Description:
 *  Sets the frequency of the interval timer in microseconds.
 * 
 * Note:
 *  Changes are not applied until pause and resume are called.
 */
void Adc_setFrequency(float newFrequency) {
  adcSampleFrequency = newFrequency;
}

/*
 * Description:
 *  returns the frequency of the interval timer in microseconds.
 */
float Adc_getFrequency() {
  return adcSampleFrequency;
}

/*
 * Description:
 *  Halts interrupts for the ADC conversion. Note
 *  that all elements in the buffer are reset.
 */
void Adc_pause() {
  AdcSampleTimer.end();
  AdcBuffer.clear();
}

/*
 * Description:
 *  Propmpts ADC conversion to begin.
 */
void Adc_samplePrep() {
  #ifdef ADC_DEBUG
  digitalWrite(ADC_DEBUG_PIN, HIGH);
  #endif
  Adc.startSingleRead(ADC_PIN, ADC_0);
}

/*
 * Description:
 *  Resumes interrupts for the ADC conversion.
 */
void Adc_resume() {
  AdcSampleTimer.begin(Adc_samplePrep, MICROSFROMFREQ(adcSampleFrequency));
}

/*
 * Description:
 *  The actual interrupt called when conversion is complete.
 */
void adc0_isr() {
  static elapsedMillis duration; // Increments automatically
  static sampleBuffer currentSample; // Bit the bullet and used a struct directly in the queue, there may be faster ways to do this
  currentSample.data[currentSample.currentSize++] = Adc.readSingle();
  // TODO seperate intervaltimer for shifting data, we may be losing data here.
  if(currentSample.currentSize >= ADC_SAMPLESIZE) {
    currentSample.duration = duration;
    AdcBuffer.unshift(currentSample);
    #ifdef ADC_DEBUG // TODO lighting does not seem to alternate properly, on for too short a time.
    if(lastOn) {
      digitalWriteFast(ADC_DEBUG_PIN, LOW);
      lastOn = false;
    } else {
      digitalWriteFast(ADC_DEBUG_PIN, HIGH);
      lastOn = true;
    }
    #endif
    duration = 0;
    currentSample.currentSize = 0; // Same buffer is recycled endlessly
    currentSample.aStart = Dac_getAOffsetMicros();
    currentSample.bStart = Dac_getBOffsetMicros();
  }
}

