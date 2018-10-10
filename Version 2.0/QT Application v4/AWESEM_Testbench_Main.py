#
# File: AWESEM_Testbench_Main.py
# ------------------------------
# Author: Erick Blankenberg
# Date: 9/28/2018
#
# Description:
#   This class starts the application and ties
#   everything together.
#
#   To successfully run this application
#   download the following: Anaconda
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

class Master(QObject):
    
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

# The all important main function OwO
if __name__ == "__main__":
    Const = Master()
