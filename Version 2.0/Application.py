import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from scanArea import scanArea
from Data import AnalogData as input

defw = 1000
defh = 600


class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.scanA = QImage('Yellow_BG.JPG')
        self.scanPixmap = QPixmap()
        self.scanLabel = QLabel('Scan Area', self)
        self.initUI()

    r = 0
    g = 0
    b = 0

    def showImage(self):
        self.scanPixmap.convertFromImage(self.scanA)
        self.scanLabel.setPixmap(self.scanPixmap)
        return

    def drawImage(self):
        p = QPainter()
        p.begin(self.scanA)
        # p.fillRect(0, 0, 500, 500, QColor(self.r, self.g, self.b, 250))
        p.setPen(QColor(self.r, self.g, self.b, 250))
        for i in range(500):
            for j in range(500):
                p.drawPoint(i, j)
        self.r = (self.r + 40) % 255
        self.g = (self.g + 40) % 255
        self.b = (self.b + 40) % 255
        p.end()
        return

    def updateImage(self):
        for i in range(50):
            self.drawImage()
            self.showImage()

    def initUI(self):
        self.drawImage()
        self.showImage()
        self.scanLabel.move(50, 50)
        self.scanLabel.show()

        self.drawImage()
        self.showImage()

        quitb = QPushButton('Quit', self)
        quitb.clicked.connect(QApplication.instance().quit)
        quitb.resize(quitb.sizeHint())
        quitb.move(defw-150, 60)

        scanb = QPushButton('Start Scan', self)
        scanb.clicked.connect(self.updateImage)

        scanb.resize(scanb.sizeHint())
        scanb.move(defw - 150, 120)

        self.setFixedWidth(defw)
        self.setFixedHeight(defh)
        self.setWindowTitle('SEM Visualization Demo')
        self.show()

    def startScan(self):
        return
    def stopScan(self):
        return
    def saystuff(self):
        print("Button was clicked")
        return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Application()
    sys.exit(app.exec_())