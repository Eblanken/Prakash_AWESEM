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
#   Finds the phase offsets associated with the 
#
#
#def retrievePhases(fastPeriod, slowPeriod, sampleData):

# ------------------- Image Mapping Functions --------------

# TODO Revisit basic functions

#
# Description
#   Returns the value of a sine function for the given parameters, 
#   migrated from WaveGen. Ranges from [baseOffset, baseOffset + amplitude].
#
# Parameters:
#   'inputTime' The time to evaluate in seconds
#   'amplitude' Amplitude of the sine output
#   'frequency' Frequency of the sine in hz
#   'phase'     Phase of the sine wave as a percentage of 2pi
#
def sine(inputTime, amplitude, frequency, phase, baseOffset):
    return amplitude * np.sin((inputTime - phase) * frequency * 2.0 * np.pi) + baseOffset
#
# Description
#   Returns the value of a triangle function for the given parameters, 
#   migrated from WaveGen. Ranges from [baseOffset, baseOffset + amplitude].
#
# Parameters:
#   'inputTime' The time to evaluate in seconds
#   'amplitude' Amplitude of the triangle output
#   'frequency' Frequency of the triangle wave in hz
#   'phase'     Phase of the the triangle wave as a percentage of the 
#
def triangle(inputTime, amplitude, frequency, phase, baseOffset):
    return (amplitude / 2.0) * (np.arcsin(np.cos((inputTime - phase) * frequency * 2.0 * np.pi)) + np.pi / 2.0) + baseOffset
    
#
# Description
#   Returns the value of a sawTooth function for the given parameters, 
#   migrated from WaveGen. Ranges from [baseOffset, baseOffset + amplitude]
#
# Parameters:
#   'inputTime'  The time to evaluate in seconds
#   'amplitude'  Amplitude of the sawTooth output
#   'frequency'  Frequency of the sawTooth wave in hz
#   'phase'      Phase delay of the function as a fraction of the full period
#   'baseOffset' Added constant
#
def sawTooth(inputTime, amplitude, frequency, phase, baseOffset):
    return (amplitude * np.mod((inputTime - phase / frequency), 1.0/frequency) * frequency) + baseOffset