#
# File: AWESEM_Display.py
# ------------------------------
# Authors: Brion Ye, Erick Blankenberg
# Date: 10/10/2018
#
# Description:
#   This QThread is called periodically from the main.
#   When called it takes some number of samples from the
#   queue of intensity values in Data.py and plots them
#   onto the class's current scan image.
#   Once some number of data points have been processed
#   the thread will update the image label in the main GUI.
#
# Edits:
#  - Erick Blankenberg, adapted to use teensy 3.6, moved temp image here.
#

import threading        as pyth
from   math             import ceil
from   PyQt5.QtGui      import *
from   PyQt5.QtCore     import *
import numpy            as np
import AWESEM_Constants as Const
import AWESEM_Data      as Data
from   AWESEM_WaveGen   import WaveGen
from   time             import perf_counter

#
# Description:
#   This class 
#
#
#
class Display(QThread):
    # Monitor output
    __DataQueue        = None
    __ScanPixmap       = None
    __LoadTimer        = None
    __ScanMonitorLabel = None
    __ColorsLUT        = []
    # Data processing
    __DataTranslateX   = None
    __DataTranslateY   = None
    __TempPointsDict   = dict() # Format is (x, y):[sumElems, numElems]

    def __init__(self, InputDataSource, OutputViewLabel):
        super().__init__()
        self.__ScanMonitorLabel = OutputViewLabel
        self.__InputDataSource  = InputDataSource
        self.__ScanPixmap       = QPixmap(Const.RES_W, Const.RES_H) # Actual monitor may be larger  
        self.__LoadTimer        = pyth.Timer(Const.ADC_POLLPERIOD, self.run)
        for i in range(257):
            self.ColorsLUT.append(QColor(i, i, i, 255))

    # Each time the thread is run, it plots all available data
    def load(self):
        self._LoadTimer = pyth.Timer(Const.ADC_POLLPERIOD, self.load)
        self._LoadTimer.start() # TODO better version where the thread does not need to restart itself?
        if (self.__InputDataSource.getQueueLength() > 0):
            #print("Display: Loading %d" % (self.__InputDataSource.getQueueLength()))
            # Loads bulk data
            while(self.__InputDataSource.getQueueLength() > 0):
                try:
                    valueBlock = self.__InputDataSource.getQueuePop()
                except:
                    break
                np.apply_along_axis(self._logPoints, 1, valueBlock)
            # Prepares image for display
            for currentKey in self.TempPointsDict:
                currentValues = self.TempPointsDict[currentKey]
                self.scanA.setPixelColor(currentKey[0], currentKey[1], self.ColorsLUT[int(ceil(currentValues[0] / currentValues[1]))])
            self.TempPointsDict.clear()
            self.__ScanMonitorLabel.setPixMap(self.__ScanPixmap.scaled(self.__ScanMonitorLabel.width(), self.__ScanMonitorLabel.height()))
            #print("Display: Updated display")
        #else:
            #print("Display: No Data")
    
    #
    # Desccription:
    #   Sets the function used to translate the data times to position
    #   along the X axis.
    #
    # Parameters:
    #   'translationFunction' Function that takes in a floating point time in seconds
    #                         and returns an integer pixel position.
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
    #                         and returns an integer pixel position.
    #
    def setDataTranslateY(self, translationFunction):
       if(callable(translationFunction)):
            self.__DataTranslateY = translationFunction
            return True
        return False
    
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
            
    # Description
    def start(self):
        if(self._checkReady()):
            print("Display: Started")
            self._LoadTimer = pyth.Timer(Const.ADC_POLLPERIOD, self.load)
            self._LoadTimer.start()

    def stop(self):
        print("Display: Stopped")
        self._LoadTimer.cancel()
        
    def _checkReady(): # TODO FROM HERE
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
