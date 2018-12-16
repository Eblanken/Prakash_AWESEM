/*
 * File: Constants.hpp
 * ------------------------------
 * Author: Erick Blankenberg
 * Date:   8/12/2018
 *
 * Description:
 *  Controls functionality of the microcontroller.
 */

#ifndef CONSTANTS_H
#define CONSTANTS_H

// ---------------------------------- Macros -----------------------------------

#define MICROSFROMFREQ(frequency) ((float) 1000000.0 / (float) frequency)

// ------------------------- Constants for ADC Manager -------------------------

// Defaults that can be changed by serial commands
#define ADC_DEFAULT_AVERAGES 4            // > Can be 0, 4, 8, 16, or 32
#define ADC_DEFAULT_SAMPLEFREQUENCY 40000 // > Sampling frequency in hertz

// Standard
#define ADC_PIN A8
#define ADC_SAMPLEPRIORITY  126
#define ADC_BUFFERSIZE      1024 // > Number of elements in sample buffer
#define ADC_BUFFERQUEUESIZE 10   // > Number of buffers stored

// Debugging
#define ADC_DEBUG // > Uncomment to enable alternation every time buffer is ready
#define ADC_DEBUG_PIN_SAMPLE        10 // > Alternates on every sample
#define ADC_DEBUG_PIN_BUFFERXCHANGE 11 // > Alternates whenever current buffer is complete

// ------------------------ Constants for DAC Manager --------------------------

// Defaults tha can be changed by serial commands
#define DAC_DEFAULT_FREQUENCY_A 35.0 // > Frequency in hertz
#define DAC_DEFAULT_FREQUENCY_B 0.05 // > Frequency in hertz
#define DAC_DEFAULT_WAVEFORM_A 0     // > Waveform types are 0 = Sine, 1 = Sawtooth, 3 = Triangle
#define DAC_DEFAULT_WAVEFORM_B 0     // > Waveform types are 0 = Sine, 1 = Sawtooth, 3 = Triangle
#define DAC_DEFAULT_MAGNITUDE_A 3.3  // > Magnitude relative to reference, [0 - 1] * vRef
#define DAC_DEFAULT_MAGNITUDE_B 3.3  // > Magnitude relative to reference, [0 - 1] * vRef
// Standard
#define DAC_REFERENCE EXTERNAL // > Options: EXTERNAL (0 - 3.3) and INTERNAL (0 - 1.2)
#define DAC_APRIORITY 1        // > Priority for timer reset functions
#define DAC_BPRIORITY 2        //   for both axis for timing tracking.

// Debugging
#define DAC_DEBUG              // > Uncomment to enable alternation whenever the waveform timing offsets are reset
#define DAC_DEBUG_PIN_A 31     // > Provides square wave that alternates whenever offset reset is called for the A channel
#define DAC_DEBUG_PIN_B 32     // > Provides square wave that alternates whenever offset reset is called for the B channel
#define DAC_DEBUG_PIN_R 30     // > Provides high notch while resetting is taking place. Rises on start falls on completion.

// ----------------------- Constans for Main Function --------------------------

// Misc debugging pins (includes built in LED)
/*
#define LED_RED      1
#define LED_YELLOW   2
#define LED_BLUE     3
#define LED_GREEN    4
*/
#define LED_MAIN     13

#define SERIAL_TIMEOUT 1000 // > Timeout for serial in milliseconds
#define SERIAL_FLUSH   100  // > Timeout to discard data originally

// Debugging
#define SERIAL_DEBUG // > Uncomment to enabe serial debugging
#define SERIAL_DEBUG_PIN_BUFFERSENDOFF 12 // > Alternates when a buffer is sent

#endif
