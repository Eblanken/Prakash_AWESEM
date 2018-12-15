/*
 * File: PiPion.ino
 * ------------------------------
 * Author: Erick Blankenberg
 * Date:   7/30/2018
 *
 * Description:
 *  This sketch uses a teensy 3.6 as both a sampling buffer
 *  and waveform generator for the AWESEM project. The main file
 *  maintains messanger commands and coordinates DAC and ADC work.
 *  The AdcManager class internally maintains sample buffers and allows
 *  for transfers. The DacManager class keeps track of the waveform outputs.
 *  I tried to use messageCMD but there seems to be no easy way to
 *  pass arrays/custom structs efficiently, which makes efficient transfer of sample buffers to the coumputer difficult.
 *  I ended up just implementing my own thing and it works well.
 *
 * Install List:
 *  - Teensyduino:    https://www.pjrc.com/teensy/teensyduino.html
 *
 * TODO:
 *  - When events halt, debugging lines should fall
 *  - Synchronization between timing and phase of driving waveform is an issue.
 *    > Originally setting phase had no effect, found out that this is because the "phase" is a phase offset rather than the actual current phase
 *      in the waveform. Original discussion here:
 *      -> https://forum.pjrc.com/threads/54370-Waveform-begin-no-longer-resets-the-wave?highlight=phase
 *      -> Solution was to modify the phase-accumulator instead of the phase (phase modification relative to current value)
 *         https://github.com/PaulStoffregen/Audio/pull/275/files.
 *    > Once we were adjusting the actual progress into the waveform, it became clear that there was a significant latency when adjusting values and
 *      that there was a non-trivial variance on the order of 20% of the waveform's total phase in some cases.
 *        -> The audio library takes advantage of DMA and other peripherals efficiently by passing around large buffers of audio samples
 *           rather than individual samples. This is the source of the latency/variance. I was able to mitigate this by setting the buffer
 *           size to 16 items.
 *        -> The best solution would be to reset all of the items in the audio chain whenever we begin our DAC output so that everything
 *           is in a known initial state. At that point we can adjust for the latency manually.
 *            -> The output dac has two buffers per channel, which explains the variance. The variance was the difference between the constant assumed final DMA read 
 *               position and the actual position depending on when exactly you stopped scanning. The solution was to add a function to clear the output dac buffers
 *               and to reset the DMA address.
 *            -> This should be done for all Audio entities.
*             -> Manual offsets need to be adjusted.
 */

//----------------------------- Command List -----------------------------

/*
 * Serial commands: (float is 4 bytes, uint8_t and char are 1 byte etc.)
 *       All commands are in the format {byte1, byte2, [bytes3...bytesn (datatype)], [bytesn+1...bytesm (datatype)]
 *
 * Note: You need to 'H' (halt) and 'B' (begin) to refresh settings. Set
 *       parameters will not take effect until the system has been refreshed.
 *
 * TODO now user asks for particular channel
 *
 *  {'p'}                                                                 - Ping command, responds with 'A'
 *
 *  {'f', [axis (uint8_t)]}                                               - Responds with the DAC frequency of the specified axis as a float in hertz. Format is {['A' if valid request, 'F' if invalid (only byte) (char)][frequency in hertz (float)]}
 *
 *  {'F', [axis (uint8_t)], [frequency (float)]}                          - Sets the frequency of the given DAC axis in hertz, 0 for A and 1 for B. Responds with 'A' if succesful, 'F' otherwise.
 *
 *  {'m', [axis (uint8_t)]}                                               - Responds with the magnitude of the specified axis. Format {['A' if valid request, 'F' if invalid (only byte) (char)][magnitude in volts (float)]}
 *
 *  {'M', [axis (uint8_t)], [magnitude (float)]}                          - Sets the frequency of the given axis, 0 for A and 1 for B. Responds with 'A' if succesful.
 *
 *  {'s'}                                                                 - Responds with the current sampling frequency in hertz. Format {[magnitude in volts (float)]}
 *
 *  {'S', [sFrequency (float)]}                                           - Sets the sampling frequency in hertz. Response is 'A' if succesful 'F' if invalid.
 *
 *  {'u'}                                                                 - Responds with the current number of samples averaged per adc datapoint. Format {[samples averages (uint8_t]}
 *
 *  {'U', [averages (uint8_t)]}                                           - Sets the number of samples averaged per adc datapoint. Response is 'A' if succesful, 'F' if invalid.
 *
 *  {'w', [axis (uint8_t)]}                                               - Reads the current waveform, return format is Format {['A' if valid request, 'F' if invalid (only byte) (char)][0 = Sine, 1 = Sawtooth, 3 = Triangle (uint8_t)]}
 *
 *  {'W', [axis (uint8_t)], [waveform (0 sine, 1 saw, 3 tria) (uint8_t)]} - Sets the waveform used in scanning, responds with 'A' if succesful
 *
 *  {'A'}                                                                 - Requests a buffer, prints in order: {['A' if valid request, 'F' if invalid (only byte) (char)], [scan number (uint8_t)],
 *                                                                          [duration of scan in microseconds (uint16_t)],
 *                                                                          [offset from last A start in microseconds (uint16_t)], [offset from last B start in microseconds (uint16_t)],
 *                                                                          [byte array of data of the length BUFFER_SIZE defined in AdcManager.h (uint8_t)]}
 *
 *  {'B'}                                                                 - Begins all sampling and waveform outputs simultaneously, response is 'A'.
 *
 *  {'H'}                                                                 - Halts all sampling and waveform outputs simultaneously, response is 'A'.
 */

//-------------------------- Included Libraries --------------------------

#include "Constants.hpp"
#include "DacManager.hpp"
#include "AdcManager.hpp"

//--------------------------- Global Variables ---------------------------

typedef union { // Makes printing and recieving floats easy
 float number;
 uint8_t bytes[4];
} FLOATUNION_t;

typedef union { // Makes printing and recieving uint32's easy
 uint32_t number;
 uint8_t bytes[4];
} UINT32UNION_t;

#ifdef SERIAL_DEBUG
volatile bool lastSentOn = false;
#endif


//------------------------------ Functions -------------------------------

/*
 * Description:
 *  Initializes LED's and other debugging resources.
 */
void debugInit() {
  pinMode(LED_MAIN, OUTPUT);
  /*
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  */
  digitalWriteFast(LED_MAIN, LOW);
  #ifdef SERIAL_DEBUG
  pinMode(SERIAL_DEBUG_PIN_BUFFERSENDOFF, OUTPUT);
  #endif
}

/*
 * Description:
 *  Turns on the LED
 */
void debugLEDError(String errorMessage) {
  digitalWrite(LED_MAIN, HIGH);
  while(1) {
    Serial.println(errorMessage);
    Serial.send_now();
    delay(1000);
  }
}

/*
 * Description:
 *  Tries to retrieve a single byte from the serial stream.
 *  Will eventually time out if this does not occur.
 */
uint8_t getSerialUInt8() {
  elapsedMillis timeOut = 0;
  while(Serial.available() < 1) {
    if(timeOut > SERIAL_TIMEOUT) {
      String error = "Byte Acquisition Error";
      debugLEDError(error);
    }
  }
  return (uint8_t) Serial.read();
}

/*
 * Description:
 *  Tries to retrieve a floating point number from the serial stream.
 *  Will eventually time out if this does not occur.
 */
float getSerialFloat() {
  elapsedMillis timeOut = 0;
  while(Serial.available() < 4) {
    if(timeOut > SERIAL_TIMEOUT) {
      String error = "Float Acquisition Error";
      debugLEDError(error);
    }
  }
  FLOATUNION_t newValue;
  newValue.bytes[0] = Serial.read();
  newValue.bytes[1] = Serial.read();
  newValue.bytes[2] = Serial.read();
  newValue.bytes[3] = Serial.read();
  return newValue.number;
}

/*
 * Description:
 *  Tries to retrieve a uint32_t from the serial stream.
 *  Will eventually time out.
 */
uint32_t getSerialUint32() {
  elapsedMillis timeOut = 0;
  while(Serial.available() < 4) {
    if(timeOut > SERIAL_TIMEOUT) {
      String error = "Integer Acquisition Error";
      debugLEDError(error);
    }
  }
  UINT32UNION_t newValue;
  newValue.bytes[0] = Serial.read();
  newValue.bytes[1] = Serial.read();
  newValue.bytes[2] = Serial.read();
  newValue.bytes[3] = Serial.read();
  return newValue.number;
}

/*
 * Description:
 *  Reads a command string to return the current DAC waveform frequency.
 *
 * Parameters:
 *  'parameterString' Format is "f".
 *
 * Response:
 *  Responds with the DAC frequencies in the format {(float) freqA, (float) freqB}
 *  as 4 byte floats in hertz.
 */
void parseGetDacFrequency() {
  uint8_t currentChannel = getSerialUInt8();
  if(currentChannel == 1 || currentChannel == 0) {
    Serial.write('A');
    FLOATUNION_t freq;
    freq.number = Dac_getFrequency(currentChannel);
    Serial.write(freq.bytes, 4);
  } else {
    Serial.write('F');
  }
  Serial.send_now();
}

/*
 * Description:
 *  Reads a command string to set the frequency of one of two
 *  axis.
 */
void parseSetDacFrequency() {
  uint8_t currentChannel = getSerialUInt8();
  float desiredFrequency = getSerialFloat();
  if(Dac_setFrequency(currentChannel, desiredFrequency)) {
    Serial.write('A');
  } else {
    Serial.write('F');
  }
  Serial.send_now();
}

/*
 * Description:
 *  Reads a command string to print out the magnitude of
 *  each of the two axis.
 */
void parseGetDacMagnitude() {
  uint8_t currentChannel = getSerialUInt8();
  if(currentChannel == 0 || currentChannel == 1) {
    Serial.write('A');
    FLOATUNION_t outMagnitude;
    outMagnitude.number = Dac_getMagnitude(currentChannel);
    Serial.write(outMagnitude.bytes, 4);
  } else {
    Serial.write('F');
  }
  Serial.send_now();
}

/*
 * Description:
 *  Reads a command string to set the magnitude of the output
 *  waveform.
 */
void parseSetDacMagnitude() {
  uint8_t currentChannel = getSerialUInt8();
  float desiredMagnitude = getSerialFloat();
  if(Dac_setMagnitude(currentChannel, desiredMagnitude)) {
    Serial.write('A');
  } else {
    Serial.write('F');
  }
  Serial.send_now();
}

/*
 * Description:
 *  Prints out the waveforms associated with the two axis.
 */
void parseGetDacWaveform() {
  uint8_t currentChannel = getSerialUInt8();
  if(currentChannel == 1 || currentChannel == 0) {
    Serial.write('A');
    uint8_t dacWaveform = Dac_getWaveform(currentChannel);
    Serial.write(dacWaveform);
  } else {
    Serial.write('F');
  }
  Serial.send_now();
}

/*
 * Description:
 *  Reads a command string to set the magnitude of the output
 *  waveform.
 */
void parseSetDacWaveform() {
  uint8_t currentChannel = getSerialUInt8();
  uint8_t desiredWaveform = getSerialUInt8();
  if(Dac_setWaveform(currentChannel, desiredWaveform)) {
    Serial.write('A');
  } else {
    Serial.write('F');
  }
  Serial.send_now();
}

 /*
  * Description:
  *   Reads a command string and responds with the
  *   sampling frequency of the device.
  *
  * Response:
  *   Responds with the DAC frequencies in the format
  *   freqA then freqB as floats in hertz as raw bytes.
  */
void parseGetSFrequency() {
  Serial.write('A');
  FLOATUNION_t freqFloat;
  freqFloat.number = Adc_getFrequency();
  Serial.write(freqFloat.bytes, 4);
  Serial.send_now();
}

/*
 * Description:
 *  Sets the sampling frequency of the device. Assumes that
 *  we will be recieving a float.
 */
void parseSetSFrequency() {
  float newFrequency = getSerialFloat();
  Adc_setFrequency(newFrequency);
  Serial.write('A');
  Serial.send_now();
}

/*
 * Description:
 *  Returns the number of samples averaged per ADC data point.
 */
void parseGetSAverages() {
  Serial.write('A');
  Serial.write(Adc_getAverages());
  Serial.send_now();
}

/*
 * Description:
 *  Sets the number of samples averaged per ADC datapoint.
 *  Assumed to be recieving a uint8_t. Value is 0, 4, 8, 16 or 32.
 */
void parseSetSAverages() {
  uint8_t newAveraging = getSerialUInt8();
  if(Adc_setAverages(newAveraging)) {
    Serial.write('A');
  } else {
    Serial.write('F');
  }
  Serial.send_now();
}

/*
 * Description:
 *   Reads a command string and prints out a buffer of data.
 */
void parseGetBuffer() {
  sampleBuffer * newData = Adc_getLatestBuffer();
  if(newData) {
    Serial.write('A');
    UINT32UNION_t currentCount;
    currentCount.number = newData->number;
    Serial.write(currentCount.bytes, 4);
    UINT32UNION_t aStartVal;
    UINT32UNION_t bStartVal;
    UINT32UNION_t durationVal;
    aStartVal.number = newData->aStart; //newData.aStart;
    bStartVal.number = newData->bStart; //newData.bStart;
    durationVal.number = newData->duration; //newData.duration;
    Serial.write(aStartVal.bytes, 4); // Start relative to last A start (microSeconds)
    Serial.write(bStartVal.bytes, 4); // Start relative to last B start (microSeconds)
    Serial.write(durationVal.bytes, 4); // Duration (microSeconds)
    Serial.write(newData->data, ADC_BUFFERSIZE); // May be inefficient, TODO is there a way to pass a buffer pointer?
    #ifdef SERIAL_DEBUG
    digitalWriteFast(SERIAL_DEBUG_PIN_BUFFERSENDOFF, lastSentOn);
    lastSentOn = !lastSentOn;
    #endif
  } else {
    Serial.write('F');
  }
  Serial.send_now();
}

/*
 * Description:
 *  Reads a command string and starts all scanning and
 *  the DAC output.
 */
void parseStartEvents() {
  Dac_resume();
  Adc_resume();
  Serial.write('A');
  Serial.send_now();
}

/*
 * Description:
 *  Reads a command string and stops all scanning and
 *  the DAC output. Note that this also resets the ADC
 *  buffer and starts off with a fresh start.
 */
void parseStopEvents() {
  Adc_pause();
  Dac_pause();
  Serial.write('A');
  Serial.send_now();
}

//----------------------------- The Program ------------------------------

void setup() {
  Serial.begin(115200); // Used for native usb
  elapsedMillis flushCounter;
  while(flushCounter < SERIAL_FLUSH) {
    if(Serial.available()) {
      Serial.read();
    }
  }
  debugInit();
  Adc_init();
  Dac_init();
}

/*
 * Main loop just recieves serial commands
 */
void loop() {
  if(Serial.available()) {
    uint8_t switchValue = Serial.read();
    switch(switchValue) {
      case 'p': // Ping
        Serial.write('A');
        break;
      case 'f': // Reads dac frequency
        parseGetDacFrequency();
        break;
      case 'F': // Sets dac frequency
        parseSetDacFrequency();
        break;
      case 'm': // Reads magnitude
        parseGetDacMagnitude();
        break;
      case 'M': // Sets magnitude
        parseSetDacMagnitude();
        break;
      case 'w': // Reads waveform
        parseGetDacWaveform();
        break;
      case 'W': // Sets waveform
        parseSetDacWaveform();
        break;
      case 's': // Reads sampling frequency in hertz
        parseGetSFrequency();
        break;
      case 'S': // Sets sampling frequency in hertz
        parseSetSFrequency();
        break;
      case 'u': // Gets number of averages per adc result
        parseGetSAverages();
        break;
      case 'U': // Sets number of averages per adc result
        parseSetSAverages();
        break;
      case 'A': // Acquires current buffer
        parseGetBuffer();
        break;
      case 'B': // Begins all actions
        parseStartEvents();
        break;
      case 'H': // Halts all actions
        parseStopEvents();
        break;
      default:
        String error = "Command Value Error: ";
        error += switchValue;
        debugLEDError(error);
        break;
    }
  }
}
