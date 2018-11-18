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
# TODO:
#   -> Could implement basic LUT's better: https://shocksolution.com/2009/01/09/optimizing-python-code-for-fast-math/
#                                          https://shocksolution.com/2008/12/11/a-lookup-table-for-fast-python-math/
#
#   -> Profile if/else versus trig triangle and mods
#

import numpy as np
    
# ------------------- Image Processing Methods --------------
    
#
# Description:
#   Acquires a full pane of imaging data for the given parameters
#   and builds a calibrated mapping file. Assumes that the target under
#   the microscope is a grid.
#
def preformCalibration():
    baseImage           = acquireModernArt()
    lutCorrectedData    = retrievePhases(baseImage)
    imageDistortionMaps = retrieveRefinement(lutCorrectedData)

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
#   Returns the value of a sine function for the given parameters, 
#   migrated from WaveGen. Ranges from [0, 1.0].
#
# Parameters:
#   'inputTime' The time to evaluate in seconds
#   'frequency' Frequency of the sine in hz
#   'phase'     Phase of the sine wave as a percentage of 2pi
#
def sine(inputTime, frequency, phase, baseOffset):
    return np.sin((inputTime - phase) * frequency * 2.0 * np.pi) + baseOffset
#
# Description
#   Returns the value of a triangle function for the given parameters, 
#   migrated from WaveGen. Ranges from [0, 1.0].
#
# Parameters:
#   'inputTime' The time to evaluate in seconds
#   'frequency' Frequency of the triangle wave in hz
#   'phase'     Phase of the the triangle wave as a percentage of the 
#
def triangle(inputTime, frequency, phase, baseOffset):
    return (1 / 2.0) * (np.arcsin(np.cos((inputTime - phase) * frequency * 2.0 * np.pi)) + np.pi / 2.0)
    
#
# Description
#   Returns the value of a sawTooth function for the given parameters, 
#   migrated from WaveGen. Ranges from [0, 1.0]
#
# Parameters:
#   'inputTime'  The time to evaluate in seconds
#   'frequency'  Frequency of the sawTooth wave in hz
#   'phase'      Phase delay of the function as a fraction of the full period
#
def sawTooth(inputTime, frequency, phase):
    return (np.mod((inputTime - phase / frequency), 1.0/frequency) * frequency)