#
# File: AWESEM_Constants.py
# ------------------------------
# Author: Brion Ye
# Date:
#
# Description:
#   This file holds all the project constant variables
#   and should be used mainly for debugging purposes.
#   All user-approved variables are handled through
#   the GUI instead.
#
# Edits:
#  - Erick Blankenberg, adapted to use teensy 3.6.
#

from PyQt5.QtGui import *

# Math Constants
pi = 3.1415926535
mill = 1000000

# Size of scan area
RES_W = 400
RES_H = 400

# Defaults
DEFAULT_XHZ   = 50  # Hertz
DEFAULT_YHZ   = 0.05
DEFAULT_XMAG  = 1.65 # Magnitude in volts
DEFAULT_YMAG  = 1.65
DEFAULT_XWAVE = 3 # Waveform: 0 = Sine, 1 = Sawtooth, 3 = Triangle
DEFAULT_YWAVE = 3

# Resolution of generated waveform LUT
waveRes = 1000

# Display Thread stats
PIX_PER_UPDATE      = 25000
DISP_PERIOD         = 1000 #?

# Data Thread Stats
ADC_BUFFERSIZE      = 1024  # NOTE: Check the PiPion firmware before changing this.
ADC_SAMPLEFREQUENCY = 14000 # Hertz, frequency of ADC sampling.
ADC_POLLPERIOD      = 1.0 / float(ADC_SAMPLEFREQUENCY/ADC_BUFFERSIZE)
DISPLAY_POLLPERIOD  = ADC_POLLPERIOD
