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
"""
class ImageCorrection:
    def __init__(self):
    
    
    #
    # Description:
    #   Finds the phase offsets associated with the 
    #
    #
    def retrievePhases(fastPeriod, slowPeriod, sampleData):
    
    def 
"""