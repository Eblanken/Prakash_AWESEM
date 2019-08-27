# This class generates the responsive UI capabilities of the application

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from QTD_Window import Ui_MainWindow
import ProjectConstants as c
from time import perf_counter


# GUI Class:
# This class creates the actual GUI of the application
# and connects all the signals to their appropriate
# slots in the other threads.
# It gets significant help from the QTD_Window file.
# ...

class GUI(QMainWindow):
    startScanning = pyqtSignal()
    endScanning = pyqtSignal()

    # Nothing much to say, this creates the UI.
    def __init__(self):
        super().__init__()
        self.scanA = c.IMG.copy(0, 0, c.defw, c.defh)
        self.scanPixmap = QPixmap()
        self.scanLabel = QLabel('Scan Area', self)
        self.scanLabel.setFixedWidth(c.defw)
        self.scanLabel.setFixedHeight(c.defh)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showGivenImage(self.scanA)
        self.scanLabel.move(50, 90)
        self.scanLabel.show()
        self.connectUI()

    # Connect all the signals and slots
    def connectUI(self):
        self.ui.ScanB.clicked.connect(self.toggleScanning)

    # Slot to show the image given by display thread
    def showGivenImage(self, image):
        b = perf_counter()
        self.scanPixmap.convertFromImage(image)
        self.scanLabel.setPixmap(self.scanPixmap)
        print("Update Pixmap:", perf_counter() - b)
        return

    # Connects Scan button to Main.py's startScanning and endScanning
    def toggleScanning(self, active):
        if active:
            self.startScanning.emit()
        else:
            self.endScanning.emit()
