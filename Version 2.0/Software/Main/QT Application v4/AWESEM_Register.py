#
# File: AWESEM_Register.py
# ------------------------------
# Authors: Brion Ye, Erick Blankenberg
# Date: 10/10/2018
#
# Description:
#   This thread continuously assigns intensity data acquired from the
#   teensy to integer coordinates based on the given reconstruction
#   method. The internal methods of this class are also exposed so that you can
#   process data outside of the main display pipeline.
#

import threading
import numpy
import numpy_indexed
from   math             import ceil
import numpy            as np
import AWESEM_Constants as Const
import AWESEM_Data      as Data
#from   time             import perf_counter

class Register(threading.Thread):
    __DataTranslateX              = None
    __DataTranslateY              = None
    __DataFilterX                 = None
    __DataFilterY                 = None
    __InputBuffer                 = None
    __StandardCallback            = None
    __xOffset                     = 0.0
    __yOffset                     = 0.0
    __MCUInterface                = None
    __DoSample                    = False
    __doRun                       = True

    """
    def __init__(self, inputQueue, outputCallback):
        threading.Thread.__init__(self)
        self.__InputBuffer    = inputQueue
        self.__OutputCallback = outputCallback
    """
    def __init__(self, outputCallback, MCUInterface):
        threading.Thread.__init__(self)
        self.__OutputCallback = outputCallback
        self.__MCUInterface   = MCUInterface

    #
    # Description:
    #   Translates points and evaluates callback.
    #
    """
    def run(self):
        while True:
            if(len(self.__InputBuffer) > 0):
                self.__OutputCallback(self.registerPoints(self.__InputBuffer.popleft()))
    """

    def run(self):
        while self.__doRun == True:
            if self.__DoSample:
                value = self.__MCUInterface.getDataBuffer()
                if value is not None:
                    self.__OutputCallback(self.registerPoints(value))
    def close(self):
        self.__doRun = False
        
    #
    # Descriptition:
    #   Stops acquiring sample blocks for continous streaming.
    #
    def halt(self):
        self.__DoSample = False

    #
    # Description:
    #   Starts acquiring sample blocks for continuous streaming.
    #
    def commence(self):
        self.__DoSample = True
    #
    # Description:
    #   Assigns screen coordinate locations to the given sample data block.
    #
    # Parameters:
    #   'newestBuffer'  Buffer of the format: (aTimestamp, bTimestamp, value (byte); ... ; ...)
    #   'functionX'     Callback to translate timestamps in microseconds to position, if specified overrides internal function
    #   'functionY'     Callback to translate timestamps in microseconds to position, if specified overrides internal function
    #   'filterX'       Callback to filter timestamps, if specified overrides internal function
    #   'filtery'       Callback to filter timestamps, if specified overrides internal function
    #
    def registerPoints(self, newestBuffer, functionX = None, functionY = None, filterX = None, filterY = None):
        # Checks defaults
        if functionX is None:
            functionX = self.__DataTranslateX
        if functionY is None:
            functionY = self.__DataTranslateY
        if filterX is None:
            filterX = self.__DataFilterX
        if filterY is None:
            filterY = self.__DataFilterY

        # Applies offsets
        newestBuffer[:, 0] = newestBuffer[:, 0] + self.__xOffset;
        newestBuffer[:, 1] = newestBuffer[:, 1] + self.__yOffset;

        # Applies filter function
        boolX = numpy.ones(len(newestBuffer), dtype = bool)
        if filterX is not None:
            boolX = filterX(newestBuffer[:, 0])
        boolY = numpy.ones(len(newestBuffer), dtype = bool)
        if filterY is not None:
            boolY = filterY(newestBuffer[:, 1])
        boolTotal = numpy.logical_and(boolX, boolY)
        newestBuffer = newestBuffer[boolTotal, :]

        if(newestBuffer.size > 0):
            # Applies translation function
            assignedPositionVals = numpy.stack((numpy.round(functionX(newestBuffer[:, 0])), numpy.round(functionY(newestBuffer[:, 1])), newestBuffer[:, 2]), 1).astype(numpy.int16)
            # Merges duplicate coordinates
            numpy_indexed.group_by(assignedPositionVals[:, [0, 1]]).mean(assignedPositionVals)
            return assignedPositionVals
        print("Threw Buffer")
        return None

    #
    # Description:
    #   Filters the given data buffer by timestamps for the given access.
    #
    # Parameters:
    #   'filterFunction' Callback to filter a column array of timestamps in
    #                    milliseconds. Should return a boolean array.
    #                    Set to None to disable filtering.
    #
    def setDataFilterX(self, filterFunction):
        if(callable(filterFunction) or filterFunction is None):
            self.__DataFilterX = filterFunction
            return True
        return False
    def setDataFilterY(self, filterFunction):
        if(callable(filterFunction) or filterFunction is None):
            self.__DataFilterY = filterFunction
            return True
        return False

    #
    # Description:
    #   Adds the given value to the timestamp of the given axis in seconds.
    #
    # Parameters:
    #   'offsetTime' Value to add to the timestamp in seconds.
    #
    def setDataOffsetX(self, offsetTime):
        self.__xOffset = offsetTime
        return True
    def setDataOffsetY(self, offsetTime):
        self.__yOffset = offsetTime
        return True

    #
    # Desccription:
    #   Sets the function used to translate the data times to position
    #   along the specified axis..
    #
    # Parameters:
    #   'translationFunction' Function that takes in a floating point time in seconds
    #                         and returns a floating point normalized value, 1.0 is maximum.
    #
    def setDataTranslateX(self, translationFunction):
        if(callable(translationFunction)):
            self.__DataTranslateX = translationFunction
            return True
        return False

    def setDataTranslateY(self, translationFunction):
        if(callable(translationFunction)):
            self.__DataTranslateY = translationFunction
            return True
        return False
