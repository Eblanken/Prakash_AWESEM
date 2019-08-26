/*
 * File: DacManager.cpp
 * ------------------------------
 * Author: Erick Blankenberg
 * Date:   8/12/2018
 *
 * Description:
 *  This is the implementation of functions for the DAC.
 *
 * TODO
 *  - Currently offset rolls over pre-maturely when slow axis is running too slow and overflows?
 *    It seems that the intervaltimer has a limit of 71582788 microseconds depending on F_BUS but overflows at about 33 seconds.
 */

#include "Constants.hpp"
#include "DacManager.hpp"
#include "Arduino.h"
#include "Stroffgen_Audio_Audio.h"
#include "IntervalTimer.h"

//----------------------- Internal Variables ---------------------

IntervalTimer            lastCrossover_0_updater;
IntervalTimer            lastCrossover_1_updater;
uint32_t                 lastCrossover_0;
uint32_t                 lastCrossover_1;
float                    waveSynth_0_Frequency = DAC_DEFAULT_FREQUENCY_0; // > Frequency in hertz
float                    waveSynth_1_Frequency = DAC_DEFAULT_FREQUENCY_1; // > Frequency in hertz
uint8_t                  waveSynth_0_Waveform  = DAC_DEFAULT_WAVEFORM_0;  // > Waveform types are 0 = Sine, 1 = Sawtooth, 3 = Triangle
uint8_t                  waveSynth_1_Waveform  = DAC_DEFAULT_WAVEFORM_1;  // > Waveform types are 0 = Sine, 1 = Sawtooth, 3 = Triangle
float                    waveSynth_0_Vpp = DAC_DEFAULT_VPP_0; // > Magnitude relative to reference, [0 - 1] * vRef
float                    waveSynth_1_Vpp = DAC_DEFAULT_VPP_1; // > Magnitude relative to reference, [0 - 1] * vRef
AudioSynthWaveform       waveSynth_0;
AudioSynthWaveform       waveSynth_1;
AudioOutputAnalogStereo  Dacs;
AudioConnection          PatchCord2(waveSynth_0, 0, Dacs, 0);
AudioConnection          PatchCord1(waveSynth_1, 0, Dacs, 1);
bool                     debugBToggleOnPeriod = false;

//----------------------- Functions ----------------------

#if DAC_REFERENCE == EXTERNAL
#define DAC_BASEVOLTAGE ((float) 3.3)
#else
#define DAC_BASEVOLTAGE ((float) 1.2)
#endif

/*
 * Description:
 *  Constructor for the adc manager class.
 */
void Dac_init() {
  pinMode(A21, OUTPUT);
  pinMode(A22, OUTPUT);
  AudioMemory(10);
  Dacs.analogReference(DAC_REFERENCE);
  lastCrossover_0_updater.priority(DAC_PRIORITY_0);
  lastCrossover_1_updater.priority(DAC_PRIORITY_1);
  #ifdef DAC_DEBUG
  pinMode(DAC_DEBUG_PIN_0, OUTPUT);
  pinMode(DAC_DEBUG_PIN_1, OUTPUT);
  pinMode(DAC_DEBUG_PIN_R, OUTPUT);
  digitalWrite(DAC_DEBUG_PIN_0, LOW);
  digitalWrite(DAC_DEBUG_PIN_1, LOW);
  digitalWrite(DAC_DEBUG_PIN_R, LOW);
  #endif
}

/*
 * Description:
 *  Sets the frequency of the given DAC channel in hertz.
 *
 * Parameters:
 *  'targetChannel' (dacChannel)    Which channel to update.
 *  'newFrequency'  (float [hertz]) Frequency at which to play the waveform
 *
 * Note:
 *  Changes are not applied until after pause and resume are called.
 */
bool Dac_setFrequency(uint8_t targetChannel, float newFrequency) {
  if(targetChannel == 0) {
    waveSynth_0_Frequency = newFrequency;
    return true;
  } else if(targetChannel == 1){
    waveSynth_1_Frequency = newFrequency;
    return true;
  }
  return false;
}

/*
 * Description:
 *  Returns the frequency of the interval timer in microseconds.
 *
 * Parameters:
 *  'targetChannel' The channel to retrieve the frequency from
 */
float Dac_getFrequency(uint8_t targetChannel) {
  if(targetChannel == 0) {
    return waveSynth_0_Frequency;
  } else if(targetChannel == 1) {
    return waveSynth_1_Frequency;
  }
  return 0;
}

/*
 * Description:
 *  Sets the magnitude in volts of the given dac channel.
 *
 * Note:
 *  Is not applied until pause and resume is called.
 */
bool Dac_setMagnitude(uint8_t targetChannel, float magnitude) {
  magnitude /= (float) DAC_BASEVOLTAGE;
  if(magnitude > 1) {
    magnitude = 1.0;
  }
  if(targetChannel == 0) {
    waveSynth_0_Vpp = magnitude;
    return true;
  } else if(targetChannel == 1){
    waveSynth_1_Vpp = magnitude;
    return true;
  }
  return false;
}

/*
 * Description:
 *  Returns the magnitude of the target dac channel in volts.
 *
 * Parameters:
 *  'targetChannel' (dacChannel) Which channel to request the magnitude from.
 */
float Dac_getMagnitude(uint8_t targetChannel) {
  if(targetChannel == 0) {
    return waveSynth_0_Vpp * DAC_BASEVOLTAGE;
  } else if(targetChannel == 1) {
    return waveSynth_1_Vpp * DAC_BASEVOLTAGE;
  }
  return 0;
}


/*
 * Description:
 *  Sets the internal arbitrary waveform data that the system will use if the waveform is switched to arbitrary.
 *
 * Parameters:
 *  'dataPointer' Pointer to first element of arbitrary waveform array, array size needs to be 256.
 * 
 * Note:
 *  Will pause and resume while setting waveform if the current waveform is the arbitrary waveform.
 */
bool Dac_setArbWData(uint8_t targetChannel, int16_t dataVals[256]) {
  bool success = false;
  bool isUsingArb = ((waveSynth_0_Waveform == 4) || (waveSynth_1_Waveform == 4)); // At least one is using arbitrary waveform
  if(isUsingArb) Dac_pause();
  if(targetChannel == 0) {
    waveSynth_0.arbitraryWaveform(dataVals, 100.0);
    success = true;
  } else if(targetChannel == 1) {
    waveSynth_1.arbitraryWaveform(dataVals, 100.0);
    success = true;
  }
  if(isUsingArb) Dac_resume();
  return success;
}

/*
 * Description:
 *  Sets the waveform of the target channel.
 *
 * Parameters:
 *  'targetChannel' The channel to set the waveform for.
 *
 * Note:
 *  Changes will not take effect until pause and resume are called.
 */
bool Dac_setWaveform(uint8_t targetChannel, uint8_t desiredWaveform) {
  if(targetChannel == 0) {
    waveSynth_0_Waveform = desiredWaveform;
    return true;
  } else if(targetChannel == 1) {
    waveSynth_1_Waveform = desiredWaveform;
    return true;
  }
  return false;
}

/*
 * Description:
 *  Returns the waveform assigned to the given DAC channel.
 */
uint8_t Dac_getWaveform(uint8_t targetChannel) {
  if(targetChannel == 0) {
    return waveSynth_0_Waveform;
  } else if(targetChannel == 1) {
    return waveSynth_1_Waveform;
  }
  return 0;
}

/*
 * Description:
 *  Returns the time in microseconds since the last
 *  A waveform began.
 *
 * Returns:
 *  The time offset in microseconds.
 */
uint32_t Dac_getOffsetMicros_0() {
  return micros() - lastCrossover_0;
}

/*
 * Description:
 *  Returns the time in microseconds since the last
 *  B waveform began.
 *
 * Returns:
 *  The time offset in microseconds.
 */
uint32_t Dac_getOffsetMicros_1() {
  return micros() - lastCrossover_1;
}

/*
 * Description:
 *  Turns off the DAC output.
 */
void Dac_pause() {
  waveSynth_0.amplitude(0);
  waveSynth_1.amplitude(0);
}


/*
 * Description:
 *  Resets the A timer at the end of the last A period.
 */
void Dac_updateCrossoverTimer_0() {
  #ifdef DAC_DEBUG
  static bool debugToggleOnPeriod_0 = false;
  digitalWrite(DAC_DEBUG_PIN_0, debugToggleOnPeriod_0);
  debugToggleOnPeriod_0 = !debugToggleOnPeriod_0;
  #endif
  lastCrossover_0 = micros();
}

/*
 * Description:
 *  Resets the B timer at the end of the last B period.
 */
void Dac_updateCrossoverTimer_1() {
  #ifdef DAC_DEBUG
  static bool debugToggleOnPeriod_1 = false;
  digitalWrite(DAC_DEBUG_PIN_1, debugToggleOnPeriod_1);
  debugToggleOnPeriod_1 = !debugToggleOnPeriod_1;
  #endif
  lastCrossover_1 = micros();
}

/*
 * Description:
 *  Returns phase so that all waveforms start at lower value
 *  and build up.
 */
float Dac_getSamplePhase(uint8_t waveSynth_0_Waveform) {
  switch(waveSynth_0_Waveform) { // > Waveform types are 0 = Sine, 1 = Sawtooth, 3 = Triangle
    case 0:
      return 270.0;
      break;
    case 1:
      return 180.0;
      break;
    case 3:
      return 270.0;
      break;
  }
  return 0;
}

/*
 * Description:
 *  Re-enables the DAC output but also implements any changes
 *  made since the last call.
 */
void Dac_resume() {
  pinMode(DAC_DEBUG_PIN_0, OUTPUT);
  pinMode(DAC_DEBUG_PIN_1, OUTPUT);
  AudioNoInterrupts();
  //digitalWrite(DAC_DEBUG_PIN_R, HIGH);
  waveSynth_0.begin(waveSynth_0_Waveform);
  waveSynth_1.begin(waveSynth_1_Waveform);
  waveSynth_0.frequency(waveSynth_0_Frequency);
  waveSynth_1.frequency(waveSynth_1_Frequency);
  waveSynth_0.phase(Dac_getSamplePhase(waveSynth_0_Waveform));
  waveSynth_1.phase(Dac_getSamplePhase(waveSynth_1_Waveform));
  AudioInterrupts();

  // Updates first channel
  digitalWriteFast(DAC_DEBUG_PIN_0, HIGH);
  waveSynth_0.amplitude(0);
  if(waveSynth_0_Vpp != 0) {
    // > Flushes old data
    delay(10);
    // > Restarts and catches first period start
    waveSynth_0.amplitude(waveSynth_0_Vpp);
    waveSynth_0.restart();    // Sets phase back so we can catch first crossover
    Dacs.forceSync0();
  }
  // > Starts timer to track crossovers indirectly
  lastCrossover_0 = micros();
  lastCrossover_0_updater.begin(Dac_updateCrossoverTimer_0, MICROSFROMFREQ(waveSynth_0_Frequency));
  digitalWriteFast(DAC_DEBUG_PIN_0, LOW);

  // Updates second channel if necessary
  digitalWriteFast(DAC_DEBUG_PIN_1, HIGH);
  waveSynth_1.amplitude(0);
  if(waveSynth_1_Vpp != 0) {
    // > Flushes old data
    delay(10);
    // > Restarts and catches first period start
    waveSynth_1.amplitude(waveSynth_1_Vpp);
    waveSynth_1.restart();    // Sets phase back so we can catch first crossover
    Dacs.forceSync1();
  }
  // > Starts timer to track crossovers indirectly
  lastCrossover_1 = micros();
  lastCrossover_1_updater.begin(Dac_updateCrossoverTimer_1, MICROSFROMFREQ(waveSynth_1_Frequency));
  digitalWriteFast(DAC_DEBUG_PIN_1, LOW);
  //digitalWrite(DAC_DEBUG_PIN_R, LOW);
}
