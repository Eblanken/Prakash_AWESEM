# This class processes the data present in the data storage
# and displays the result in the scanArea

import random
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import Data as data


class display(QThread):
    notCancelling = True
    loadedImage = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()

    def run(self):
        q = QMutexLocker(data.lock)
        # t = random.randint(0, 256)
        t = 0
        scanA = QImage('Yellow_BG.JPG')
        p = QPainter()
        p.begin(scanA)
        for i in range(500):
            for j in range(500):
                t = data.displayData[i][j]
                p.setPen(QColor(t, t, t, 255))
                p.drawPoint(i, j)
        p.end()
        print("Finished Image...")
        self.loadedImage.emit(scanA)

    def saystuff(self):
        print("HI")
