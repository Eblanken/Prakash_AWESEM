/*
 * File: AdcManager.hpp
 * ------------------------------
 * Author: Erick Blankenberg
 * Date:   8/12/2018
 *
 * Description:
 *  TCircular buffer for high speed in place buffer for writing.
 */

#ifndef ADCBUFFER_H
#define ADCBUFFER_H

#include "Constants.hpp"
#include "Arduino.h"

//------------------------ Structs ----------------------

typedef struct {
  uint32_t number;
  uint32_t aStart;
  uint32_t bStart;
  uint32_t duration;
  uint8_t  data[ADC_BUFFERSIZE];
} sampleBuffer;

//----------------------- Functions ----------------------

sampleBuffer *          AdcBuffer_getHead();
sampleBuffer *          AdcBuffer_getTail();
void                    AdcBuffer_resetBuffer();

#endif
