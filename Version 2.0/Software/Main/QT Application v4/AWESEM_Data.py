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
import threading
import numpy
from   collections             import deque
from   AWESEM_PiPion_Interface import AWESEM_PiPion_Interface
import AWESEM_Constants        as     Const

class DataIn(threading.Thread):
    __OutQueue           = None
    __PollPeriod         = None
    __MCUInterface       = None
    __DoSample           = False
    __InternalQueue      = deque(maxlen = 50)
    __InternalNumCollect = 0

    def __init__(self, MCUInterface, outputQueue):
        threading.Thread.__init__(self)
        self.__MCUInterface = MCUInterface
        self.__OutQueue     = outputQueue

    def setPollFrequency(self, newPollFrequency):
        self.__PollPeriod = 1.0 / float(newPollFrequency)
        return True

    """
    def run(self):
        def g_tick():
            t = time.time()
            count = 0
            while True:
                count += 1
                yield max(t + count * self.__PollPeriod - time.time(), 0)
        while True: # Feels bad, better than threading maybe?
            if self.__DoSample or self.__InternalNumCollect > 0:
                g = g_tick()
                time.sleep(next(g))
                value = None
                while value is None and self.__DoSample:
                    value = self.__MCUInterface.getDataBuffer()
                    if value is not None:
                        if self.__InternalNumCollect > 0: # Happens if redirected by acquireNBuffers
                            self.__InternalNumCollect = self.__InternalNumCollect - 1
                            self.__InternalQueue.append(value)
                        if self.__DoSample and self.__OutQueue is not None:
                            self.__OutQueue.append(value)
    """
    
    def run(self):
        while True: # Feels bad, better than threading maybe?
            if self.__DoSample or self.__InternalNumCollect > 0:
                value = None
                while value is None and self.__DoSample:
                    value = self.__MCUInterface.getDataBuffer()
                    if value is not None:
                        #if self.justHalted < 4:
                        #    self.justHalted = self.justHalted + 1
                        #    if self.justHalted > 3:
                        #        self.justHalted = 10
                        #        print(value[0, :])
                        if self.__InternalNumCollect > 0: # Happens if redirected by acquireNBuffers
                            self.__InternalNumCollect = self.__InternalNumCollect - 1
                            self.__InternalQueue.append(value)
                        if self.__DoSample and self.__OutQueue is not None:
                            self.__OutQueue.append(value)
    
    #
    # Description:
    #   Acquires N buffers into a single numpy array.
    #   Currently set up to run in parrallel with standard acquisition. If we
    #   are acquiring live also saves values here. If paused then will still take
    #   the desired number of samples.
    #
    def acquireNBuffers(self, numBuffers):
        print("acquireNBuffers not fully implemented")
        """
        self.__InternalNumCollect = numBuffers
        sampleLen = self.__MCUInterface.getBufferSize()
        outputArray = numpy.empty((numBuffers * sampleLen), 3) # Format is (aTime, bTime, value (byte); ... ; ...)
        for index in range(0, numBuffers):
            while not (len(self.__InternalQueue.size()) > 0):
                time.sleep(0.01)
            outputArray[(index * sampleLen:(index + 1) * sampleLen), :] = self.__InternalQueue.popleft()
        return outputArray
        """

    #
    # Descriptition:
    #   Stops acquiring sample blocks for continous streaming.
    #
    def halt(self):
        self.justHalted = 0 # TODO debug thingy please kill me
        self.__DoSample = False

    #
    # Description:
    #   Starts acquiring sample blocks for continuous streaming.
    #
    def commence(self):
        self.justHalted = 0
        self.__DoSample = True
