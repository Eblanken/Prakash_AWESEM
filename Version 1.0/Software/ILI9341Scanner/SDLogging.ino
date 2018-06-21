/*
 * This file includes an object that manages logging images to the on-board SD
 * card for the Teensy 3.6. I found the image logging code 
 * here: https://forum.arduino.cc/index.php?topic=406416.0.
 */

// TODO
    // Multiple image sizes on same object, how to deal with multiple objects,
    // logging text files?
    // All activity happens in IMAGE_LOCATION folder, multiple folders?
    // debugging preprocessor commands

// Included Libraries:

/*
#ifndef __SDFAT_H
#include SDFAT.h

// Class Definitions:

class DataLogger {
  SdFatSdio SD;
  SdFile file;
  const static String IMAGE_LOCATION = "Screenshots";
  int currentSession;
  int currentScreenshot;
  int imageWidth;
  int imageHeight;

  findAvailableSession();
  openNewScreenshot();
  saveScreenshot();
  public:
  DataLogger(int imageWidth, int imageHeight);
  ~DataLogger();
  logData(int index, uint16_t* pixelArray, int pixelArraySize);
  stopLogging();
  
}
*/
// Function Definitions:

/*
 * This is the constructor for the data logger object.
 * The constructor defines the expected size of the images
 * to write and also 
 */
 /*
void DataLogger::DataLogger(int imageWidth, int imageHeight) {
  // Initializes SD card
  if (!sd.begin()) {
    Serial.println(F("Failed to initialize SD card.")) // TODO replace with console
  }
  // Builds image directory if necessary
  if(!sd.exists(IMAGE_LOCATION)) {
    if(!sd.mkdir(IMAGE_LOCATION)) {
      Serial.println(F("Creation of root folder failed.")); // TODO replace with console
    } else {
      Serial.println(F("Created new root folder.")); // TODO replace with console
    }
  }
  // Navigates to current directory
  if(!sd.chdir(IMAGE_LOCATION)) {
    Serial.println(F("Folder navigation failed."));
  }
  
  this.imageWidth = imageWidth;
  this.imageHeight = imageHeight;
  this.currentSession = findAvailableSession();
  this.currentScreenshot = 1; // Screenshots start at 1

  openNewScreenshot();
  
}
*/

/*
 * This function logs the given line of pixels at the specified vertical
 * index.
 * 
 * The index parameter is the vertical index to log at, the pixelArray 
 * pointer is the pointer to the vector to use for pixel values, and 
 * the pixelArraySize is the size of the vector to log.
 * 
 * It is assumed that pixels sent to this function are in 565 format, they
 * are converted to 555 as part of the write process.
 */
 /*
void DataLogger::logData(int index, uint16t* pixelArray, int pixelArraySize, bool newFile) {
  if(newFile) {
     
  }
}
*/
/*
 * This function just searches through to find the latest available session #
 * from the given images file. It is assumed that all images are stored in the
 * format "[sessionNumber]_[screenshotNumber].bmp"
 */
 /*
int DataLogger::findAvailableSession() {
  char fileName[10]; // TODO replace 10 with a constant
  int largest = 0;
  while(file.openNext(sd.vwd(), 0_READ)) {
    file.getFilename(fileName);
    file.close();
    int count = 0;
    // Finds size of session
    for(int index = 0; index < 10; index++) {
      if(fileName[index] == '_') {
        break;
      }
      count += pow(10,index) * (fileName[index] - '0');
    }
    if(count > largest) largest = count;
  }
  return largest + 1;
}
*/

/*
 * This function opens a new 
 */



