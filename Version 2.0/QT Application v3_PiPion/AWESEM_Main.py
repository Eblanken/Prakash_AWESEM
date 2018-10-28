#
# File: AWESEM_Main.py
# ------------------------------
# Author: Brion Ye
# Date:
#
# Description:
#   This class starts the application and ties
#   everything together.
#
#   To successfully run this application
#   download the following: PyQt5, numpy, scipy,
#   UniversalPiAPI, spidev (comes with Linux OS)
#
# Edits:
#  - Erick Blankenberg, adapted to use teensy 3.6.
#

import sys
from   PyQt5.QtWidgets  import *
from   PyQt5.QtGui      import *
from   PyQt5.QtCore     import *
from   AWESEM_PiPion_Interface import AWESEM_PiPion_Interface
import AWESEM_Data      as Data
import AWESEM_Display   as Display
import AWESEM_Gui       as Gui
import AWESEM_WaveGen   as WaveGen
import AWESEM_Constants as Const


# Master Class:
# This class starts the event loop for all the QThreads
# and acts as the medium for all the threads to talk to
# each other.
# ...

class Master(QObject):
    startScanning = pyqtSignal()
    endScanning = pyqtSignal()
    sendImage = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self._MCUInterface = AWESEM_PiPion_Interface();
        self.app           = QApplication(sys.argv)
        self.window        = Gui.GUI(self._MCUInterface)
        self.displayTh     = Display.Display()
        self.dataTh        = Data.DataIn(self._MCUInterface)
        self.waveformTh    = WaveGen.WaveGen(self._MCUInterface)

        WaveGen.WaveGen.generateLUT()

        self.window.startScanning.connect(self.startScans)
        self.window.endScanning.connect(self.endScans)
        self.displayTh.loadedImage.connect(self.relayImage)
        self.sendImage.connect(self.window.showGivenImage)

        self.window.show()
        sys.exit(self.app.exec_())

    # Sends Display's image to GUI
    def relayImage(self, image):
        #print("Main: Relaying Image")
        self.sendImage.emit(image)
        return

    # Connects GUI's startScanning to running of display and data
    def startScans(self):
        print("Main: Starting Scans")
        self.displayTh.start()
        self.dataTh.start()

    # Connects GUI's endScanning to stopping of display and data
    def endScans(self):
        print("Main: Halting Scans")
        self.displayTh.stop()
        self.dataTh.stop()


# The all important main function OwO
if __name__ == "__main__":
    Const = Master()
