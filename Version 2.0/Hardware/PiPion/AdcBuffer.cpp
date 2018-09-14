/*
 * File: AdcBuffer.cpp
 * ------------------------------
 * Author: Erick Blankenberg
 * Date:   8/12/2018
 *
 * Description:
 *  This is a simple circularBuffer, there are ton of good circularbuffer libraries avialable online
 *  but mine is written to prioritize writing in place. There may be another library online but oh well.
 *  Also this buffer style is fairly unsafe.
 *  
 *  The intent is to write data to the head and then advance forward, while reading data from the tail and
 *  retreating forward.
 *  
 *  Note: Data is never explicitly cleared during any operation, it is assumed that data is overwritten by whatever
 *    entity is calling for pointers to the head of the buffer.
 *    
 *  Warning: As of right now there is no security for overwriting data while the main thread attempts to read it, maybe
 *    this can be addressed with a lock system but also a real buffer may be better if we can get away with it. 
 */

#include "AdcManager.hpp"
#include "AdcBuffer.hpp"

//----------------------- Private Variables ---------------------

volatile uint32_t headIndex                      = 0;
volatile uint32_t tailIndex                      = 0;
sampleBuffer      circularBuffer[ADC_BUFFERSIZE] = { };
int32_t           numSamples                     = -1; // Needs to have at least two requested, one filled one in progress
 
//----------------------- Public Functions ----------------------

/*
 * Description:
 *  Moves the head pointer up by one.
 * 
 * Returns:
 *  Returns false if data was overwritten by this action, true otherwise.
 */
bool headAdvance() {
  headIndex++; 
  if(headIndex >= ADC_BUFFERSIZE) { // Wraps back
    headIndex = 0;
  }
  numSamples++;
  if(numSamples >= ADC_BUFFERSIZE) {
    tailRetreat(); // Head index overwrote oldest data
    return false;
  }
  return true;
}

/*
 * Description:
 *  Moves the tail pointer up by one.
 * 
 * Returns:
 *  Returns false if there is no data left, true otherwise.
 */
bool tailRetreat() {
  if(numSamples > 0) {
    numSamples--;  
    tailIndex++;
    if(tailIndex >= ADC_BUFFERSIZE) {
      tailIndex = 0;
    } 
  } else {
    return false;
  }
  return true;
}

/*
 * Description:
 *  Returns a pointer to the current adc sample
 *  associated with the head. The head is intended
 *  to be written to, not read. The head advances after
 *  this read.
 * 
 * Returns:
 *  A pointer to a sampleBuffer struct at the head
 *  of the buffer.
 */
sampleBuffer * AdcBuffer_getHead() {
  sampleBuffer * retVal = &circularBuffer[headIndex];
  headAdvance();
  return retVal;
}

/*
 * Description:
 *  Returns a pointer to the current adc sample
 *  associated with the tail. The tail advances
 *  after this read.
 * 
 * Returns:
 *  A pointer to a sampleBuffer struct at the tail
 *  of the buffer. Returns NULL if there is no data
 *  left.
 */
sampleBuffer * AdcBuffer_getTail() {
  sampleBuffer * retVal = & circularBuffer[tailIndex];
  if(tailRetreat()) {
    return retVal; 
  }
  return NULL;
}

/*
 * Description:
 *  Sets the head and tail to the same index, sets the length to zero.
 */
void AdcBuffer_resetBuffer() {
  headIndex    = 0;
  tailIndex    = 0;
  numSamples  = -1;
}
