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

#include "Constants.hpp"
#include "AdcManager.hpp"
#include "DacManager.hpp"
#include "Arduino.h"
#include "ADC.h"
#include "IntervalTimer.h"

//----------------------- Private Variables ---------------------

IntervalTimer  AdcSampleTimer;
ADC            Adc;
uint8_t        adcAverages = ADC_DEFAULT_AVERAGES;
float          adcSampleFrequency = ADC_DEFAULT_SAMPLEFREQUENCY;
elapsedMicros  duration;
uint32_t       totalPacketCount = 0;
uint32_t       currentSampleCount = 0;
bool           doSample = false;
#ifdef ADC_DEBUG
volatile bool lastOn = false;
#endif

//----------------------- Public Functions ----------------------

void Adc_samplePrep();

/*
 * Description:
 *  Initializes hardware resources for the ADC.
 */
void Adc_init() {
  pinMode(ADC_PIN, INPUT);
  AdcSampleTimer.priority(ADC_SAMPLEPRIORITY);
  Adc.enableInterrupts(ADC_0);
  Adc.setAveraging(adcAverages);
  Adc.setResolution(8);
  Adc_pause();
  #ifdef ADC_DEBUG
  pinMode(ADC_DEBUG_PIN_SAMPLE, OUTPUT);
  pinMode(ADC_DEBUG_PIN_BUFFERXCHANGE, OUTPUT);
  #endif
}

/*
 * Description:
 *  Returns a pointer to the most recent sampleBuffer struct.
 *
 * Returns:
 *  Pointer to the latest and greatest.
 */
sampleBuffer * Adc_getLatestBuffer() {
  return AdcBuffer_getTail();
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
 *
 */
uint8_t Adc_getAverages() {
  return adcAverages;
}

/*
 * Description:
 *  Sets the number of averages, value must be 0, 4, 8, 16 or 32.
 *
 * Parameters:
 *  'newAverages' The number of samples per adc result.
 */
bool Adc_setAverages(uint8_t newAverages) {
  if((newAverages % 4 == 0) && (newAverages <= 32)) {
    adcAverages = newAverages;
    return true;
  }
  return false;
}

/*
 * Description:
 *  Halts interrupts for the ADC conversion. Note
 *  that all elements in the buffer are reset.
 */
void Adc_pause() {
  doSample = false;
  AdcBuffer_resetBuffer();
  currentSampleCount = 0;
  duration           = 0;
  Adc.setAveraging(adcAverages);
  AdcSampleTimer.begin(Adc_samplePrep, MICROSFROMFREQ(adcSampleFrequency));
}

/*
 * Description:
 *  Propmpts ADC conversion to begin.
 */
void Adc_samplePrep() {
  if(doSample) {
    Adc.startSingleRead(ADC_PIN, ADC_0);
    #ifdef ADC_DEBUG // TODO lighting does not seem to alternate properly, on for too short a time.
    digitalWriteFast(ADC_DEBUG_PIN_SAMPLE, HIGH);
    #endif
  }
}

/*
 * Description:
 *  Resumes interrupts for the ADC conversion.
 */
void Adc_resume() {
  doSample = true;
}

/*
 * Description:
 *  The actual interrupt called when conversion is complete.
 */
void adc0_isr() {
  static sampleBuffer * currentSample = AdcBuffer_getHead(); // TODO first buffer does not have proper Aoffset and Boffset, maybe does not matter since both are 0?
  currentSample->data[currentSampleCount++] = Adc.readSingle();
  #ifdef ADC_DEBUG // TODO lighting does not seem to alternate properly, on for too short a time.
  digitalWriteFast(ADC_DEBUG_PIN_SAMPLE, LOW);
  #endif
  if(currentSampleCount >= ADC_BUFFERSIZE) {
    #ifdef ADC_DEBUG
    digitalWriteFast(ADC_DEBUG_PIN_BUFFERXCHANGE, lastOn);
    lastOn = !lastOn;
    #endif
    currentSample->duration = duration;
    currentSample->number = totalPacketCount++;
    duration = 0;
    currentSampleCount = 0;
    currentSample = AdcBuffer_getHead();
    currentSample->aStart = Dac_getAOffsetMicros();
    currentSample->bStart = Dac_getBOffsetMicros();
  }
}
