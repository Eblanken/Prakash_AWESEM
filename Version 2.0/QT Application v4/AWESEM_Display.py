#
# File: AWESEM_Display.py
# ------------------------------
# Authors: Brion Ye, Erick Blankenberg
# Date: 10/10/2018
#
# Description:
#   This thread continuously assigns intensity data acquired from the
#   teensy to the display.
#
# Edits:
#  - Erick Blankenberg, adapted to use teensy 3.6, moved temp image here. Switched to mpipe
#

import mpipe
from   math             import ceil
import numpy            as np
import AWESEM_Constants as Const
import AWESEM_Data      as Data
from   time             import perf_counter

#
# Description:
#   This class 
#
#
#
class Display(mpipe.OrderedWorker):
    # Data processing
    __DataTranslateX   = None
    __DataTranslateY   = None
    __TempPointsDict   = dict()

    # 
    # As per the mpipe interfacem doTask runs whenever the stage has data to
    # distribute.
    #
    def doTask(task):
        assignedPositionVals = numpy.stack((self.__DataTranslateX(task[:, 0]), self.__DataTranslateY(task[:, 1]), task[:, 2]), 1)
        np.apply_along_axis(self._collapseDuplicates, 1, valueBlock)
        # Prepares image for display
        for currentKey in self.TempPointsDict:
            currentValues = self.TempPointsDict[currentKey]
        self.scanA.setPixelColor(currentKey[0], currentKey[1], self.ColorsLUT[int(ceil(currentValues[0] / currentValues[1]))])
        self.TempPointsDict.clear()
    
    #
    # Description:
    #   Takes in data point of the format [(xTime), (yTime), (value)] and logs
    #   this data point to the corresponding location in an image 
    #   update data structure.
    #
    def _logPoints(self, dataRow):
        # TODO this whole thing seems really inefficient, may be way to generate tons of LUT values
        # at once more quickly or maybe better way to log values to dictionary or maybe there is
        # a better alternative to a dictionary altogether. I am not sure how efficient dictionaries are, especially when adding lots of new keys.
        plotx = self.__DataTranslateX(dataRow[0]) #round(WaveGen.SawtLUT(dataRow[0], Const.defw, Const.mill / Const.XHz))
        ploty = self.__DataTranslateY(dataRow[1]) #round(WaveGen.SawtLUT(dataRow[1], Const.defh, Const.mill / Const.YHz))
        #print("Display: Logged %d %d from %d %d" % (plotx, ploty, dataRow[0], dataRow[1]))
        try:
            oldVals = self.TempPointsDict[(plotx, ploty)]
        except:
            oldVals = [0, 0]
        newVals = [dataRow[2], 1]
        if oldVals is not None:
            newVals[0] += oldVals[0]
            newVals[1] += oldVals[1]
        self.TempPointsDict[(plotx, ploty)] = newVals
    
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
            
