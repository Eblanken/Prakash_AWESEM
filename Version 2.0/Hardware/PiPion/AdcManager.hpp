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

#include "Arduino.h"
#include "ADC.h"
#include "DacManager.hpp"
#include "IntervalTimer.h"

#define ADC_PIN A8
#define ADC_SAMPLEPRIORITY 126
#define ADC_AVERAGES 4 // Default value, can change in commands, has to be a multiple of 4 and less than 32
#define ADC_SAMPLEFREQUENCY 40000 // Default value, can change with commands, max seems to be about 60,000 as a function of averages and integration time
#define ADC_SAMPLESIZE 1024

#define ADC_BUFFERSIZE 10   

#define ADC_DEBUG // Uncomment to enable LED alternation every time buffer is ready
#define ADC_DEBUG_PIN_SAMPLE        10
#define ADC_DEBUG_PIN_BUFFERXCHANGE 11

typedef struct {
  uint32_t number;
  uint32_t aStart;
  uint32_t bStart;
  uint32_t duration;
  uint8_t  data[ADC_SAMPLESIZE];
} sampleBuffer;

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
