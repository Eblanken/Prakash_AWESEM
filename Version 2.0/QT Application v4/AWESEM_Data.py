#
# File: AWESEM_Data.py
# ------------------------------
# Author: Brion Ye
# Date:
#
# Description:
#   This class takes the input data and stores it in a queue.
#   This class houses a python timer thread (NOT QThread).
#   When called periodically it "polls" data points with
#   timestamps and adds them to the data queue to be
#   processed by the display thread. 
#
# Edits:
#  - Erick Blankenberg, Adapted to use teensy 3.6.
#

import threading as pyth
from collections import deque
from AWESEM_PiPion_Interface import AWESEM_PiPion_Interface
import AWESEM_Constants as Const

sampleData = deque(maxlen=250500)

class DataIn:
    def __init__(self, PiPionInterface):
        # super().__init__()
        self._MCUInterface = PiPionInterface
        self._MCUInterface.setAdcFrequency(Const.ADC_SAMPLEFREQUENCY)
        self._SampleTimer = pyth.Timer(Const.DISPLAY_POLLPERIOD, self.sample)

    def sample(self):
        self._SampleTimer = pyth.Timer(Const.DISPLAY_POLLPERIOD, self.sample)
        self._SampleTimer.start() # TODO code stink here, why do new samples need to create new instances of themselves?
        value = self._MCUInterface.getDataBuffer()
        if value is not None:
            sampleData.append(value) # TODO numpy may have methods? Faster to enqueue all rows or to enqueue blocks
        #print("Data: Buffer size: %d" % len(sampleData))
        
    def start(self):
        print("Data: Started")
        self._SampleTimer = pyth.Timer(Const.DISPLAY_POLLPERIOD, self.sample)
        self._SampleTimer.start()
        self._MCUInterface.beginEvents()

    def stop(self):
        print("Data: Stopped")
        self._SampleTimer.cancel()
        self._MCUInterface.pauseEvents()
