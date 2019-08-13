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

//----------------------- Functions ----------------------

void     Dac_init();
bool     Dac_setFrequency(uint8_t targetChannel, float newFrequency);
float    Dac_getFrequency(uint8_t targetChannel);
bool     Dac_setMagnitude(uint8_t targetChannel, float magnitude);
float    Dac_getMagnitude(uint8_t targetChannel);
bool     Dac_setArbWData(uint8_t channel, int16_t dataVals[256]); // Note that 
bool     Dac_setWaveform(uint8_t targetChannel, uint8_t desiredWaveform);
uint8_t  Dac_getWaveform(uint8_t targetChannel);
uint32_t Dac_getAOffsetMicros();
uint32_t Dac_getBOffsetMicros();
void     Dac_pause();
void     Dac_resume();

#endif
