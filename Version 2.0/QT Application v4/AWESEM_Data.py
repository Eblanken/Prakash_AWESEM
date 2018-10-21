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
# Edits:
#  - Erick Blankenberg, Adapted to use teensy 3.6.
#

import threading               as     pyth
from   collections             import deque
from   AWESEM_PiPion_Interface import AWESEM_PiPion_Interface
import AWESEM_Constants        as     Const

class DataIn:
    
    __SampleTimer  = None
    __SampleBuffer = deque(maxlen=250500)
    __PollPeriod   = None
    __MCUInterface = None
    
    def __init__(self, MCUInterface, OutputPointsQueue):
        self.__MCUInterface = MCUInterface
    
    def getQueueLength(self):
        return len(self.__SampleBuffer)
    
    def getQueuePop(self):
        return self.__SampleBuffer.pop()
    
    def setInputMCUInterface(self, newMCUInterface):
        if isinstance(newMCUInterface, AWESEM_PiPion_Interface):
            self.__MCUInterface = newMCUInterface
            return True
        return False
    
    def setPollFrequency(self, newPollFrequency):
        self.__PollPeriod = 1.0 / float(newPollFrequency)
        return True    
    
    def sample(self):
        self.__SampleTimer = pyth.Timer(self.__PollPeriod, self.sample)
        self.__SampleTimer.start() # TODO code stink here, why do new samples need to create new instances of the sample timer?
        value = self.__MCUInterface.getDataBuffer()
        if value is not None:
            self.__SampleBuffer.append(value) # TODO numpy may have methods? Faster to enqueue all rows or to enqueue blocks
        #print("Data: Buffer size: %d" % len(sampleData))
        
    def start(self):
        if(self._checkReady):
            print("Data: Started")
            self._SampleTimer = pyth.Timer(self.__PollPeriod, self.sample)
            self._SampleTimer.start()
            self._MCUInterface.beginEvents()

    def stop(self):
        print("Data: Stopped")
        self._SampleTimer.cancel()
        self._MCUInterface.pauseEvents()
        
    def _checkReady(self):
        if not isinstance(self.__MCUInterface, AWESEM_PiPion_Interface):
            print("ERROR: Data: MCU Interface not valid")
            return False
        elif not isinstance(self.__PollPeriod, float):
            print("ERROR: Data: Frequency is invalid")
            return False
        elif not self.__MCUInterface.ping():
            print("ERROR: Data: MCU not responding")
            return False
        return True
            
        
