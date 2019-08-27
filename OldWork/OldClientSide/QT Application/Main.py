# This class starts the application and handles everything

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import Data as data
import Display as display
import Gui as gui


class master(QObject):
    startScanning = pyqtSignal()
    endScanning = pyqtSignal()
    sendImage = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.window = gui.GUI()
        self.displayTh = display.display()
        self.dataTh = data.AnalogData()

        self.datatimer = QTimer()
        self.datatimer.setInterval(100)
        self.datatimer.timeout.connect(self.dataTh.start)

        self.disptimer = QTimer()
        self.disptimer.setInterval(2000)
        self.disptimer.timeout.connect(self.displayTh.start)

        self.window.startScanning.connect(self.startScans)
        self.window.endScanning.connect(self.endScans)
        self.displayTh.loadedImage.connect(self.relayImage)
        self.sendImage.connect(self.window.showGivenImage)

        self.window.show()
        sys.exit(self.app.exec_())

    def relayImage(self, image):
        print("Relaying Image")
        self.sendImage.emit(image)
        return

    def startScans(self):
        self.disptimer.start()
        self.datatimer.start()

    def endScans(self):
        self.disptimer.stop()
        self.datatimer.stop()

    def saystuff(self):
        print("HI")


if __name__ == "__main__":
    c = master()
