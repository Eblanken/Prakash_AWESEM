# This file holds all the project constant variables
# and should be used mainly for debugging purposes.
# All user-approved variables are handled through
# the GUI instead.

# To successfully run this application
# download the following: PyQt5, numpy, scipy,
# UniversalPiAPI, spidev (comes with Linux OS)
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

# Waveform Frequencies
XHz = 25
YHz = 0.1

# Resolution of generated waveform
waveRes = 1000

# Display Thread stats
PIX_PER_UPDATE = 25000
PERIOD_OF_DISP = 1000

# Data Thread Stats
FREQ_OF_SAMPLE = XHz
SAMP_PER_CALL = 1000

CALL_PERIOD = bill / FREQ_OF_SAMPLE
BETWEEN_TIME = CALL_PERIOD / SAMP_PER_CALL

# Pinouts for Pi
XDAC = 1
YDAC = 2
VADC = 4
