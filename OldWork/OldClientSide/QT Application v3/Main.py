# This class starts the application and handles everything

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import Data as data
import Display as display
import Gui as gui
import WaveGen
import ProjectConstants as c


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
        self.app = QApplication(sys.argv)
        self.window = gui.GUI()
        self.displayTh = display.Display()
        self.dataTh = data.TestData()

        WaveGen.UZPOut.generateLUT()

        self.disptimer = QTimer()
        self.disptimer.setInterval(c.PERIOD_OF_DISP)
        self.disptimer.timeout.connect(self.displayTh.start)

        self.window.startScanning.connect(self.startScans)
        self.window.endScanning.connect(self.endScans)
        self.displayTh.loadedImage.connect(self.relayImage)
        self.sendImage.connect(self.window.showGivenImage)

        self.window.show()
        sys.exit(self.app.exec_())

    # Sends Display's image to GUI
    def relayImage(self, image):
        print("Relaying Image")
        self.sendImage.emit(image)
        return

    # Connects GUI's startScanning to running of display and data
    def startScans(self):
        self.disptimer.start()
        self.dataTh.start()

    # Connects GUI's endScanning to stopping of display and data
    def endScans(self):
        self.disptimer.stop()
        self.dataTh.stop()


# The all important main function OwO
if __name__ == "__main__":
    c = Master()
