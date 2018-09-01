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

from   PyQt5.QtGui import *
from   PyQt5.QtCore import *
import numpy as np
import AWESEM_Constants as Const
import AWESEM_Data as Data
from   AWESEM_WaveGen import WaveGen

class Display(QThread):
    loadedImage = pyqtSignal(QImage)
    ColorsLUT = []
    TempPointsDict = {} # Format is (x, y):[sumElems, numElems]

    # Prepares the color LUT (for efficiency)
    # and creates the base image.
    def __init__(self):
        super().__init__()
        self.scanA = Const.IMG.copy(0, 0, Const.defw, Const.defh)
        for i in range(256):
            self.ColorsLUT.append(QColor(i, i, i, 255))

    # Each time the thread is run, it plots all available data
    def run(self):
        print("Displaying")
        print(len(data.sampleData))
        testing = perf_counter()

        # Loads bulk data
        while(True):
            try:
                valueBlock = Data.sampleData.popleft()
            except:
                break
            np.apply_along_axis(self._logPoints, 0, valueBlock)
        
        # Moves to display
        for currentKey in TempPointsDict:
            currentValues = TempPointsDict[currentKey]
            self.scanA.setPixelColor(currentKey(0), currentKey(1), self.ColorsLUT[currentValues(0) / currentValues(1)])
        TempPointsDict.clear()
        
        print("Generating Image:", perf_counter() - testing)
        print("Finished Image...")
        self.loadedImage.emit(self.scanA)
    
    #
    # Description:
    #   Takes in data point of the format [(xTime), (yTime), (value)] and logs
    #   this data point to the corresponding location in an image 
    #   update data structure.
    #
    def _logPoints(dataRow):
        # TODO this whole thing seems really inefficient, may be way to generate tons of LUT values
        # at once more quickly or maybe better way to log values to dictionary or maybe there is
        # a better alternative to a dictionary altogether. I am not sure how efficient dictionaries are, especially when adding lots of new keys.
        plotx = WaveGen.TriaLUT(dataRow(1) % (Const.bill / Const.XHz), Const.defw, Const.bill / Const.XHz)
        ploty = WaveGen.SawtLUT(dataRow(2), Const.defh, Const.bill / Const.YHz)
        oldVals = TempPointsDict[(plotx, ploty)]
        newVals = [dataRow(3), 1]
        if oldVals is not None:
            newVals(0) += oldVals(0)
            newVals(1) += oldVals(1)
        TempPointsDict[(plotx, ploty)] = newVals
            
