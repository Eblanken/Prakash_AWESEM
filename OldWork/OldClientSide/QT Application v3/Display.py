# The classes in this file process and send scan updates to the GUI

from PyQt5.QtGui import *
from PyQt5.QtCore import *
import ProjectConstants as c
import Data as data
from time import perf_counter
from WaveGen import UZPOut as gen


# Display Class:
# This QThread is called periodically from the main.
# When called it takes some number of samples from the
# queue of intensity values in Data.py and plots them
# onto the class's current scan image.
# Once some number of data points have been processed
# the image is then sent as pyqtSignal that eventually
# gives the updated image to the GUI for presentation.
# ...

class Display(QThread):
    loadedImage = pyqtSignal(QImage)
    ColorsLUT = []

    # Prepares the color LUT (for efficiency)
    # and creates the base image.
    def __init__(self):
        super().__init__()
        self.scanA = c.IMG.copy(0, 0, c.defw, c.defh)
        for i in range(256):
            self.ColorsLUT.append(QColor(i, i, i, 255))

    # Each time the thread is run, it takes some number of
    # data points from the queue and plots them on the
    # scanA image attribute.
    def run(self):
        print("Displaying")
        print(len(data.sampleData))
        testing = perf_counter()

        for i in range(c.PIX_PER_UPDATE):
            # If data queue is empty, break till next call
            try:
                tsvalue = data.sampleData.popleft()
            except:
                break
            t = tsvalue[1]
            v = tsvalue[0]
            # Convert timestamp to x and y coordinate
            plotx = gen.TriaLUT(t % (c.bill / c.XHz), c.defw, c.bill / c.XHz)
            ploty = gen.SawtLUT(t, c.defh, c.bill / c.YHz)
            # Plot the pixel at x and y with input intensity v
            self.scanA.setPixelColor(plotx, ploty, self.ColorsLUT[v])
        print("Generating Image:", perf_counter() - testing)
        print("Finished Image...")
        self.loadedImage.emit(self.scanA)
