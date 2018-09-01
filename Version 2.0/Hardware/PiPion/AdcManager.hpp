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
#include "CircularBuffer.h"
#include "DacManager.hpp"
#include "IntervalTimer.h"

#define ADC_PIN A8
#define ADC_SAMPLESIZE 1024
#define ADC_BUFFERSIZE 10
#define ADC_SAMPLEPRIORITY 126
#define ADC_AVERAGES 8

//#define ADC_DEBUG // Uncomment to enable LED alternation every time buffer is ready
#define ADC_DEBUG_PIN 13

typedef struct {
  uint16_t aStart;
  uint16_t bStart;
  uint16_t duration;
  uint16_t currentSize;
  uint8_t data[ADC_SAMPLESIZE];
} sampleBuffer;

//----------------------- Functions ----------------------

void           Adc_init();
sampleBuffer   Adc_getLatestBuffer();
bool           Adc_bufferReady();
void           Adc_setFrequency(float newFrequency);
float          Adc_getFrequency();
void           Adc_pause();
void           Adc_resume();

#endif
