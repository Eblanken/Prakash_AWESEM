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
# Edits:
#  - Erick Blankenberg, adapted to use teensy 3.6, moved temp image here. Switched to mpipe
#  - Was originally the display thread, divided point assignment and display assignment into two threads
#
# TODO:
#  - How to cleanly handle output so that it is easy to save to file,
#  - might be better ways to use NUMPY arrays to work faster
#  - might be better
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
    # Data processing
    __DataTranslateX              = None
    __DataTranslateY              = None
    __InputBuffer                 = None
    __StandardCallback            = None
    __AlternateCallback           = None
    __AlternateCallbackNumbuffers = 0

    def __init__(self, inputQueue, outputCallback):
        threading.Thread.__init__(self)
        self.__InputBuffer    = inputQueue
        self.__OutputCallback = outputCallback

    #
    # Description:
    #   As per the mpipe interface doTask runs whenever the stage has data to
    #   distribute.
    #
    def run(self):
        while True:
            if(len(self.__InputBuffer) > 0):
                print(len(self.__InputBuffer) )
                newestBuffer = self.__InputBuffer.popleft()
                assignedPositionVals = self.registerPoints(newestBuffer)
                if(self.__AlternateCallbackNumbuffers > 0 and callable(self.__AlternateCallback)):
                    self.__AlternateCallbackNumbuffers = self.__AlternateCallbackNumbuffers - 1
                    self.__AlternateCallback(newestBuffer)
                    if(self.__AlternateCallbackNumbuffers <= 0):
                        self.__AlternateCallback = None
                else:
                    self.__OutputCallback(assignedPositionVals)

    #
    # Description:
    #   Assigns screen coordinate locations to the given sample data block.
    #
    # Parameters:
    #   'newestBuffer'  Buffer of the format: (aTimestamp, bTimestamp, value (byte); ... ; ...)
    #   'functionX'     Callback to translate timestamps in microseconds to position, if specified overrides internal function
    #   'functionY'     Callback to translate timestamps in microseconds to position, if specified overrides internal function
    #
    def registerPoints(self, newestBuffer, functionX = None, functionY = None):
        # Checks defaults
        if functionX is None:
            functionX = self.__DataTranslateX
        if functionY is None:
            functionY = self.__DataTranslateY

        # Applies translation function
        #print(newestBuffer)
        assignedPositionVals = numpy.stack((functionX(newestBuffer[:, 0] / 1000000), functionY(newestBuffer[:, 1] / 1000000), newestBuffer[:, 2]), 1).astype(int)
        #print(assignedPositionVals)
        # Merges duplicate coordinates
        numpy_indexed.group_by(assignedPositionVals[:, [0, 1]]).mean(assignedPositionVals)
        #print(assignedPositionVals)
        return assignedPositionVals

    #
    # Desccription:
    #   Sets the function used to translate the data times to position
    #   along the X axis.
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
    #
    # Desccription:
    #   Sets the function used to translate the data times to position
    #   along the Y axis.
    #
    # Parameters:
    #   'translationFunction' Function that takes in a floating point time in seconds
    #                         and returns a floating point normalized value, 1.0 is maximum.
    #
    def setDataTranslateY(self, translationFunction):
        if(callable(translationFunction)):
            self.__DataTranslateY = translationFunction
            return True
        return False
