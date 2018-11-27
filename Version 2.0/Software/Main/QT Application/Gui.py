# This class generates the responsive UI capabilities of the application
# and acts as the main starter for all other threads

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from QTD_Window import Ui_MainWindow

class GUI(QMainWindow):
    startScanning = pyqtSignal()
    endScanning = pyqtSignal()
    defw = 1000
    defh = 600

    def __init__(self):
        super().__init__()
        self.scanA = QImage('Yellow_BG.JPG')
        self.scanPixmap = QPixmap()
        self.scanLabel = QLabel('Scan Area', self)
        self.scanLabel.setFixedSize(500, 500)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.drawImage()
        self.showImage()
        self.scanLabel.move(50, 90)
        self.scanLabel.show()
        self.connectUI()

    def showImage(self):
        self.scanPixmap.convertFromImage(self.scanA)
        self.scanLabel.setPixmap(self.scanPixmap)
        return

    def showGivenImage(self, image):
        self.scanPixmap.convertFromImage(image)
        self.scanLabel.setPixmap(self.scanPixmap)
        return

    def drawImage(self):
        p = QPainter()
        p.begin(self.scanA)
        p.setPen(QColor(0, 0, 0, 250))
        for i in range(500):
            for j in range(500):
                p.drawPoint(i, j)
        p.end()
        return

    def updateImage(self):
        for i in range(10):
            self.drawImage()
            self.showImage()

    def connectUI(self):
        self.ui.ScanB.clicked.connect(self.toggleScanning)

    def toggleScanning(self, active):
        if active:
            self.startScanning.emit()
        else:
            self.endScanning.emit()

    def saystuff(self, val):
        print("HI")
