/*
 * This file contains all of the relevant methods for 
 * manipulating the output image.
 */

// Constants:

#define SYMMETRY_TYPE 1 // Options are: (0) BRUTE, (1) VOTE_BLOB

// Debugging Constants:

//#define DEBUG_SYMMETRY_TIMER // Prints out how long a single symmetry analysis takes in micros.
//#define DEBUG_SYMMETRY_VECTOR
//#define DEBUG_THRESHOLD
//#define DEBUG_THRESHOLD_FAST
//#define DEBUG_BLOB_DETECTION
//#define DEBUG_ERODE
//#define DEBUG_BOXBLUR
//#define SYMMETRY_THRESHOLD

// Function definitions:

/*
 * This function segments the given 1d vector according to the given threshold
 */
void applyThreshold(volatile uint32_t vector[], int vectorSize, uint16_t currentThreshold) {
  #ifdef DEBUG_THRESHOLD
  Serial.print(F("(Threshold) Original Input: "));
  for(int index = 0; index < vectorSize; index++) {
    Serial.print(vector[index] + (String) " ");
  }
  Serial.println();
  #endif

  // Applies threshold
  #ifdef DEBUG_THRESHOLD
  Serial.print(F("(Threshold) Final Output: "));
  #endif
  #ifdef DEBUG_THRESHOLD_FAST
  Serial.print(F("(Threshold) Final Output: "));
  #endif
  for(int index = 0; index < vectorSize; index++) {
    if(vector[index] > currentThreshold) {
      vector[index] = 1;
    } else {
      vector[index] = 0;
    }
    #ifdef DEBUG_THRESHOLD
    Serial.println(vector[index] + (String) " ");
    #endif
    #ifdef DEBUG_THRESHOLD_FAST
    if(!(index % 8)) {
      char val = (vector[index] == 1)? '#':'_';
      Serial.println((String) val + " ");
    }
    #endif
  }
  #ifdef DEBUG_THRESHOLD
  Serial.println();
  #endif 
  #ifdef DEBUG_THRESHOLD_FAST
  Serial.println();
  #endif
}

/*
 * This function erodes the given 1d vector with the given mask size. It is assumed
 * that the vector has already had a threshold applied.
 */
void erode(volatile uint32_t vector[], int vectorSize, int erosionMask) {
  #ifdef DEBUG_ERODE
  Serial.print(F("(Erode) Original Input: "));
  for(int index = 0; index < vectorSize; index++) {
    Serial.print(vector[index] + (String) " ");
  }
  Serial.println();
  #endif
  
  // Assigns eroded values to reference vector
  uint16_t referenceVector[vectorSize] = { 0 };
  #ifdef DEBUG_ERODE
  Serial.print(F("(Erode) Final Output:   "));
  #endif
  for(int16_t index = 0; index < vectorSize; index++) {
    referenceVector[index] = 1; // Innocent until proven guilty
    for(int16_t subIndex = -(erosionMask / 2); subIndex <= erosionMask / 2; subIndex++) {
      int newIndex = ((subIndex + vectorSize) + index) % vectorSize; // Wrap-around
      if(vector[newIndex] == 0) {
        referenceVector[index] = 0;
        break;
      }
    }
    #ifdef DEBUG_ERODE
    Serial.print(referenceVector[index] + (String) " ");
    #endif
  }
  #ifdef DEBUG_ERODE
  Serial.println();
  #endif 
  
  // Assigns reference vector values to old vector
  for(int16_t index = 0; index < vectorSize; index++) {
    vector[index] = referenceVector[index];
  }
}

/*
 * Finds the average of values in a 1d vector.
 */
int findAverage(volatile uint32_t vector[], int vectorSize) {
  uint64_t counter = 0; 
  for(int index = 0; index < vectorSize; index++) {
    counter += vector[index];
  }
  return counter / vectorSize;
}

/*
 * Averages value in an nxn area, currently wraps around
 */
void boxBlur(volatile uint32_t vector[], int vectorSize, int boxWidth) {
  #ifdef DEBUG_BOXBLUR
  Serial.print(F("(Box Blur) Original Input: "));
  for(int index = 0; index < vectorSize; index++) {
    Serial.print(vector[index] + (String) " ");
  }
  Serial.println();
  #endif

  uint32_t referenceVector[vectorSize] = { 0 };
  for(int targetIndex = 0; targetIndex < vectorSize; targetIndex++) {
    int sum = 0;
    int total = 0; // TODO redundant with box dimensions
    for(int subIndex = - (boxWidth / 2); subIndex <= (boxWidth / 2); subIndex++) {
      sum += vector[((targetIndex + subIndex) + vectorSize) % vectorSize];
      total++;
    }
    referenceVector[targetIndex] = sum / total;
  }

  // Saves reference to original vector
  #ifdef DEBUG_BOXBLUR
  Serial.print(F("(Box Blur) Final Output:   "));
  #endif
  for(int index = 0; index < vectorSize; index++) {
    vector[index] = referenceVector[index];
    #ifdef DEBUG_BOXBLUR
    Serial.print(vector[index] + (String) " ");
    #endif
  }
  #ifdef DEBUG_BOXBLUR
  Serial.println();
  #endif
}

/*
 * Convolves the current image with the given kernal, 
 * currently this function wraps pixels at the edge boundaries. 
 * 
 * The vector parameter is the vector to create a convolution for,
 * the vectorColumns and vectorRows parameters are the number of rows
 * and columns in the given input image. The kernal parameters are similar.
 * 
 * The function returns a pointer to the image vector for the 
 * 
 * // TODO 4 bit pixels + other encodings, multiple wrap types 
 */
 /*
uint8_t* convolve(uint8_t vector[], int vectorColumns, int vectorRows, uint8_t kernalVector[], int kernalColumns, int kernalRows) {
  // Allocates convolution vector
  *convolvedVector = (uint8_t*) calloc(vectorColumns * vectorRows, sizeof(**convolvedVector));
  if(!*convolvedVector) {
    Serial.println("(Convolve) Allocation error!");
    while(true);
  }

  // We want to normalize the results of the kernal
  int kernalSum = 0;
  for(int index = 0; index < (kernalColumns * kernalRows); index++) {
    kernalSum += kernalVector[index];
  }

  // Fills in the convolution output with data
  for(int columnIndex = 0; columnIndex < vectorColumns; columnIndex++) {
    for(int rowIndex = 0; rowIndex < vectorRows; rowIndex++) {
      // Traverses kernal
      int accumulator = 0;
      for(int kernalColumnIndex = 0; kernalColumnIndex < kernalColumns; kernalColumnIndex++) {
        for(int kernalRowIndex = 0; kernalRowIndex < kernalRows; kernalRowIndex++) {
          accumulator += vector[((((rowIndex + kernalRows / 2) - kernalRowIndex) % vectorRows) * vectorColumns) + (((columnIndex + kernalColumns / 2) - kernalColumnIndex) % vectorRows)] * kernal[(kernalRowIndex * kernalColumns) + kernalColumnIndex]; 
        }
      }
      accumulator /= kernalSum; // Normalizes result
      (*convolvedVector)[(rowIndex * vectorColumns) + columnIndex] = accumulator;
    }
  }
  
  return convolvedVector;
}
*/

/*
 * Identifies blobs in a given 1d vector and reports average location
 * and total surface area, it is assumed that the
 * vector has already had a threshold applied and that
 * it has been eroded to prevent small blobs. This function identifies
 * both background and foreground blobs. 
 * 
 * The function returns a pointer to an array that stores the
 * blob catalog, in the vector catalog[2x] refers to the position
 * of the blob whereas catalog[2x + 1] refers to the size of the blob.
 * 
 * The vector parameter is the vector to analyze, the vectorSize parameter is
 * the length of the vector to analyze. The catalog and catalogSize parameters
 * are return values by reference for the actual catalog and length of the catalog
 * respectably.
 * 
 * It is the user's responsibility to de-allocate the memory they
 * are using from this function. 
 * 
 * // TODO findBlobs for non-binary images?
 */
void findBlobs(volatile uint32_t vector[], int vectorSize, uint32_t** catalog, int* totalBlobs) {
  if((catalog == NULL) || (totalBlobs == NULL)) {
    Serial.println(F("(Blob Detection) NULL inputs for catalog or totalBlobs!"));
    while(true);
  }
  
  #ifdef DEBUG_BLOB_DETECTION
  Serial.print(F("(Blob_Detection) Original Input: "));
  for(int index = 0; index < vectorSize; index++) {
    Serial.print(vector[index] + (String) " ");
  }
  Serial.println();
  #endif
  
  // Identifies number of blobs and also finds a boundary
  // between two blobs for use as a starting point for the
  // blob search.
  int startIndex = 0;
  *totalBlobs = 0;
  for(int index = 0; index < vectorSize; index++) {
    int prevVal = vector[(index + vectorSize - 1) % vectorSize];
    int currVal = vector[index];
    if(prevVal != currVal) {
      startIndex = index;
      *totalBlobs = *totalBlobs + 1;
    }
  }
  #ifdef DEBUG_BLOB_DETECTION
  Serial.print("Total number of blobs: ");
  Serial.println(*totalBlobs);
  #endif

  // Catalogs blobs working from the start index. 
  *catalog = (uint32_t*) calloc(*totalBlobs * 2, sizeof(**catalog));
  if(!*catalog) {
    Serial.println("(Blob_Detection) Allocation error!");
    while(true);
  }
  int currentBlobIndex = 0;
  int currentBlobSum = 0; // Sums total of blob
  int currentBlobAccumulator = 0; // Sums total of blob * index for centroid
  int oldValue = vector[startIndex];
  #ifdef DEBUG_BLOB_DETECTION
  Serial.println();
  #endif
  for(int index = startIndex; index < startIndex + vectorSize; index++) {
    int currentValue = vector[index % vectorSize];
    if(currentValue == oldValue) {
      // Adds current value to current blob
      /*
      currentBlobSum += currentValue;
      currentBlobAccumulator += currentValue * index;
      */
      currentBlobSum += currentValue;
      currentBlobAccumulator += index;
      #ifdef DEBUG_BLOB_DETECTION
      Serial.print("Adding Value: ");
      Serial.print(currentValue);
      Serial.print(" To blob #: ");
      Serial.print(currentBlobIndex);
      Serial.print(" [ current accumulator = ");
      Serial.print(currentBlobAccumulator);
      Serial.print(" , current sum = ");
      Serial.print(currentBlobSum);
      Serial.println(" ]");
      #endif
    } else {
      // Current index is a new blob, catalogs current blob and moves on
        #ifdef DEBUG_BLOB_DETECTION
      Serial.print("Cataloging Current Blob (location, magnitude): (");
      Serial.print((uint32_t) (currentBlobAccumulator / currentBlobSum) /*% vectorSize*/ );
      Serial.print(" , ");
      Serial.print((uint32_t) currentBlobSum);
      Serial.println(" )");
      #endif
      (*catalog)[currentBlobIndex * 2] = (uint32_t) (currentBlobAccumulator / currentBlobSum) % vectorSize; // Saves position
      (*catalog)[(currentBlobIndex * 2) + 1] = (uint32_t) currentBlobSum; // Saves mass
      // Sets up for next blob
      currentBlobIndex++;
      currentBlobSum = currentValue;
      currentBlobAccumulator = index;
    }
    oldValue = vector[index % vectorSize];
  }
  // Catalogs last blob
  (*catalog)[currentBlobIndex * 2] = (uint32_t) (currentBlobAccumulator / currentBlobSum) % vectorSize; // Saves position
  (*catalog)[(currentBlobIndex * 2) + 1] = (uint32_t) currentBlobSum; // Saves mass

  #ifdef DEBUG_BLOB_DETECTION
  Serial.print(F("(DEBUG_BLOB_DETECTION) Total Blobs: "));
  Serial.println(*totalBlobs);
  Serial.print(F("(DEBUG_BLOB_DETECTION) Final Output (location:size): "));
  for(int index = 0; index < *totalBlobs; index++) {
    Serial.print((*catalog)[index * 2]);
    Serial.print(":");
    Serial.print((*catalog)[(index * 2) + 1]);
    Serial.print(" ");
  }
  Serial.println();
  #endif
}

//void identifyVelocity()

#if (SYMMETRY_TYPE == 0)
/*
 * This method uses brute force to find the index in the
 * array with the highest degree of symmetry.
 * 
 * The score per element is determined as the sum
 * of abs(point1 - point2). It is assumed that 
 * the inbound vector wraps around itself.
 * 
 * The function returns the point with the highest
 * symmetry according to this definition. The actual
 * point of interest may be some multiple of the period
 * away.
 * 
 * This is not a good approach, takes roughly 24,110 micros
 * when overclocked to 240 MHZ for full 480 elem vector. 
 * You might be able to speed this up by using smaller types 
 * and smaller vectors, but there are better options available.
 * 
 * // TODO Better to keep track of all values for debugging?
 */
int determineReflection(volatile uint32_t vector[], int vectorSize) {
  #ifdef DEBUG_SYMMETRY_TIMER
  int currentTime = micros();
  #endif

  applyThreshold(vector, vectorSize, findAverage(vector, vectorSize));

  int mirrorSize = vectorSize / 4;
  int lowestIndex = 0;
  uint32_t lowestCount = pow(2,5);
  
  #ifdef DEBUG_SYMMETRY_VECTOR
    Serial.print(F("Symmetry Values: "));
  #endif
  
  for(int startIndex = 0; startIndex < vectorSize; startIndex++) {
    uint32_t currentScore = 0;
    // Compares all mirrored points about the axis startIndex // TODO Modulo might be inefficient
    for(int checkIndex = 0; checkIndex < mirrorSize; checkIndex++) {
      uint32_t backValue = vector[((startIndex - checkIndex) + vectorSize) % vectorSize];
      uint32_t forwardValue = vector[((startIndex + checkIndex) + vectorSize) % vectorSize];
      uint32_t newDelta = 0;
      if(backValue > forwardValue) {
        newDelta = backValue - forwardValue;
      } else {
        newDelta = forwardValue - backValue;
      }
      currentScore += newDelta;
    }
    #ifdef DEBUG_SYMMETRY_VECTOR
    Serial.print(currentScore + (String) " ");
    #endif
    // Only keeps track of lowest score
    if(currentScore <= lowestCount) {
      lowestIndex = startIndex;
      lowestCount = currentScore;
    }
  }
  
  #ifdef DEBUG_SYMMETRY_VECTOR
  Serial.println();
  #endif
  
  #ifdef DEBUG_SYMMETRY_TIMER
  int newTime = micros();
  int finalTime = newTime - currentTime;
  Serial.print("Symmetry Calc Time (Micros): ");
  Serial.print(finalTime);
  Serial.print(" Value (index): ");
  Serial.println(lowestIndex);
  #endif
  
  return lowestIndex;
}
 
#elif (SYMMETRY_TYPE == 1)
/*
 * This method breaks a vector up into similar regions and
 * then finds an axis of symmetry by submitting votes for each
 * pair of regions. The votes are weighted higher if the difference 
 * between the blobs is smaller, the smaller the better.
 */
int determineReflection(volatile uint32_t vector[], int vectorSize) {
  #ifdef DEBUG_SYMMETRY_TIMER
  int currentTime = micros();
  #endif

  // Processes data
  applyThreshold(vector, vectorSize, findAverage(vector, vectorSize));
  erode(vector, vectorSize, 3);
  uint32_t* blobCatalog = NULL;
  int blobCatalogSize = 0; // Remember this is the number of blobs, the vector size is 2 times as large
  findBlobs(vector, vectorSize, &blobCatalog, &blobCatalogSize);

  // Finds largest and smallest blob to determine similarity threshold
  uint32_t largestSize = 0;
  uint32_t smallestSize = UINT32_MAX;
  for(int index = 0; index < blobCatalogSize; index++) {
    largestSize = max(largestSize, blobCatalog[(index * 2) + 1]);
    smallestSize = min(smallestSize, blobCatalog[(index * 2) + 1]);
  }
  const uint16_t SIMILARITY_THRESHOLD = largestSize - smallestSize; // Max dissimilarity allowed, also determines max voting weight // TODO replace
  
  // Compares all blobs, even compares with self. Score is maxPossibleDifference - currentDifference
  uint32_t similarityScores[vectorSize] = { 0 };
  // Charts scores in range
  for(int index = 0; index < blobCatalogSize; index++) {
    for(int subIndex = 0; subIndex < blobCatalogSize; subIndex++) {
      similarityScores[(blobCatalog[index * 2] + blobCatalog[subIndex * 2]) / 2] = SIMILARITY_THRESHOLD - abs(max(blobCatalog[(index * 2) + 1], blobCatalog[((subIndex * 2) + 1)]) - min(blobCatalog[(index * 2) + 1], blobCatalog[((subIndex * 2) + 1)]));
    }
  }

  // Blurs symmetry scores
  boxBlur(similarityScores, vectorSize, 3);

  // Symmetry center found as the lowest score // TODO replace
  //int sum = 0;
  //int accumulator = 0;
  int bestScoreIndex = 0;
  #ifdef DEBUG_SYMMETRY_VECTOR
  Serial.print(F("Symmetry Values: "));
  #endif
  for(int index = 0; index < vectorSize; index++) {
    if(similarityScores[index] > similarityScores[bestScoreIndex]) {
      bestScoreIndex = index;
    }
    //sum += similarityScores[index];
    //accumulator += similarityScores[index] * index;
    #ifdef DEBUG_SYMMETRY_VECTOR
    Serial.print(similarityScores[index]);
    Serial.print(F(" "));
    #endif
  }
  #ifdef DEBUG_SYMMETRY_VECTOR
  Serial.println();
  #endif

  #ifdef DEBUG_SYMMETRY_TIMER
  int newTime = micros();
  int finalTime = newTime - currentTime;
  Serial.print("Symmetry Calc Time (Micros): ");
  Serial.println(finalTime);
  #endif
  
  return bestScoreIndex;
}

#endif 


