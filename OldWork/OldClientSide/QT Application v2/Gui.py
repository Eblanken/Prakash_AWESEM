# This class generates the responsive UI capabilities of the application
# and acts as the main starter for all other threads

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from QTD_Window import Ui_MainWindow
import ProjectConstants as c
import Data as data

class GUI(QMainWindow):
    startScanning = pyqtSignal()
    endScanning = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.scanA = c.IMG.copy(0, 0, c.defw, c.defh)
        self.scanPixmap = QPixmap()
        self.scanLabel = QLabel('Scan Area', self)
        self.scanLabel.setFixedWidth(c.defw)
        self.scanLabel.setFixedHeight(c.defh)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.drawImage()
        self.showGivenImage(self.scanA)
        self.scanLabel.move(50, 90)
        self.scanLabel.show()
        self.connectUI()

    def showGivenImage(self, image):
        self.scanPixmap.convertFromImage(image)
        self.scanLabel.setPixmap(self.scanPixmap)
        return

    def drawImage(self):
        p = QPainter()
        p.begin(self.scanA)
        p.setPen(QColor(0, 0, 0, 250))
        for i in range(c.defw):
            for j in range(c.defh):
                p.drawPoint(i, j)
        p.end()
        return

    def connectUI(self):
        self.ui.ScanB.clicked.connect(self.toggleScanning)

    def toggleScanning(self, active):
        if active:
            self.startScanning.emit()
        else:
            self.endScanning.emit()

    def saystuff(self, val):
        print("HI")
