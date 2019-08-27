#
# File: AWESEM_Display.py
# ------------------------------
# Author: Brion Ye
# Date:
#
# Description:
#   This QThread is called periodically from the main.
#   When called it takes some number of samples from the
#   queue of intensity values in Data.py and plots them
#   onto the class's current scan image.
#   Once some number of data points have been processed
#   the image is then sent as pyqtSignal that eventually
#   gives the updated image to the GUI for presentation.
#
# Edits:
#  - Erick Blankenberg, adapted to use teensy 3.6.
#

import threading as pyth
from   math import ceil
from   PyQt5.QtGui import *
from   PyQt5.QtCore import *
import numpy as np
import AWESEM_Constants as Const
import AWESEM_Data as Data
from   AWESEM_WaveGen import WaveGen
from time import perf_counter

class Display(QThread):
    loadedImage = pyqtSignal(QImage)
    ColorsLUT = []
    TempPointsDict = dict() # Format is (x, y):[sumElems, numElems]

    # Prepares the color LUT (for efficiency)
    # and creates the base image.
    def __init__(self):
        super().__init__()
        self.scanA = Const.IMG.copy(0, 0, Const.defw, Const.defh)
        self._LoadTimer = pyth.Timer(Const.ADC_POLLPERIOD, self.run)
        for i in range(257):
            self.ColorsLUT.append(QColor(i, i, i, 255))

    # Each time the thread is run, it plots all available data
    def load(self):
        self._LoadTimer = pyth.Timer(Const.ADC_POLLPERIOD, self.load)
        self._LoadTimer.start() # TODO code stink here
        if (len(Data.sampleData) > 0):
            #print("Display: Loading %d" % (len(Data.sampleData)))
            # Loads bulk data
            while(True):
                try:
                    valueBlock = Data.sampleData.pop()
                except:
                    break
                np.apply_along_axis(self._logPoints, 1, valueBlock)
            # Moves to display
            for currentKey in self.TempPointsDict:
                currentValues = self.TempPointsDict[currentKey]
                self.scanA.setPixelColor(currentKey[0], currentKey[1], self.ColorsLUT[int(ceil(currentValues[0] / currentValues[1]))])
            self.TempPointsDict.clear()
            self.loadedImage.emit(self.scanA)
            #print("Display: Updated display")
        #else:
            #print("Display: No Data")
    
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
        plotx = round(WaveGen.SawtLUT(dataRow[0], Const.defw, Const.mill / Const.XHz))
        ploty = round(WaveGen.SawtLUT(dataRow[1], Const.defh, Const.mill / Const.YHz))
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
            
    def start(self):
        print("Display: Started")
        self._LoadTimer = pyth.Timer(Const.ADC_POLLPERIOD, self.load)
        self._LoadTimer.start()

    def stop(self):
        print("Display: Stopped")
        self._LoadTimer.cancel()
