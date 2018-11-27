# This class takes the input data and stores it in a queue

import threading as pyth
from collections import deque
from UniversalPiAPI import UZP
import ProjectConstants as c

# implement SPI interface with the Universal Pi Board and do I/O

sampleData = deque(maxlen=250500)
inittime = 0
LUTX = None
LUTY = None


# filler Class:
# Basic irrelevant class to allow the code to compile
# on a Windows OS where spidev and thus UZP don't work
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

# UZPIn Class [INCOMPLETE]:
# This class houses a python timer thread (NOT QThread).
# When called periodically it "polls" data points with
# timestamps and adds them to the data queue to be
# processed by the display thread. This is the data class
# intended for use with the Universal Pi Zero Board's ADCs.
# ...

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
            # sampleData.put((databuff[c.VADC][0][i], 0 + i * c.BETWEEN_TIME))
            pass
        self.sec = (self.sec + 1) % 10

    def start(self):
        self.t.start()

    def stop(self):
        self.t.cancel()


# TestData Class:
# This class houses a python timer thread (NOT QThread).
# When called periodically it "polls" data points with
# timestamps and adds them to the data queue to be
# processed by the display thread. This is the testing
# version of the class as it generates its own input
# instead of reading from an ADC.
# ...

class TestData:
    sec = 0
    subsection = 0

    # Sort of like a recursive function, calls itself
    # repeatedly using the threading.Timer, with each call
    # activating the sample() function.
    def activate(self):
        self.sample()
        self.t = pyth.Timer(1 / c.FREQ_OF_SAMPLE, self.activate)
        self.t.start()

    # "Polls" a bunch of data points and puts them into the queue
    # along with timestamps for each data point.
    # [In this test class the sample function also creates the data].
    def sample(self):
        databuff = []
        for i in range(c.SAMP_PER_CALL):
            databuff.append(i * 255 / c.SAMP_PER_CALL)
            # databuff.append(np.random.randint(255))
            # databuff.append(0)

        for i in range(c.SAMP_PER_CALL):
            t = c.bill * self.sec + c.bill * self.subsection / c.XHz + 0 + i * c.BETWEEN_TIME
            sampleData.append((int(databuff[i]), t))

        if len(sampleData) > 250000:
            sampleData.clear()

        self.subsection += 1
        if self.subsection == c.FREQ_OF_SAMPLE:
            self.sec = (self.sec + 1) % (1 / c.YHz)
            self.subsection = 0

    # Starts the activate function
    def start(self):
        self.t = pyth.Timer(1 / c.FREQ_OF_SAMPLE, self.activate)
        self.t.start()

    # Stops the activate function and the data taking
    def stop(self):
        self.t.cancel()
