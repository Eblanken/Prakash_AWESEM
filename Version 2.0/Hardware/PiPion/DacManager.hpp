/*
 * File: DacManager.hpp
 * ------------------------------
 * Author: Erick Blankenberg
 * Date:   8/12/2018
 *
 * Description:
 *  These are functions to interact with the DACs on the Teensy. By default
 *  the Dacs are disabled and must be enabled with "Dac_resume()" after the
 *  magnitudes and frequencies are set.
 */

#ifndef DACMANAGER_H
#define DACMANAGER_H

#include "Arduino.h"
#include "Audio.h"
#include "IntervalTimer.h"

#define DAC_REFERENCE EXTERNAL // Options: EXTERNAL (0 - 3.3) and INTERNAL (0 - 1.2)
#define DAC_APRIORITY 122 // Priority for timer reset functions
#define DAC_BPRIORITY 123 // for both axis for timing tracking.

#define DAC_DEBUG // Uncomment to enable LED alternation whenever 
#define DAC_DEBUG_PIN_A 31 // TODO not used
#define DAC_DEBUG_PIN_B 32

//----------------------- Functions ----------------------

void     Dac_init();
bool     Dac_setFrequency(uint8_t targetChannel, float newFrequency);
float    Dac_getFrequency(uint8_t targetChannel);
bool     Dac_setMagnitude(uint8_t targetChannel, float magnitude);
float    Dac_getMagnitude(uint8_t targetChannel);
bool     Dac_setWaveform(uint8_t targetChannel, uint8_t desiredWaveform);
uint8_t  Dac_getWaveform(uint8_t targetChannel);
uint32_t Dac_getAOffsetMicros();
uint32_t Dac_getBOffsetMicros();
void     Dac_pause();
void     Dac_resume();

#endif

