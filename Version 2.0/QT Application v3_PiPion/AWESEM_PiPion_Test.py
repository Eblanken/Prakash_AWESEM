#
# File: AWESEM_PiPion_Test.py
# ------------------------------
# Author: Erick Blankenberg
# Date: 8/25/2018
#
# Description:
#   This script makes sure everything is working.
#
# Note:
#   Speeding up matplotlib: https://bastibe.de/2013-05-30-speeding-up-matplotlib.html
#

import matplotlib
from matplotlib import pyplot as plt
import numpy
import time
from AWESEM_PiPion_Interface import AWESEM_PiPion_Interface

PiPion = AWESEM_PiPion_Interface()

print(PiPion.getDacFrequency(0))
print(PiPion.getDacFrequency(1))

PiPion.setDacFrequency(1, 1.00)
PiPion.setDacWaveform(1, 3)

print(PiPion.getDacWaveform(1))
print(PiPion.getDacFrequency(0))
print(PiPion.getDacFrequency(1))

PiPion.beginEvents()

"""
PiPion.setDacFrequency(1, 12.00)
print(PiPion.getDacFrequency(1))

PiPion.setDacFrequency(0, 4.55)
print(PiPion.getDacFrequency(0))

PiPion.setDacMagnitude(0, 2.54)
print(PiPion.getDacMagnitude(0))

PiPion.setDacMagnitude(1, 1.24)
print(PiPion.getDacMagnitude(1))

PiPion.setDacWaveform(0, 0)
print(PiPion.getDacWaveform(0))
PiPion.setDacWaveform(1, 0)
print(PiPion.getDacWaveform(1))

print(PiPion.getAdcFrequency())
PiPion.setAdcFrequency(10000) # Barely keeps up at 12500, inefficiency is in matplotlib, can easily match 40,000 otherwise.
print(PiPion.getAdcFrequency())

PiPion.beginEvents()
plt.figure(1)
while True:
    values = PiPion.getDataBuffer()
    if values is not None:
        plt.plot(values[:, 2])
        plt.show()
"""