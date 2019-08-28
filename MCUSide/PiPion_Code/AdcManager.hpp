/*
 * File: AdcManager.hpp
 * ------------------------------
 * Author: Erick Blankenberg
 * Date:   8/12/2018
 *
 * Description:
 *  These functions allows users to sample from an analog pin at
 *  a set rate and accumulate buffers that can then be read. Everything
 *  starts disabled and Adc_resume() must be called after the desired
 *  frequency is set.
 */

#ifndef ADCMANAGER_H
#define ADCMANAGER_H

#include "Constants.hpp"
#include "AdcBuffer.hpp"

//----------------------- Functions ----------------------

void           Adc_init();
sampleBuffer * Adc_getLatestBuffer();
bool           Adc_bufferReady();
void           Adc_setFrequency(float newFrequency);
float          Adc_getFrequency();
uint8_t        Adc_getAverages();
bool           Adc_setAverages(uint8_t newAverages);
void           Adc_pause();
void           Adc_resume();

#endif
