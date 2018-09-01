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
bill = 1000000000

# Size of scan area
defw = 500
defh = 500

# Background Image
IMG = QImage('grid.png')

# To fill the screen in 10 seconds:

# Waveform Data
XHz = 25  # Hertz
YHz = 0.1
XMag = 3.3 # Magnitude in volts
YMag = 3.3
XWave = 0 # Waveform: 0 = Sine, 1 = Sawtooth, 3 = Triangle
YWave = 0

# Resolution of generated waveform LUT
waveRes = 1000

# Display Thread stats
PIX_PER_UPDATE      = 25000
DISP_PERIOD         = 1000

# Data Thread Stats
ADC_BUFFERSIZE      = 1024  # NOTE: Check the PiPion firmware before changing this.
ADC_SAMPLEFREQUENCY = 40000 # Hertz, frequency of ADC sampling.
ADC_POLLFREQUENCY   = ADC_SAMPLEFREQUENCY/ADC_BUFFERSIZE

CALL_PERIOD = bill / FREQ_OF_SAMPLE
BETWEEN_TIME = CALL_PERIOD / SAMP_PER_CALL
