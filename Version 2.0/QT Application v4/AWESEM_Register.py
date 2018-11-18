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
#  - How to cleanly handle output so that it is easy to save to file, 
#  - might be better ways to use NUMPY arrays to work faster
#  - might be better 
#

import mpipe
from   math             import ceil
import numpy            as np
import AWESEM_Constants as Const
import AWESEM_Data      as Data
from   time             import perf_counter

class Register(threading.Thread):
    # Data processing
    __DataTranslateX              = None
    __DataTranslateY              = None
    __InputBuffer                 = None
    __StandardCallback            = None
    __AlternateCallback           = None
    __AlternateCallbackNumbuffers = 0

    def __init__(self, MCUInterface, inputQueue, standardOutputCallback):
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
                newestBuffer = self.__InputBuffer.popleft()
                print("Recieved")
                assignedPositionVals = numpy.stack((self.__DataTranslateX(newestBuffer[:, 0]), self.__DataTranslateY(newestBuffer[:, 1]), newestBuffer[:, 2]), 1)
                if(self.__AlternateCallbackNumbuffers > 0 and callable(self.__AlternateCallback)):
                    self.__AlternateCallbackNumbuffers = self.__AlternateCallbackNumbuffers - 1
                    self.__AlternateCallback(newestBuffer)
                    if(self.__AlternateCallbackNumbuffers <= 0):
                        self.__AlternateCallback = None
                else:
                    self.__OutputCallback(assignedPositionVals)
    
    #
    # Description:
    #   
    #
    
    #
    # Description:
    #   If the user wants to re-direct processed data to a
    #   different location, they can request numBlocks buffers
    #   be processed by temporaryCallback rather than the standard
    #   callback method. The output will redirect back after this.
    #
    # Parameters:
    #   'numBlocks'         The number of blocks to redirect
    #   'temporaryCallback' The temporary function to use, is reset after
    #
    def setTempAlternateCallback(numBlocks, temporaryCallback):
        self.__AlternateCallbackNumbuffers = numBlocks
        self.__AlternateCallbackNumbuffers = temporaryCallback
    
    def isAlternateDone():
        return (self.__AlternateCallbackNumbuffers > 0)
    
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
            
