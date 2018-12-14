// TODO change to use singleton design pattern

/*
 * File: DacManager.cpp
 * ------------------------------
 * Author: Erick Blankenberg
 * Date:   8/12/2018
 *
 * Description:
 *  This is the implementation of functions for the DAC.
 */

#include "Constants.hpp"
#include "DacManager.hpp"
#include "Arduino.h"
#include "StroffgenAudio_Audio.h"
#include "IntervalTimer.h"

//----------------------- Internal Variables ---------------------

IntervalTimer            AUpdater;
IntervalTimer            BUpdater;
elapsedMicros            aDuration;
elapsedMicros            bDuration;
float                    channelAFrequency = DAC_DEFAULT_FREQUENCY_A; // > Frequency in hertz
float                    channelBFrequency = DAC_DEFAULT_FREQUENCY_B; // > Frequency in hertz
uint8_t                  channelAWaveform  = DAC_DEFAULT_WAVEFORM_A;  // > Waveform types are 0 = Sine, 1 = Sawtooth, 3 = Triangle
uint8_t                  channelBWaveform  = DAC_DEFAULT_WAVEFORM_B;  // > Waveform types are 0 = Sine, 1 = Sawtooth, 3 = Triangle
float                    channelAMagnitude = DAC_DEFAULT_MAGNITUDE_A; // > Magnitude relative to reference, [0 - 1] * vRef
float                    channelBMagnitude = DAC_DEFAULT_MAGNITUDE_B; // > Magnitude relative to reference, [0 - 1] * vRef
AudioSynthWaveform       ChannelA;
AudioSynthWaveform       ChannelB;
AudioOutputAnalogStereo  Dacs;
AudioConnection          PatchCord1(ChannelA, 0, Dacs, 1);
AudioConnection          PatchCord2(ChannelB, 0, Dacs, 0);
bool                     debugAToggleOnPeriod = false;
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
  AUpdater.priority(DAC_APRIORITY);
  BUpdater.priority(DAC_BPRIORITY);
  #ifdef DAC_DEBUG
  pinMode(DAC_DEBUG_PIN_A, OUTPUT);
  pinMode(DAC_DEBUG_PIN_B, OUTPUT);
  digitalWrite(DAC_DEBUG_PIN_A, LOW);
  digitalWrite(DAC_DEBUG_PIN_B, LOW);
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
    channelAFrequency = newFrequency;
    return true;
  } else if(targetChannel == 1){
    channelBFrequency = newFrequency;
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
    return channelAFrequency;
  } else if(targetChannel == 1) {
    return channelBFrequency;
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
    channelAMagnitude = magnitude;
    return true;
  } else if(targetChannel == 1){
    channelBMagnitude = magnitude;
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
    return channelAMagnitude * DAC_BASEVOLTAGE;
  } else if(targetChannel == 1) {
    return channelBMagnitude * DAC_BASEVOLTAGE;
  }
  return 0;
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
    channelAWaveform = desiredWaveform;
    return true;
  } else if(targetChannel == 1) {
    channelBWaveform = desiredWaveform;
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
    return channelAWaveform;
  } else if(targetChannel == 1) {
    return channelBWaveform;
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
uint32_t Dac_getAOffsetMicros() {
  return aDuration;
}

/*
 * Description:
 *  Returns the time in microseconds since the last
 *  B waveform began.
 *
 * Returns:
 *  The time offset in microseconds.
 */
uint32_t Dac_getBOffsetMicros() {
  return bDuration;
}

/*
 * Description:
 *  Turns off the DAC output.
 */
void Dac_pause() {
  ChannelA.amplitude(0);
  ChannelB.amplitude(0);
}


/*
 * Description:
 *  Resets the A timer at the end of the last A period.
 */
void Dac_updateATimer() {
  #ifdef DAC_DEBUG
  digitalWrite(DAC_DEBUG_PIN_A, debugAToggleOnPeriod);
  debugAToggleOnPeriod = !debugAToggleOnPeriod;
  #endif
  // > Tried to call restart() on the channel here earlier but calling continuously
  //   causes issues, better to call once. No observed timing drift relative to waveform,
  //   so just get initial offset to be correct.
  aDuration = 0;
}

/*
 * Description:
 *  Resets the B timer at the end of the last B period.
 */
void Dac_updateBTimer() {
  #ifdef DAC_DEBUG
  digitalWrite(DAC_DEBUG_PIN_B, debugBToggleOnPeriod);
  debugBToggleOnPeriod = !debugBToggleOnPeriod;
  #endif
  bDuration = 0;
}

/*
 * Description:
 *  Re-enables the DAC output but also implements any changes
 *  made since the last call.
 */
void Dac_resume() { // TODO verify restart order
  cli();
  ChannelA.begin(channelAWaveform);
  ChannelB.begin(channelBWaveform);
  ChannelA.frequency(channelAFrequency);
  ChannelB.frequency(channelBFrequency);
  ChannelA.amplitude(channelAMagnitude);
  ChannelB.amplitude(channelBMagnitude);
  ChannelA.phase(180);
  ChannelB.phase(180);
  aDuration = 0;
  ChannelA.restart();
  delay(8); // TODO I was found empirically, needs to be redone in microseconds and with more samples, maybe better alternative to restart required
  AUpdater.begin(Dac_updateATimer, MICROSFROMFREQ(channelAFrequency));
  bDuration = 0;
  ChannelB.restart();
  delay(8);
  BUpdater.begin(Dac_updateBTimer, MICROSFROMFREQ(channelBFrequency));
  sei();
}
