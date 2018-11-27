# This class takes the input data and stores it

import numpy as np
import random
from PyQt5.QtCore import *
# import RPi.GPIO as gpio

#implement SPI interface with the ADC and set up the call function

lock = QMutex()
scanData = np.zeros((500, 500, 5))
displayData = np.zeros((500, 500))


class AnalogData(QThread):
    x = 0
    y = 0
    z = 0

    def __init__(self):
        super().__init__()

    def run(self):
        q = QMutexLocker(lock)
        for i in range(2500):
            scanData[self.x][self.y][self.z] = np.random.randint(0, 256)
            displayData[self.x][self.y] = np.sum(scanData[self.x][self.y]) / 5
            self.x += 1
            if self.x == 500:
                self.x = 0
                self.y += 1
            if self.y == 500:
                self.y = 0
                self.z += 1
            if self.z == 5:
                self.z = 0
        return
