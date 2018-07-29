# To successfully run this application
# download the following: PyQt5, numpy, scipy,
# UniversalPiAPI, spidev (comes with Linux OS)

from PyQt5.QtGui import *

# Size of scan area
defw = 500
defh = 500

# Background Image
IMG = QImage('grid.png')

# To fill the screen in 10 seconds:
# (defw*defh*SAMP_PER_CALL)/(PIX_PER_UPDATE/PERIOD_OF_DISP*1000*FREQ_OF_SAMPLE)<=10

# Display Thread stats
PIX_PER_UPDATE = 1000
PERIOD_OF_DISP = 1000

# Data Thread Stats
FREQ_OF_SAMPLE = 0.01  # in seconds
# in 500x500 sine, 2K
# in 500x500 triangle, 500
SAMP_PER_CALL = 1000

CALL_PERIOD = 10000000
BETWEEN_TIME = CALL_PERIOD / SAMP_PER_CALL

# Pinouts for Pi
XDAC = 1
YDAC = 2
VADC = 4

# Waveform Frequencies
XHz = 100
YHz = 0.1

# Resolution of generated waveform
waveRes = 1000

# Math Constants
pi = 3.1415926535
bill = 1000000000
