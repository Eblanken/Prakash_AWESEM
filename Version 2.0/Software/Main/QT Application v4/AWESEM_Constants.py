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
RES_W = 500
RES_H = 500
PATH_BACKGROUNDIMAGE = "ProgramFiles/grid.png"

# Defaults
DEFAULT_ADC_SAMPLEFREQUENCY = 40.0 # KHz, frequency of ADC sampling.
# Default driving waveform set by insert order
# Default driving waveform frequency in hertz
DEFAULT_VERTHZ = 50  # Hertz
DEFAULT_HORZHZ = 0.03
# Default driving waveform amplitude in volts (centered at 3.3/2)
DEFAULT_VERTAM = 3.30 # Magnitude in volts
DEFAULT_HORZAM = 3.30
# Phase offsets for sample reconstruction
DEFAULT_HORZPHASE = 0.00 # Fraction of period of waveform, positive delays reading (shifts forward)
DEFAULT_VERTPHASE = 0.00
# Reconstruction data sources
DEFAULT_HORZSRC   = 1 # (0) All, (1) Rising displacement, (2) Falling displacement
DEFAULT_VERTSRC   = 1

# Resolution of generated waveform LUT
waveRes = 1000

# Display Thread stats
PIX_PER_UPDATE      = 25000
DISP_PERIOD         = 1000 #?

# Data Thread Stats
BUFFLEN_DATA_TO_REGISTER    = 256
