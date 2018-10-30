#
# File: AWESEM_Register.py
# ------------------------------
# Authors: Brion Ye, Erick Blankenberg
# Date: 10/10/2018
#
# Description:
#   This thread continuously assigns intensity data acquired from the
#   teensy to normalized coordinates [0, 1] based on the given reconstruction
#   method.
#
# Edits:
#  - Erick Blankenberg, adapted to use teensy 3.6, moved temp image here. Switched to mpipe
#  - Was originally the display thread, divided point assignment and display assignment into two threads
#
# TODO:
#  - How to cleanly handle output so that it is easy to save to file, currently
#    saves directly to monior.
#

import mpipe
from   math             import ceil
import numpy            as np
import AWESEM_Constants as Const
import AWESEM_Data      as Data
from   time             import perf_counter

class Register(mpipe.OrderedWorker):
    # Data processing
    __DataTranslateX   = None
    __DataTranslateY   = None
    __TempPointsDict   = dict()

    # 
    # Description:
    #   As per the mpipe interface doTask runs whenever the stage has data to
    #   distribute.
    #
    def doTask(task):
        #assignedPositionVals = numpy.stack((self.__DataTranslateX(task[:, 0]), self.__DataTranslateY(task[:, 1]), task[:, 2]), 1)
        print("Sending to callback")
        return 1
        #self.__outputCallback(assignedPositionVals)
    
    def setOutputCallback(self, outputCallbackFuncton):
        self.__outputCallback = outputCallbackFuncton
    
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
            
