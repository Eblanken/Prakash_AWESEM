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

#include "AdcManager.hpp"

//----------------------- Functions ----------------------

sampleBuffer *          AdcBuffer_getHead();
sampleBuffer *          AdcBuffer_getTail();
void                    AdcBuffer_resetBuffer();

#endif
