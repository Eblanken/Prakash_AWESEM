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
    _MCUInterface
    _SampleTimer

    def __init__(self, PiPionInterface):
        # super().__init__()
        self._MCUInterface = PiPionInterface
        self._MCUInterface.setAdcFrequency() # TODO
        self._SampleTimer = pyth.Timer(Const.FREQ_OF_SAMPLE, self.sample)

    def sample(self):
        sampleData.put(MCUInterface.getDataBuffer()) # TODO numpy may have methods? Faster to enqueue all rows or to enqueue blocks?

    def start(self):
        self._SampleTimer.start()
        MCUInterface.beginEvents()

    def stop(self):
        self._SampleTimer.cancel()
        MCUInterface.pauseEvents()
