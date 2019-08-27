#
# File: ProcessingFuncs.py
# --------------
# Erick Blankenberg
# AWESEM
# 6/27/2019
#
# Description:
#   Encapsulates image processing functions used for symmetry detection.
#

import numpy
from   math  import floor
from   math  import ceil
from   scipy import interpolate
from   scipy import ndimage
from   skimage.exposure import adjust_gamma
from   skimage.segmentation import clear_border
import skimage.filters as filters

## --------------------------- Getting the Phase ---------------------------- ##

def getAssumedTroughPhase(targetImage):
    return getSymmetryPhaseFromVals(evaluatePatchVerticalSymmetry(targetImage))

# Evaluates symmetry along rows for the given patch
def evaluatePatchVerticalSymmetry(targetImage):
    # Uses patches that are essentially the original image barrel shifted so energy is always the same
    totalEnergy = numpy.sum(targetImage * targetImage)
    # Evaluates symmetry score about every column one at a time
    symmetryVals = numpy.zeros((targetImage.shape[1]))
    for currentCenterColumn in range(int(targetImage.shape[1])):
        # Finds numerator
        columnStartLeft  = currentCenterColumn
        columnStartRight = currentCenterColumn
        numeratorAccumulator = 0
        for currentColumnOffset in range(int(ceil(targetImage.shape[1] / 2.0))):
            numeratorAccumulator += numpy.sum(targetImage[:, columnStartLeft] * targetImage[:, columnStartRight])
            columnStartLeft = int((columnStartLeft + 1) + targetImage.shape[1]) % targetImage.shape[1]
            columnStartRight = int((columnStartRight - 1) + targetImage.shape[1]) % targetImage.shape[1]
        # Normalizes and stores
        symmetryVals[currentCenterColumn] = numeratorAccumulator / totalEnergy
    return symmetryVals

def getSymmetryPhaseFromVals(symmetrySequence):
    assumedTroughPoint = numpy.argmax(symmetrySequence) % floor(max(symmetrySequence.shape)) # Assumed to have period equal to width of image and actual displacement
    return (float(assumedTroughPoint) / float(max(symmetrySequence.shape))) * (2.0 * numpy.pi)


## ------------------------- Getting the Magnitude -------------------------- ##



# Uses crest as reference point at zero in an assumed cosine displacement function to be inverted
def resampleVerticalDistortion(distortedImage, phaseToTrough):
    imageInterpolator = interpolate.interp2d(range(distortedImage.shape[1]), range(distortedImage.shape[0]), distortedImage, bounds_error = False) # Is occasionally slightly over by 0.75
    offsetToCrest = ((phaseToTrough + numpy.pi) / (numpy.pi * 2.0)) * distortedImage.shape[1]
    rebuiltImageFalling = numpy.zeros(distortedImage.shape)
    rebuiltImageRising  = numpy.zeros(distortedImage.shape)
    #targetColumnsFalling = numpy.zeros((targetImage.shape[1])) - 1
    #targetColumnsRising = numpy.zeros((targetImage.shape[1]))  - 1
    for currentColumn in range(distortedImage.shape[1]):
        baseOffset = numpy.arccos(((currentColumn * 2.0) / distortedImage.shape[1]) - 1) * (distortedImage.shape[1]) / (2.0 * numpy.pi)
        targetColumnFalling = (offsetToCrest + baseOffset) % distortedImage.shape[1]
        targetColumnRising  = ((offsetToCrest - baseOffset) + distortedImage.shape[1]) % distortedImage.shape[1]
        rebuiltImageFalling[:, currentColumn] = (imageInterpolator(targetColumnFalling, range(distortedImage.shape[0]))).flatten()
        rebuiltImageRising[:, currentColumn]  = (imageInterpolator(targetColumnRising, range(distortedImage.shape[0]))).flatten()
        #targetColumnsFalling[currentColumn] = targetColumnFalling
        #targetColumnsRising[currentColumn]  = targetColumnRising
    return rebuiltImageRising, rebuiltImageFalling #, targetColumnsFalling, targetColumnsRising

# Isolates elements
def isolateAndLabelNonOcccluded(inputImage):
    moddedImage = adjust_gamma(inputImage, gamma = 5)
    thresholdedVals = moddedImage > filters.threshold_local(moddedImage, block_size = 125)
    moddedImage = clear_border(thresholdedVals)
    moddedImage = ndimage.binary_opening(moddedImage) # Remove salt
    moddedImage = ndimage.binary_closing(moddedImage) # Remove pepper
    labeled_bars, numBars = ndimage.label(moddedImage)
    return (labeled_bars, numBars)

# Gets width counts for every row for every element
def getLabelWidthCounts(labeled_bars, numBars):
    rowStats = [0] * numBars
    for bar in range(numBars):
        currentRowStats = numpy.zeros(labeled_bars.shape[0])
        for currentRow in range(labeled_bars.shape[0]):
            currentRowStats[currentRow] = numpy.sum(labeled_bars[currentRow, :] == (bar + 1))  # Bars labeled 1..numBars inclusive
        rowStats[bar] = currentRowStats[currentRowStats[:] > 0]
    return rowStats

# Get spacing between centroids for each adjacent labelled object in the image for every row slice
# Ideally the average spacing would be the same as the grid period
def getLabelHorizontalSpacings(labeled_bars, numBars):
    rowStats = [0] * labeled_bars.shape[0]
    for currentRow in range(labeled_bars.shape[0]):
        targetRow = labeled_bars[currentRow, :]
        # Identifies centroids
        targVals = numpy.unique(targetRow)
        targVals = targVals[targVals > 0]
        resultStorage = numpy.zeros(targVals.shape[0])
        for currentTargetIndex in range(targVals.shape[0]):
            resultStorage[currentTargetIndex] = numpy.mean(numpy.nonzero(targetRow == targVals[currentTargetIndex]))
        rowStats[currentRow] = numpy.diff(numpy.sort(resultStorage))
    return rowStats
