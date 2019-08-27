// TODO Major issues with arbitrary waveform definitely related to TFT display data transfer
// Crashes for sure when trying to stop the width increment

// This program displays data from the analog input on the monitor
// assuming that the input originates from a solenoid driven stage
// controlled by DAC1 and DAC2 (see variables)

// In the current setup, the ADC samples freely and places the results
// into the appropriate "bucket" in the sample buffer. Timers manage the
// bucket placement.

// Major TODOS: Organize Code into .h and .cpp files, redo symmetry buffers. Use finite state machines

// TODO: Volatile? Consolidate timers and counters for width and height. Better Tables. Symmetry Detection
// use structs instead of piles of pointers etc. Debug mode? Saving images and settings to sd card
// using actual buffer width in sendline instead of pixel_width? Organize debugging events. Build a GUI
// debug monitor text, Use real analysis buffer instead of PIXEL_WIDTH

// Debug control panel:

const int COM_DELAY = 5; // Delay in ms after each serial message is sent
const int COM_BAUD = 9600; // Baud rate
const int WAVEOUT_MODE_DETECTOR = A5;

#define WAVEOUT // Comment out to disable the audio output for stage controls
#define SAMPLE_READ // Comment out to disable sampling of the ADC
#define MONITOR_BUFFER // Comment out to disable interrupts for moving the current pixel
#define MONITOR // Comment out to disable the monitor
//#define MONITOR_CONSOLE // Console and keyboard
//#define ENABLE_MODETYPES // Comment out to save all data, otherwise check SAMPLE_MODE
#define SERIAL_MESSAGES
//#define SLAVE_OUT // Enables master-slave communications with ANOTHER 3.3 V device (watch logic voltages)

// It is usually best practice to only have a few debug options in use at one time, they also usually have caveats
// that include breaking the program or strongly altering the behavior of the scanner.
//#define DEBUG_VERBOSE_STARTUP // Supposed to let you know how startup goes, currently broken unless COM_DELAY is 1.
//#define DEBUG_WAVEFORM // Prints out the waveform during initial startup
//#define DEBUG_SINEWAVEFORM // Prints out the results of calling buildSineWaveform 
//#define DEBUG_INTERRUPT_WIDTH_INCREMENT // Prints out information every time width is incremented
//#define DEBUG_INTERRUPT_WIDTH_PERIOD_TIME // Prints out length of full period of with in micros // TODO impliment
//#define DEBUG_INTERRUPT_HEIGHT_INCREMENT // Prints out information every time height is incremented
//#define DEBUG_INTERRUPT_HEIGHT_INCREMENT_TIME // Prints out how long the heightIncrement interrupt takes to execute
//#define DEBUG_INTERRUPT_HEIGHT_PERIOD_TIME // Prints out length of full period of height in micros // TODO impliment
//#define DEBUG_ADC // Prints out first ADC read, will stop program
//#define DEBUG_MONITOR_COM_QUICK // Prints out "Line" whenever the monitor sends a line
//#define DEBUG_MONITOR_COM_TRANSTIME // Prints out the monitor's total communication time every line
//#define DEBUG_PIXELBUFFER // Note this will mess a lot of stuff up, just use to verify values
//#define DEBUG_TIME_MAIN // This prints how long each cycle of main takes, it currently takes about 960 microseconds to send a line

#define PIN_LED_BLUE 35
#define PIN_LED_GREEN 36
#define PIN_LED_YELLOW 37
#define PIN_LED_RED 38

// Included Libraries:

#include <Wire.h>
#include <SPI.h>
#include <ILI9341_t3.h>
#include <ADC.h>
#include <Audio.h>

// Function prototypes: // TODO Create all prototypes and default parameters

void startEvents();
void stopEvents();
void printConsoleMessage(String message, uint16_t color = ILI9341_WHITE);

// Stage Controls:

const double FAST_FREQUENCY = 50; // Frequency in hertz (best 1000)
const double SLOW_FREQUENCY = 0.05; // ILI935 (0.35 max) // 0.05 // Frequency in hertz ((no color : best 0.33 w/o WAVEOUT, 0.185 w/ WAVEOUT) (color : 0.1 max w/ WAVEOUT)) 

#ifdef WAVEOUT
const double FAST_AMPLITUDE = 0.3; // Magnitude of fast driver in volts
const double SLOW_AMPLITUDE = 0.3; // Magnitude of slow driver in volts
const double FAST_OFFSET = 0.5; // Midpoint of sine wave (total cannot go above 3.3 or under 0)
const double SLOW_OFFSET = 0.5;

AudioSynthWaveform       fastSine;
AudioSynthWaveform       slowSine;
AudioOutputAnalogStereo  dacs;
AudioConnection          patchCord1(fastSine, 0, dacs, 1);
AudioConnection          patchCord2(slowSine, 0, dacs, 0);

// The audio library can accept an arbitrary waveform in the form of a 256 sample array
const int AUDIO_FILE_SIZE = 257; // TODO this should be 257, currently includes buffer on beginning and end b/c tft.writeRect etc. interferes with reading somehow, re-check code in the library for WAVEFORM_SINE and WAVEFORM_ARBITRARY under synth_waveform.cpp 
int16_t slowSineWaveform[AUDIO_FILE_SIZE] = { };
int16_t fastSineWaveform[AUDIO_FILE_SIZE] = { };

#endif

// Monitor Variables:

#ifdef MONITOR_BUFFER
const int MONITOR_IMAGE_WIDTH = 240; // Width of image along X axis
const int MONITOR_IMAGE_HEIGHT = 240; // Height of image along Y axis

const int MONITOR_MAX_WIDTH  = 240;// Maximum width of monitor
const int MONITOR_MAX_HEIGHT = 320; // Maximum height of monitor

const int MONITOR_IMAGE_WIDTH_OFFSET = 0;
const int MONITOR_IMAGE_HEIGHT_OFFSET = 0;
 
// Buffers used for scan lines, these are sent to the monitor
// after one full period. What they contain depends on the mode.
const int WIDTH_BUFFER_RESOLUTION = MONITOR_IMAGE_WIDTH;
const int HEIGHT_BUFFER_RESOLUTION = MONITOR_IMAGE_HEIGHT; // Not actually used for transfer

volatile uint32_t widthBufferOne[WIDTH_BUFFER_RESOLUTION] = { };
volatile uint8_t widthBufferCounterOne[WIDTH_BUFFER_RESOLUTION] = { };

volatile uint32_t widthBufferTwo[WIDTH_BUFFER_RESOLUTION] = { };
volatile uint8_t widthBufferCounterTwo[WIDTH_BUFFER_RESOLUTION] = { };

volatile uint32_t* widthBufferPointer = widthBufferOne;
volatile uint8_t* widthBufferCounterPointer = widthBufferCounterOne;
volatile uint32_t* widthBufferReadPointer = NULL;
volatile uint8_t* widthBufferReadCounterPointer = NULL;

// Positioning constants
const int FAST_RESOLUTION = MONITOR_IMAGE_WIDTH * 4; // Resolutions of position functions
const int SLOW_RESOLUTION = MONITOR_IMAGE_HEIGHT * 4;
const int FAST_MIDPOINT = FAST_RESOLUTION / 2;// Midpoint of width function, positions after midpoint assumed to be solenoid returning // TODO better solution
const int SLOW_MIDPOINT = SLOW_RESOLUTION / 2;// returning values are stored in the second half of the buffer // TODO better solution

volatile int widthCounter = 0; // The width counter tracks the current position to fill samples in the width buffer
volatile uint16_t widthTime = 0; // Incremented by one during every widthIncrementor call
volatile uint16_t widthTimeOffset = 0; // Added to widthTime, used for calibration
uint16_t widthWaveGuide[FAST_RESOLUTION] = { }; // Every time the incrementor is called, the widthCounter is set to widthWaveForm[widthTime]
IntervalTimer widthIncrementor;
double fastUpdateTime;

volatile int heightCounter = 0; // heightCounter tracks the Y position of the buffer to be sent
volatile uint16_t heightTime = 0; // Incremented by one during every widthIncrementor call
volatile uint16_t heightTimeOffset = 0; // Added to heightTime, used for calibration
uint16_t heightWaveGuide[SLOW_RESOLUTION] = { }; // Every time the incrementor is called, the widthCounter is set to widthWaveForm[widthTime]
IntervalTimer heightIncrementor;
double slowUpdateTime;

#define GUIDESTYLE 0 // Can be linear (0) or sine (1)

#endif

#ifdef MONITOR
//#define MONITOR_MESSAGES

#define TFT_CS 10
#define TFT_DC 9

ILI9341_t3 tft = ILI9341_t3(TFT_CS, TFT_DC);
#endif

// Sampling Variables:

#ifdef SAMPLE_READ

const int SAMPLE_PIN = A8;
const int SAMPLE_BITS = 8;
const int ANALOG_MAX = pow(2, SAMPLE_BITS);
bool readReady = true;

ADC *adc = new ADC();

#else
#ifdef MONITOR
const int ANALOG_MAX = (MONITOR_IMAGE_WIDTH + MONITOR_IMAGE_HEIGHT);
#endif
#endif

// Values for debugging:

long timer;
long currentTime;

// Enumeration for reader mode:

enum ReaderMode { saveRight, saveLeft, saveAll, spliceAll }; // TODO spliceAll
const ReaderMode READ_MODE = saveRight;

bool monitorActive = true; // Descibes current activity of the program
bool request = true; // Other parts of the program can set this to the desired current state

// The program:

void setup() {
  // Starts LEDs
  #ifdef PIN_LED_RED
  pinMode(PIN_LED_RED, OUTPUT);
  analogWrite(PIN_LED_RED, 255);
  #endif
  #ifdef PIN_LED_GREEN
  pinMode(PIN_LED_GREEN, OUTPUT);
  analogWrite(PIN_LED_GREEN, 255);
  #endif
  #ifdef PIN_LED_BLUE
  pinMode(PIN_LED_BLUE, OUTPUT);
  analogWrite(PIN_LED_BLUE, 255);
  #endif
  #ifdef PIN_LED_YELLOW
  pinMode(PIN_LED_YELLOW, OUTPUT);
  analogWrite(PIN_LED_YELLOW, 255);
  #endif
  
  delay(2500);
  
  #ifdef PIN_LED_BLUE
  analogWrite(PIN_LED_BLUE, 0);
  #endif
  #ifdef PIN_LED_GREEN
  analogWrite(PIN_LED_GREEN, 0);
  #endif
  #ifdef PIN_LED_YELLOW
  analogWrite(PIN_LED_YELLOW, 0);
  #endif

  // Initializes the monitor
  #ifdef MONITOR
  tft.begin();
  #ifdef MONITOR_CONSOLE
  setupGUI();
  #endif
  #endif
  
  // Initializes serial
  Serial.begin(COM_BAUD);
  /*
  while(!Serial) {
    #ifdef PIN_LED_RED
    digitalWrite(PIN_LED_RED, HIGH);
    delay(20);
    digitalWrite(PIN_LED_RED, LOW);
    delay(20);
    #endif
  }
  */
  #ifdef PIN_LED_RED
  pinMode(PIN_LED_RED, OUTPUT);
  digitalWrite(PIN_LED_RED, HIGH);
  #endif
  
  // Program starts
  //printConsoleMessage("Beginning Program.");
  
  // Initializes the buffers
  #ifdef MONITOR_BUFFER
  buildTables();
  //printConsoleMessage("Infrastructure Initialized");
  #endif

  // Initializes the ADC
  #ifdef SAMPLE_READ
  pinMode(SAMPLE_PIN, INPUT);
  adc->setAveraging(1); // set number of averages
  adc->setResolution(SAMPLE_BITS); // set bits of resolution
  adc->setConversionSpeed(ADC_CONVERSION_SPEED::VERY_HIGH_SPEED);
  adc->setSamplingSpeed(ADC_SAMPLING_SPEED::VERY_HIGH_SPEED);
  //printConsoleMessage("ADC Initialized");
  #endif

  // Initializes the interrupts
  #ifdef MONITOR_BUFFER
  fastUpdateTime = frequencyToMicros(FAST_FREQUENCY * FAST_RESOLUTION); 
  slowUpdateTime = frequencyToMicros(SLOW_FREQUENCY * SLOW_RESOLUTION);
  String fastAxis = (String) "Fast axis update every (uS): " + fastUpdateTime;
  //printConsoleMessage(fastAxis);
  String slowAxis = (String) "Slow axis update every (uS): " + slowUpdateTime;
  //printConsoleMessage(slowAxis);
  widthIncrementor.priority(120);
  heightIncrementor.priority(125);
  //printConsoleMessage("Interrupts Initialized");
  #endif

  // Initializes the waveforms
  #ifdef WAVEOUT
  AudioMemory(15); // This is how many audio samples to store, use the function AudioMemoryUsageMax() to get the most used to set this value. My last test showed that it used 2 (one for each dac).
  dacs.analogReference(EXTERNAL);
  fastSine.begin(WAVEFORM_SINE);
  slowSine.begin(WAVEFORM_SINE);
  fastSine.amplitude(0);
  slowSine.amplitude(0);
  fastSine.frequency(FAST_FREQUENCY);
  slowSine.frequency(SLOW_FREQUENCY);
  //printConsoleMessage("Waveforms Initialized");
  #endif

  startEvents();
  //printConsoleMessage("All Events Started");
  
  //printConsoleMessage("Program startup complete!");
  monitorActive = true;
  #ifdef PIN_LED_RED
  analogWrite(PIN_LED_RED, 0);
  #endif
}

/*
 *  Main loop basically just polls for lines (TODO make this more elegant) for its day
 *  job and can be used for other stuff but priority scheduling is a major TODO and this needs
 *  to be redone anyway
 */
void loop() {
  #ifdef DEBUG_TIME_MAIN
  timer = micros();
  #endif

  sendLine();
  
  #ifdef DEBUG_TIME_MAIN
  currentTime = micros();
  printConsoleMessage((String) "Monitor Line Delay: " + (currentTime - timer));
  #endif
}

/*
 * This function enables all sampling, timers, etc. at roughly the same time
 */
void startEvents() {
  #ifdef MONITOR_BUFFER
  if(!widthIncrementor.begin(widthIncrement, fastUpdateTime)) {
    printConsoleError(F("Error: Unable to initialize width incrementor!"));
  }
  if(!heightIncrementor.begin(heightIncrement, slowUpdateTime)){
    printConsoleError(F("Error: Unable to initialize width incrementor!"));
  }
  #ifdef DEBUG_VERBOSE_STARTUP
  //printConsoleMessage(F("-> Buffer incrementors initialized."));
  #endif
  #endif
  
  //#ifdef SAMPLE_READ
  adc->enableInterrupts(ADC_0);
  adc->startContinuous(SAMPLE_PIN, ADC_0);
  //#ifdef DEBUG_VERBOSE_STARTUP
  //printConsoleMessage(F("-> Sampling interrupts begun."));
  //#endif
  //#endif
  
  #ifdef WAVEOUT
  fastSine.phase(90);
  slowSine.phase(90);
  fastSine.amplitude((FAST_AMPLITUDE * 2) / 3.3);
  slowSine.amplitude((SLOW_AMPLITUDE * 2) / 3.3);
  #ifdef DEBUG_VERBOSE_STARTUP
  //printConsoleMessage(F("-> Wave outputs begun."));
  #endif
  #endif
}

 /*
  * This function disables all sampling, timers, etc. at roughly the same time
  * 
  * TODO major crashes while attempting to disable height interrupts
  * TODO find every instance of monitorActive, these are related to the temp fix
  */
void haltEvents() {
  #ifdef WAVEOUT
  fastSine.amplitude(0);
  slowSine.amplitude(0);
  #endif
  
  #ifdef SAMPLE_READ
  adc->disableInterrupts();
  adc->stopContinuous();
  #endif

  #ifdef MONITOR_BUFFER
  widthIncrementor.end();
  heightIncrementor.end(); // Crashes here :(
  #endif

  #ifdef MONITOR
  tft.fillRect(0,0, MONITOR_MAX_WIDTH, MONITOR_MAX_HEIGHT, ILI9341_BLACK);
  #endif
}

/*
 * This function sends the current buffer designated
 * for reading to the monitor, if there is a monitor
 * ready to be read.
 */
inline void sendLine() {
  #ifdef MONITOR_BUFFER
  // Only sends a line if there is a buffer ready
  if((widthBufferReadPointer != NULL) && (widthBufferReadCounterPointer != NULL)) {
    uint16_t imageBuffer[MONITOR_IMAGE_WIDTH] = { };
    #ifdef DEBUG_MONITOR_COM_TRANSTIME
       uint16_t startTime = micros(); 
    #endif
    
    for(int index = 0; index < WIDTH_BUFFER_RESOLUTION; index++) {
      int currentIndex = index * (MONITOR_IMAGE_WIDTH / ((double) WIDTH_BUFFER_RESOLUTION)); // TODO more elegant collapsing of larger / smaller buffers then PIXELS_WIDTH: Averaging? Blurring to fill in holes?
      imageBuffer[currentIndex] = widthBufferReadPointer[index] / widthBufferReadCounterPointer[index];
      #ifdef MONITOR
      imageBuffer[currentIndex] = pixelColor565(imageBuffer[currentIndex]);
      #endif
    }
    
    #ifdef DEBUG_PIXELBUFFER
    haltEvents();
    for(int index = 0; index < MONITOR_IMAGE_WIDTH; index++) {
      String data = "Pixel Buffer: " + index + " : " + imageBuffer[index] + " [ " + *(widthBufferReadCounterPointer + index) + " : " + *(widthBufferReadPointer + index) + " ]";
      printConsoleMessage(data);
    }
    startEvents();
    #endif

    // Resets buffers
    for(int index = 0; index < WIDTH_BUFFER_RESOLUTION; index++) {
        *(widthBufferReadCounterPointer + index) = 0;
        *(widthBufferReadPointer + index) = 0;
    }

    #ifdef DEBUG_MONITOR_COM_QUICK
    printConsoleMessage("Line Sent");
    #endif
    
    #ifdef MONITOR
    if(monitorActive) {
      tft.writeRect((int16_t) MONITOR_IMAGE_WIDTH_OFFSET, (int16_t) (MONITOR_IMAGE_HEIGHT_OFFSET + heightCounter), (int16_t) MONITOR_IMAGE_WIDTH, 1, &imageBuffer[0]);
    }
    #endif
    
    widthBufferReadPointer = NULL;
    widthBufferReadCounterPointer = NULL;

    #ifdef DEBUG_MONITOR_COM_TRANSTIME
       uint16_t endTime = micros(); 
       Serial.print("Line Time (uS): ");
       Serial.println(endTime - startTime);
    #endif
  }
  #endif
}

/*
 * This function defines a sine waveform in the format required for
 * the audio library with the given input amplitude and offset.
 * 
 * The sineAmplitude, and sineOffset parameters are not in any
 * particular units. The sinePhase parameter is in degrees. The sineFrequency
 * is in waves / vector length. The inputArray and array length parameters pertain
 * to the array.
 * 
 * The function returns the completed array by reference to arrayPointer
 */
void buildSineWaveform(float sineAmplitude, float sineOffset, float sinePhaseOffset, float sineFrequency, int16_t inputArray[], int arraySize) {
  #ifdef DEBUG_SINEWAVEFORM
  printConsoleMessage("Sinewave: [index] : [value] (debugging)");
  #endif
  for(int index = 0;index < arraySize;index++) {
    inputArray[index] = sineAmplitude * sin((((float) index / arraySize) * (2.0 * PI) * sineFrequency) + ((sinePhaseOffset / 360) * (2 * PI))) + sineOffset;
    #ifdef DEBUG_SINEWAVEFORM
    Serial.println((String) "Sinewave: " + index + (String) " : " + inputArray[index]);
    #endif
  }
}

/*
 * Converts frequency in HZ to delay in microseconds
 */
float frequencyToMicros(float desiredFrequency) {
  return(1000000 / desiredFrequency);
}

// TODO actually make better tables
#ifdef MONITOR_BUFFER 
void buildTables() { 

  #if (GUIDESTYLE == 0)
  // Constructs width table
  for(int index = 0; index < FAST_RESOLUTION; index++) {
    int value = 0;
    if(index < FAST_MIDPOINT) {
      value = index * ((double) WIDTH_BUFFER_RESOLUTION / FAST_MIDPOINT);
    } else {
      value = (FAST_RESOLUTION - index) * ((double) WIDTH_BUFFER_RESOLUTION / FAST_MIDPOINT);
    }
    widthWaveGuide[index] = value;
    
    
    #ifdef DEBUG_WAVEFORM
    String data = (String) "Width: " + (String) index + (String) " : " + (String) value;
    printConsoleMessage(data);
    #endif
    
  }
  // Constructs height table
  for(int index = 0; index < SLOW_RESOLUTION; index++) {
    int value = 0;
    if(index < SLOW_MIDPOINT) {
      value = index * ((double) HEIGHT_BUFFER_RESOLUTION / SLOW_MIDPOINT);
    } else {
      value = (SLOW_RESOLUTION - index) * ((double) HEIGHT_BUFFER_RESOLUTION / SLOW_MIDPOINT);
    }
    heightWaveGuide[index] = value;
    
    #ifdef DEBUG_WAVEFORM
    String data = (String) "Height: " + (String) index + (String) " : " + (String) value;
    printConsoleMessage(data);
    #endif 
  }
  
  #elif (GUIDESTYLE == 1)
  // Constructs width table
  buildSineWaveform((WIDTH_BUFFER_RESOLUTION / 2), (WIDTH_BUFFER_RESOLUTION / 2), 90, 1, (int16_t*) &widthWaveGuide[0], FAST_RESOLUTION);

  // Constructs height table
  buildSineWaveform((HEIGHT_BUFFER_RESOLUTION / 2), (HEIGHT_BUFFER_RESOLUTION / 2), 90, 1, (int16_t*) &heightWaveGuide[0], SLOW_RESOLUTION);
  #endif
}
#endif

/*
 * Every time a conversion is complete, this function is 
 * called.
 */
 //#ifdef SAMPLE_READ
void adc0_isr(void) {
  uint16_t value = adc->analogReadContinuous(ADC_0);
  #ifdef MONITOR_BUFFER
  if(readReady) {
    *(widthBufferPointer + widthCounter) += value;
    *(widthBufferCounterPointer + widthCounter) += 1;
  }
  #endif
  
  #ifdef DEBUG_ADC
    #warning Warning! "Enabling DEBUG_ADC will stop the program after the first read!"
    printConsoleError("Debug: ADC value is " + value);
  #endif
}
//#endif

/*
 * This interrupt function is called to increment the width
 */
#ifdef MONITOR_BUFFER
void widthIncrement() {
  if(monitorActive) {
    #ifdef DEBUG_WIDTH_INCREMENT
    #warning "Enabling debug statements in the width interrupt will probably cause issues."
    String data = "Width Data: [" + widthTime + ":" + widthCounter + "]";
    printConsoleMessage(data);
    #endif
  
    #ifndef SAMPLE_READ // If reading is disabled, then blank information is filled in
    widthBufferPointer[widthCounter] = widthCounter + heightCounter;
    widthBufferCounterPointer[widthCounter] = 1;
    #endif
    
    widthTime++;
    if(widthTime >= FAST_RESOLUTION) {
      widthTime = 0;
    }
    
    widthCounter = widthWaveGuide[widthTime];
  
    #ifdef SAMPLE_READ
    // We may or may not want to log more data depending on the reader mode
    if(((widthTime > FAST_MIDPOINT) && (READ_MODE == saveRight)) || ((widthTime < FAST_MIDPOINT) && (READ_MODE == saveLeft))) {
      readReady = false;
    } else {
      readReady = true;
    }
    #endif
  }
}
#endif

/*
 * This function is called to increment the height
 */
#ifdef MONITOR_BUFFER
void heightIncrement() {
  if(monitorActive) {
    #ifdef DEBUG_INTERRUPT_HEIGHT_INCREMENT_TIME
      int currentTime = micros();
    #endif
    
    #ifdef DEBUG_INTERRUPT_HEIGHT_INCREMENT
    #warning "Enabling debug statements in the height interrupt might cause issues."
    string data = "Height Data: [" + heightTIme + ":" + heightCounter + "]";
    printConsoleMessage(data);
    #endif
  
    // Full set of images produced
    heightTime++;
    if(heightTime >= SLOW_RESOLUTION) {
      heightTime = 0;
      //writeReady != writeReady;
    }
    
    // If the current Y level has changed, then the buffer must be switched
    if(heightWaveGuide[heightTime] != heightCounter) {
      heightCounter = heightWaveGuide[heightTime];
  
      // Marks used buffer for transportation
      if(widthBufferReadPointer == NULL) {
        // Marks the current buffer as ready for transmission
        widthBufferReadPointer = widthBufferPointer;
        widthBufferReadCounterPointer = widthBufferCounterPointer;
        // Switches to the next buffer
        if(widthBufferPointer == widthBufferOne) {
          widthBufferPointer = widthBufferTwo;
          widthBufferCounterPointer = widthBufferCounterTwo;
        } else {
          widthBufferPointer = widthBufferOne;
          widthBufferCounterPointer = widthBufferCounterOne;
        }
        #ifdef DEBUG_INTERRUPT_HEIGHT_INCREMENT
        printConsoleMessage("Height buffer changed.");
        #endif
      } else {
        // If there is no available buffer, an error is thrown and the system stops
        printConsoleError("Error: No available buffer for height increment");
      }
      
    }
    #ifdef DEBUG_INTERRUPT_HEIGHT_INCREMENT_TIME
    int newTime = micros();
    printConsoleMessage("Height Interrupt Time (uS): " + (newTime - currentTime));
    #endif
  }
}
#endif

/*
 * This function prints an error to the console and stops the program.
 */
void printConsoleError(String error) {
  cli();
  //printConsoleMessage(error, ILI9341_RED);
  #ifdef PIN_LED_RED
  digitalWrite(PIN_LED_RED, HIGH);
  #endif
  while(true);
}

/*
 * Prints a message to serial and to the monitor if defined
 */
void printConsoleMessage(String message, uint16_t color) {
  #ifdef SERIAL_MESSAGES
  Serial.println(message);
  #ifdef MONITOR_CONSOLE
  //addNewLine(message, color);
  #endif
  #endif
}

// Part of jank solution for heightIncrement.end crash, TODO please kill
/*
 * Stops DAC output
 */
 /*
void haltOutput() {
  fastSine.amplitude(0);
  slowSine.amplitude(0);
  monitorActive = false;
  tft.fillRect(0, 0, MONITOR_MAX_WIDTH, MONITOR_MAX_HEIGHT, ILI9341_BLACK);
}
*/

/*
 * Restarts DAC output, resets counters etc. TODO review or destroy me
 */
 /*
void restartOutput() {
  tft.fillRect(0, 0, MONITOR_MAX_WIDTH, MONITOR_IMAGE_HEIGHT, ILI9341_BLACK);
  monitorActive = true;
  fastSine.amplitude(1);
  slowSine.amplitude(1);
  fastSine.phase(90);
  slowSine.phase(90);
  widthTime = 0;
  heightTime = 0;
}
*/

