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


class master(QObject):
    startScanning = pyqtSignal()
    endScanning = pyqtSignal()
    sendImage = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.window = gui.GUI()
        self.displayTh = display.display()
        self.dataTh = data.TestData()

        WaveGen.UZPOut.generateLUT()

        # self.datatimer = QTimer()
        # self.datatimer.setInterval(10)
        # self.datatimer.timeout.connect(self.dataTh.start)

        self.disptimer = QTimer()
        self.disptimer.setInterval(c.PERIOD_OF_DISP)
        self.disptimer.timeout.connect(self.displayTh.start)

        self.window.startScanning.connect(self.startScans)
        self.window.endScanning.connect(self.endScans)
        self.displayTh.loadedImage.connect(self.relayImage)
        # self.dataTh.loadedImage.connect(self.relayImage)
        self.sendImage.connect(self.window.showGivenImage)

        self.window.show()
        sys.exit(self.app.exec_())

    def relayImage(self, image):
        print("Relaying Image")
        self.sendImage.emit(image)
        return

    def startScans(self):
        self.disptimer.start()
        self.dataTh.start()

    def endScans(self):
        self.disptimer.stop()
        self.dataTh.stop()

    def saystuff(self):
        print("HI")


if __name__ == "__main__":
    c = master()
