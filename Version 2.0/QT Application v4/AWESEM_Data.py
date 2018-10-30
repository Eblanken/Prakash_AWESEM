#
# File: AWESEM_Data.py
# ------------------------------
# Author: Brion Ye, Erick Blankenberg
# Date: 10/10/2018
#
# Description:
#   This class takes the input data and stores it in a queue.
#   This class houses a python timer thread (NOT QThread).
#   When called periodically it "polls" data points with
#   timestamps and adds them to the data queue to be
#   processed by the display thread.
#
#   Polling based off of: https://stackoverflow.com/a/28034554
#
# TODO:
#   Need to check threads behavior on a single core processor
#
# Edits:
#  - Erick Blankenberg, Adapted to use teensy 3.6, used new polling.
#

import time
import mpipe
import threading
from   collections             import deque
from   AWESEM_PiPion_Interface import AWESEM_PiPion_Interface
import AWESEM_Constants        as     Const

class DataIn(threading.Thread):
    __PipeOut      = None
    __PollPeriod   = None
    __MCUInterface = None
    __DoSample     = False

    def __init__(self, MCUInterface, PipeOut):
        threading.Thread.__init__(self)
        self.__MCUInterface = MCUInterface
        self.__PipeOut      = PipeOut

    def setPollFrequency(self, newPollFrequency):
        self.__PollPeriod = 1.0 / float(newPollFrequency)
        return True

    def run(self):
        def g_tick():
            t = time.time()
            count = 0
            while True:
                count += 1
                yield max(t + count * self.__PollPeriod - time.time(), 0)
        while True: # Feels bad, better than threading maybe?
            if self.__DoSample:
                g = g_tick()
                time.sleep(next(g))
                value = None
                while value is None and self.__DoSample:
                    # As per MPipe's docs, if you return None that shuts down the pipeline, dont do this
                    value = self.__MCUInterface.getDataBuffer()
                    if value is not None and self.__PipeOut is not None:
                        print("Placed")
                        self.__PipeOut.put(value)

    def halt(self):
        self.__DoSample = False

    def commence(self):
        self.__DoSample = True
