import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as UVS
import time as time
import Data as data
from UniversalPiAPI import UZP
from math import floor
import ProjectConstants as c

# This class will be controlling the continuous
# sine/sawtooth waves for the coil generators

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

class UZPOut:
    def __init__(self):
        # super().__init__(self)
        uzp.DACInit(c.XDAC)
        uzp.DACInit(c.YDAC)
        uzp.DACGenerate(c.XDAC, c.waveRes, self.mSine(c.waveRes, 4096), c.XHz)
        uzp.DACGenerate(c.YDAC, c.waveRes, self.mSawt(c.waveRes, 4096), c.YHz)
        self.generateLUT()

    @staticmethod
    def generateLUT():
        xcors = UZPOut.mTria(c.waveRes, c.defw)
        xtval = UZPOut.mSawt(c.waveRes, c.bill / c.XHz)
        for i in range(c.waveRes):
            print(xcors[i], xtval[i])
        # the lookup table is giving out a couple negative numbers...
        data.LUTX = UVS(xtval, xcors, None, [None, None], 1)
        # print(data.LUTX(-100000))
        # for i in range(c.waveRes):
        #     print(data.LUTX(xtval[i]), xtval[i])
        # print(data.LUTX(10000000), 10000000)

        ycors = UZPOut.mSawt(c.waveRes, c.defh + 1)
        ytval = UZPOut.mSawt(c.waveRes, c.bill / c.YHz)
        data.LUTY = UVS(ytval, ycors, None, [None, None], 1)

    # Returns a list of size numS that traces one period of a sine wave
    # (lowest pt at 0, highest pt at amp)
    @staticmethod
    def mSine(numS, amp):
        samples = []
        for i in range(numS):
            j = (amp / 2 * np.sin((i * 2 * c.pi) / numS) + amp / 2)
            samples.append(j)

        return samples

    # Returns a list of size numS that
    # traces a sawtooth wave from 0 to amp
    @staticmethod
    def mSawt(numS, amp):
        samples = []
        for i in range(numS):
            samples.append(amp * i / numS)
        return samples

    @staticmethod
    def mTria(numS, amp):
        samples = []
        for i in range(int(numS / 4)):
            samples.append(amp / 2 + 2 * amp * i / (numS))
            # print(amp / 2 + 2 * amp * i / numS, i)
        for i in range(int(numS / 2)):
            samples.append(amp - 2 * amp * i / numS)
            # print(amp - 2 * amp * i / numS, i+int(numS/4))
        for i in range(int(numS / 4)):
            samples.append(2 * amp * i / numS)
            # print(2 * amp * i / numS, i+int(numS*3/4))
        return samples

    def startGen(self):
        uzp.DACStart(c.XDAC)
        uzp.DACStart(c.YDAC)
        globals().inittime = time.perf_counter()

    def stopGen(self):
        uzp.DACStop(c.XDAC)
        uzp.DACStop(c.YDAC)