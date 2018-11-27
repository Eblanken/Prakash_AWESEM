# This class takes the input data and stores it

import numpy as np
from scipy.interpolate import UnivariateSpline as UVS
import time as time
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import threading as pyth
from queue import Queue
from UniversalPiAPI import UZP
from math import floor
import ProjectConstants as c

# implement SPI interface with the Universal Pi Board and do I/O

sampleData = Queue(250500)
inittime = 0
LUTX = None
LUTY = None


class filler:
    def DACInit(self, a):
        pass

    def DACGenerate(self, a, b, c, d):
        pass

    def DACStart(self, a):
        pass

    def DACStop(self, a):
        pass

    def ADCInit(self, a):
        pass

    def ADCReadData(self, a, b, c, d):
        pass


uzp = filler()


# uzp = UZP()

class UZPIn:
    sec = 0

    def __init__(self):
        # super().__init__()
        uzp.ADCInit(c.VADC)
        self.t = pyth.Timer(1.0, self.sample)

    def sample(self):
        databuff = uzp.ADCReadData([c.VADC], 1, c.SAMP_PER_CALL, c.bill / c.CALL_PERIOD)
        for i in range(c.SAMP_PER_CALL):
            # Stores time in nanoseconds
            sampleData.put((databuff[c.VADC][0][i], 0 + i * c.BETWEEN_TIME)) # 39.1
        self.sec = (self.sec + 1) % 10

    def start(self):
        self.t.start()

    def stop(self):
        self.t.cancel()


class TestData:
    # exitFlag = False
    sec = 0

    def __init__(self):
        self.stTime = 0

    def activate(self):
        self.sample()
        self.t = pyth.Timer(c.FREQ_OF_SAMPLE, self.activate)
        self.t.start()
        self.stTime = time.perf_counter()

    def sample(self):
        databuff = []
        for i in range(c.SAMP_PER_CALL):
            databuff.append(i * 255 / c.SAMP_PER_CALL)
            # databuff.append(np.random.randint(255))
            # databuff.append(0)

        for i in range(c.SAMP_PER_CALL):
            t = c.bill * self.sec * c.FREQ_OF_SAMPLE + 0 + i * c.BETWEEN_TIME
            # Stores time in nanoseconds
            sampleData.put((databuff[i], t))
        self.sec = (self.sec + 1) % 250

    def start(self):
        self.t = pyth.Timer(c.FREQ_OF_SAMPLE, self.activate)
        self.t.start()

    def stop(self):
        self.t.cancel()
