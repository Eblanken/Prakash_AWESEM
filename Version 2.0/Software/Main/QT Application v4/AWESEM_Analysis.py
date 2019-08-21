#
# File: AWESEM_Analysis.py
# ------------------------------
# Author: Erick Blankenberg
# Date: 9/11/2018
#
# Description:
#   This class has methods for an image analysis and distortion
#   correction pipeline.
#
#   The general approach is as follows:
#       1). Assign rough location by using driving waveform w/ phase shift
#           a). Build "Modern Art" image by stacking fast waveforms from
#               travel along both directions of fast and slow axis
#           b). The resulting image has four quadrants, upper/lower is back/fourth
#               of vertical slow axis, left/right is back/fourth of fast axis. However,
#               there is probably a phase offset. Identify this phase offset by checking
#               for mirror symmetry vertically and horizonally. The program assumes that this
#               phase offset will be less than half of the full period and so will
#               check close to the middle and edges of the image from a).
#           c). Return phase offsets for use with a periodic mapping function.
#       2). If imaging a grid, find a distortion correction map using splines.
#           a). Retrieve an image generated from step 1, one that is already
#               roughly aligned.
#           b). Segment this image and identify the lines between the grid squares,
#               sort these lines into two perpendicular camps
#           c). Find the average distance between parralel lines, build a r
#

import numpy as np
from   scipy import signal
from   math import ceil

# ------------------- Image Processing Methods --------------

#
# Description:
#   Acquires a full pane of imaging data for the given parameters
#   and builds a calibrated mapping file. Assumes that the target under
#   the microscope is a grid.
#
def preformCalibration():
    print("Not Implemented")
    """
    baseImage           = acquireModernArt()
    lutCorrectedData    = retrievePhases(baseImage)
    imageDistortionMaps = retrieveRefinement(lutCorrectedData)
    """
#
# Description:
#   Finds the phase offsets associated with the given base "modern art"
#   image. Values are percentage of period of function of each axis.
#
#
#def retrievePhases(fastPeriod, slowPeriod, sampleData):

#
# Description:
#   Finds distortion maps for each of four iamges (rising falling vertical,
#   rising falling horizontal) seperated and given initial values using data
#   from the retrievePhases method.
#

# ------------------- Image Mapping Functions --------------

#
# Description
#  Creates look up table that simulates the steady state response of the
#  system to the given 256 sample input at the given frequency.
#
def findSteadyStateResp(systemModel, wavetableRaw, waveformFrequency):
    transientTime = 1.0
    extendPeriods = 2.0
    waveformPeriodLength    = 1.0 / waveformFrequency
    wavetablePadded         = (np.append(wavetableRaw, wavetableRaw[0]) / 32767.0) * (3.3 / 2.0) # Convertes 16 bit signed integer to vpp, also pads with first sample at end to emulate wraparound, note that MCU does the same thing
    wavetableTimes          = np.append(np.arange(start = 0, stop = waveformPeriodLength, step = waveformPeriodLength / float(wavetableRaw.shape[0])), waveformPeriodLength + waveformPeriodLength / float(wavetableRaw.shape[0]))
    systemLUTLen = 256 # TODO see LTI reconstruction notes, there has to be a better way
    # Also generally we should convert the continuous model to a discrete model
    # Version here is really janky
    numPeriods              = int(ceil(transientTime * waveformFrequency) + extendPeriods)
    oneShotTimesLUT         = np.linspace(start = 0, stop = waveformPeriodLength, num = systemLUTLen)
    oneShotValsLUT          = np.interp(oneShotTimesLUT, wavetableTimes, wavetablePadded)
    extendedOneShotValsLUT  = np.tile(oneShotValsLUT, numPeriods) # Clears transient time + last period is clean
    extendedOneShotTimesLUT = np.linspace(0, numPeriods * waveformPeriodLength, extendedOneShotValsLUT.shape[0])
    newTimesLUT, newValsLUT, _ = signal.lsim(systemModel, extendedOneShotValsLUT, extendedOneShotTimesLUT, interp = "True")
    newValsLUTLastPeriod  = newValsLUT[-systemLUTLen:]
    newTimesLUTLastPeriod = newTimesLUT[-systemLUTLen:]
    stableLUT               = newValsLUT
    stableTimes             = newTimesLUT % waveformPeriodLength
    return stableTimes, stableLUT

# Normalizes the given lookup tabke to monitor dimensions and returns a scale
# factor for the scale bar on the monitor
def normalizeDisplacement(stableLUT, imageDimension):
    min = np.min(stableLUT)
    max = np.max(stableLUT)
    totalDisp = max - min
    screenLUT = np.round(((stableLUT - min) / totalDisp) * imageDimension).astype(np.uint16)
    scaleFactor = float(totalDisp) / float(imageDimension) # Microns per pixel
    return screenLUT, scaleFactor

#
# Description
#   Returns the value of a cose function for the given parameters,
#   migrated from WaveGen.
#
# Parameters:
#   'inputTime' The time to evaluate in seconds
#   'amplitude'  Amplitude of wave
#   'frequency' Frequency of the sine in hz
#   'phase'     Phase of the sine wave as a percentage of 2pi
#   'baseOffset' Shift upwards applied to all points. By default set to amplitude (so that base is 0)
#
def cos(inputTime, amplitude, frequency, phase, baseOffset = None):
    if inputTime is None: # Filtering can send "None" as input data occasionally
        return None
    if baseOffset is None:
        baseOffset = amplitude
    return amplitude * np.cos((inputTime * frequency - phase + 0.5) * 2.0 * np.pi) + baseOffset
#
# Description
#   Returns the value of a triangle function for the given parameters,
#   migrated from WaveGen. Ranges from [0, 1.0].
#
# Parameters:
#   'inputTime' The time to evaluate in seconds
#   'amplitude'  Amplitude of wave
#   'frequency' Frequency of the triangle wave in hz
#   'phase'     Phase delay of the function as a fraction of the full period.
#   'baseOffset' Shift upwards applied to all point, by default shifted up by none (so that base is 0)
#
def triangle(inputTime, amplitude, frequency, phase, baseOffset = None):
    if inputTime is None: # Filtering can send "None" as input data occasionally
        return None
    if baseOffset is None:
        baseOffset = amplitude
    return ((2.0 * amplitude) / np.pi) * (np.arcsin(np.sin(((inputTime * frequency) - phase - 0.25) * 2.0 * np.pi))) + baseOffset

#
# Description
#   Returns the value of a sawTooth function for the given parameters,
#   migrated from WaveGen. Note that the triangular wave is offset so that it is centered
#   at zero.
#
# Parameters:
#   'inputTime'  The time to evaluate in seconds
#   'amplitude'  Amplitude of wave
#   'frequency'  Frequency of the sawTooth wave in hz
#   'phase'      Phase delay of the function as a fraction of the full period.
#   'baseOffset' Shift upwards applied to all points, by default shifted up by amplitude (so that base is 0)
#
def sawTooth(inputTime, amplitude, frequency, phase, baseOffset = None):
    if inputTime is None: # Filtering can send "None" as input data occasionally
        return None
    if baseOffset is None:
        baseOffset = amplitude
    return (2 * amplitude * np.mod((inputTime - phase / frequency), 1.0/frequency) * frequency) + baseOffset - amplitude
