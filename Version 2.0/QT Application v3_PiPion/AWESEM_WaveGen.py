#
# File: AWESEM_WaveGen.py
# ------------------------------
# Author: Brion Ye
# Date:
#
# Description:
#   This class starts the waveform generator in the
#   teensy 3.6 MCU board.
#   It also holds several useful functions to generate
#   waveforms and analyze waveforms, and if necessary it
#   will generate the LUT for data conversion.
#
# Edits:
#  - Erick Blankenberg, adapted to use teensy 3.6.
#

import numpy as np
from   scipy.interpolate import InterpolatedUnivariateSpline as UVS
import AWESEM_Data as Data
from   AWESEM_PiPion_Interface import AWESEM_PiPion_Interface
import AWESEM_Constants as Const

# UZPOut Class:
# 

class WavGen:
    MCUInterface
    # Performs necessary setup operations to prepare
    # the waveform generators.
    def __init__(self, PiPionInterface):
        self.MCUInterface = PiPionInterface
        self.MCUInterface.setDacWaveform(0, Const.XWave)
        self.MCUInterface.setDacWaveform(1, Const.YWave)
        self.MCUInterface.setDacFrequency(0, Const.XHz)
        self.MCUInterface.setDacFrequency(1, Const.YHz)
        self.MCUInterface.setDacMagnitude(0, Const.XMag)
        self.MCUInterface.setDacMagnitude(1, Const.YMag)
        self.generateLUT()

    # Generates the lookup tables for possible usage in the display thread
    @staticmethod
    def generateLUT():
        xcors = AWESEM_Waveout.mTria(Const.waveRes, Const.defw)
        xtval = AWESEM_Waveout.mSawt(Const.waveRes, Const.bill / Const.XHz)
        data.LUTX = UVS(xtval, xcors, None, [None, None], 1)

        ycors = AWESEM_Waveout.mSawt(Const.waveRes, Const.defh)
        ytval = AWESEM_Waveout.mSawt(Const.waveRes, Const.bill / Const.YHz)
        data.LUTY = UVS(ytval, ycors, None, [None, None], 1)

    # Returns a list of size numS that traces one period of a sine wave
    # (lowest pt at 0, highest pt at amp)
    @staticmethod
    def mSine(numS, amp):
        samples = []
        for i in range(numS):
            j = (amp / 2 * np.sin((i * 2 * Const.pi) / numS) + amp / 2)
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
        print("Check Data file, start is unified") # TODO maybe seperate ADC sampling and DAC out in the PiPion

    # Stops the waveform generators
    def stopGen(self):
         print("Check Data file, stop is unified") # TODO see above
