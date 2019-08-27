# This file handles waveform generation

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as UVS
import time as time
import Data as data
from UniversalPiAPI import UZP
import ProjectConstants as c


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


# UZPOut Class:
# This class starts the waveform generator in the
# Universal Pi Zero Board (the MCU has its own logic
# so a continuous thread is not necessary in this case).
# It also holds several useful functions to generate
# waveforms and analyze waveforms, and if necessary it
# will generate the LUT for data conversion.
# ...

class UZPOut:
    # Performs necessary setup operations to prepare
    # the waveform generators.
    def __init__(self):
        uzp.DACInit(c.XDAC)
        uzp.DACInit(c.YDAC)
        uzp.DACGenerate(c.XDAC, c.waveRes, self.mSine(c.waveRes, 4096), c.XHz)
        uzp.DACGenerate(c.YDAC, c.waveRes, self.mSawt(c.waveRes, 4096), c.YHz)
        self.generateLUT()

    # Generates the lookup tables for possible usage in the display thread
    @staticmethod
    def generateLUT():
        xcors = UZPOut.mTria(c.waveRes, c.defw)
        xtval = UZPOut.mSawt(c.waveRes, c.bill / c.XHz)
        data.LUTX = UVS(xtval, xcors, None, [None, None], 1)

        ycors = UZPOut.mSawt(c.waveRes, c.defh)
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

    # Returns a list of size numS that
    # traces a triangular wave from 0 to amp
    @staticmethod
    def mTria(numS, amp):
        samples = []
        for i in range(int(numS / 2)):
            samples.append(2 * amp * i / numS)
        for i in range(int(numS / 2)):
            samples.append(amp - 2 * amp * i / numS)
        return samples

    # Emulates an LUT by "reversing" the triangle wave.
    # Given input time, time domain, and amplitude of wave,
    # it returns the position value of the wave at that point.
    @staticmethod
    def TriaLUT(inp, amp, domain):
        if inp < domain / 2:
            return 2 * amp * inp / domain
        else:
            return amp - 2 * amp * (inp - domain / 2) / domain

    # Emulates an LUT by "reversing" the sawtooth wave.
    # Given input time, time domain, and amplitude of wave,
    # it returns the position value of the wave at that point.
    @staticmethod
    def SawtLUT(inp, amp, domain):
        return amp * inp / domain

    # Starts the waveform generators and records the start time
    # to allow for syncing with the data thread.
    def startGen(self):
        uzp.DACStart(c.XDAC)
        uzp.DACStart(c.YDAC)
        globals().inittime = time.perf_counter()

    # Stops the waveform generators
    def stopGen(self):
        uzp.DACStop(c.XDAC)
        uzp.DACStop(c.YDAC)
