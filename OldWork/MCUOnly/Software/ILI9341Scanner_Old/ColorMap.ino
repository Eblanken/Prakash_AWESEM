#ifdef MONITOR
/*
 * This file contains functions to interpret the intensity data from the sensor
 * in an easy to read color scheme. This file is only included if the monitor is in use.
 */

// Constants:

#define COLOR_MODE 3 // The color mode defines how intensity is portrayed, can be greyscale (0), red-yellow gradient (1), rainbow (2), or Viridis (3)

// Function definitions:

/*
 * This function converts RGB to 565 format // TODO unnecessary for greyscale, can be made faster
 */
inline uint16_t color565(uint8_t r, uint8_t g, uint8_t b) {
  return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}

#if (COLOR_MODE == 0) // Greyscale
/*
 * This function just converts the intensity to greyscale.
 */
int pixelColor565(int analogInput) {
  byte val = ((analogInput / ((double) ANALOG_MAX)) * 255);
  return color565(val, val, val);
}

#elif (COLOR_MODE == 1) // Red-Yellow

/*
 * This function converts analog input into 565 color as a linear map from
 * red to yellow. I found this function at the same site for rainbow565.
 */
int pixelColor565(int analogInput) {
  return color565(255, (255 - ((analogInput / ((double) ANALOG_MAX)) * 255)), 0);
}

#elif (COLOR_MODE == 2) // Rainbow

/*
 * This function converts analog input into 565 color as a long rainbow.
 * 
 * I found this function at https://www.particleincell.com/2014/colormap/
 * This site has a few other helpful color scales as well.
 * 
 * WARNING: Rainbow has poor color ranges for general use
 */
int pixelColor565(int analogInput) {
  byte r, g, b;
  double a = ((ANALOG_MAX - analogInput) / (ANALOG_MAX / 5.0));
  byte x = (byte) (a);
  byte y = (byte) (255 * (a - x));
  switch(x) {
    case 0:
      r = 255;
      g = y;
      b = 0;
      break;
    case 1:
      r = 255 - y;
      g = 255;
      b = 0;
      break;
    case 2:
      r = 0;
      g =  255;
      b = y;
      break;
    case 3:
      r = 0;
      g = 255 - y;
      b = 255;
      break;
    case 4: 
      r = y;
      g = 0; 
      b = 255; 
      break;
    case 5:
      r = 255;
      g = 0;
      b = 255;
      break;
  }
  return color565(r, g, b);
}

#elif (COLOR_MODE == 3) // Viridis
 const byte viridisR[] PROGMEM = {68,69,69,69,70,70,70,71,71,71,71,72,72,72,72,72,72,72,72,72,72,73,72,
                        72,72,72,72,72,72,72,72,72,71,71,71,71,70,70,70,70,69,69,69,68,68,67,
                        67,67,66,66,65,65,65,64,64,63,63,62,62,61,61,60,60,59,59,58,58,57,57,
                        56,56,55,55,54,54,53,53,52,52,52,51,51,50,50,49,49,48,48,48,47,47,46,
                        46,45,45,45,44,44,43,43,43,42,42,42,41,41,40,40,40,39,39,39,38,38,37,
                        37,37,36,36,36,35,35,35,34,34,34,33,33,33,32,32,32,32,31,31,31,31,31,
                        31,31,31,31,31,31,31,31,31,32,32,32,33,33,34,34,35,36,37,38,38,39,40,
                        41,43,44,45,46,48,49,50,52,53,55,56,58,60,61,63,65,67,68,70,72,74,76,
                        78,80,82,84,86,88,90,92,95,97,99,101,103,106,108,110,113,115,117,120,
                        122,125,127,130,132,135,137,140,142,145,147,150,153,155,158,160,163,
                        166,168,171,174,176,179,182,184,187,190,192,195,198,201,203,206,209,
                        211,214,216,219,222,224,227,229,232,235,237,240,242,245,247,249,252,254};
 const byte viridisG[] PROGMEM = {1,2,4,5,7,8,10,11,13,14,16,17,19,20,22,23,24,26,27,28,30,31,32,34,35,
                        36,37,39,40,41,42,44,45,46,47,49,50,51,52,54,55,56,57,58,60,61,62,63,
                        64,66,67,68,69,70,71,73,74,75,76,77,78,79,80,81,83,84,85,86,87,88,89,
                        90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,
                        110,111,112,113,114,115,116,117,118,119,120,121,122,123,123,124,125,126,
                        127,128,129,130,131,132,133,134,135,136,137,138,139,139,140,141,142,143,
                        144,145,146,147,148,149,150,151,152,153,154,155,156,156,157,158,159,160,
                        161,162,163,164,165,166,167,168,169,170,170,171,172,173,174,175,176,177,
                        178,179,180,180,181,182,183,184,185,186,187,187,188,189,190,191,192,193,
                        193,194,195,196,197,197,198,199,200,200,201,202,203,203,204,205,206,206,
                        207,208,208,209,210,210,211,212,212,213,213,214,215,215,216,216,217,217,
                        218,218,219,219,220,220,221,221,222,222,222,223,223,224,224,224,225,225,
                        225,226,226,226,227,227,227,228,228,228,229,229,229,230,230,230,231,231,
                        231,232,232};
 const byte viridisB[] PROGMEM = {84,86,87,89,90,92,93,95,96,98,99,100,102,103,104,106,107,108,109,110,112,
                        113,114,115,116,117,118,119,120,121,122,123,124,125,125,126,127,128,128,
                        129,130,130,131,132,132,133,133,134,134,135,135,136,136,136,137,137,138,
                        138,138,138,139,139,139,139,140,140,140,140,140,141,141,141,141,141,141,
                        141,142,142,142,142,142,142,142,142,142,142,142,142,143,143,143,143,143,
                        143,143,143,143,143,143,143,143,143,143,143,143,143,143,143,143,143,143,
                        143,143,143,143,142,142,142,142,142,142,142,142,142,142,141,141,141,141,
                        141,141,140,140,140,140,139,139,139,139,138,138,138,137,137,137,136,136,
                        135,135,134,134,134,133,133,132,131,131,130,130,129,128,128,127,126,126,
                        125,124,123,123,122,121,120,119,118,118,117,116,115,114,113,112,111,110,
                        109,108,106,105,104,103,102,101,99,98,97,95,94,93,91,90,89,87,86,84,83,
                        81,80,78,77,75,74,72,71,69,67,66,64,62,61,59,57,55,54,52,50,49,47,45,43,
                        42,40,38,37,35,34,32,31,29,28,27,26,26,25,25,24,24,25,25,26,27,28,29,30,
                        32,33,35,37};

/*
 * This function just references a lookup table for the Viridis color scheme
 * that I found at: https://gist.github.com/kanchukaitis/bcf0f7a3d1556cbfdb05
 */
int pixelColor565(int analogInput) {
  byte val = (analogInput / (double) ANALOG_MAX) * 256;
  return color565(viridisR[val], viridisG[val], viridisB[val]);
}

#endif
#endif



