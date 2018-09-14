# This class generates the responsive UI capabilities of the application

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from QTD_Window import Ui_MainWindow
import AWESEM_Constants as Const
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
    
    xZoomUpdate = pyqtSignal()
    yZoomUpdate = pyqtSignal()

    # Nothing much to say, this creates the UI.
    def __init__(self, PiPionInterface):
        super().__init__()
        self._MCUInterface = PiPionInterface
        self.scanA = Const.IMG.copy(0, 0, Const.defw, Const.defh)
        self.scanPixmap = QPixmap()
        self.scanLabel = QLabel('Scan', self)
        self.scanLabel.setFixedWidth(Const.defw)
        self.scanLabel.setFixedHeight(Const.defh)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.XZoomSlider.setValue(Const.XMag * 100.0)
        self.ui.YZoomSlider.setValue(Const.YMag * 100.0)
        self.showGivenImage(self.scanA)
        self.scanLabel.move(50, 90)
        self.scanLabel.show()
        self.connectUI()

    # Connect all the signals and slots
    def connectUI(self):
        # Scan Controls
        self.ui.ScanB.clicked.connect(self.toggleScanning)
        
        # Y Zoom
        self.ui.XUpdateB.clicked.connect(self.setXMagnitude)
        
        # X Zoom
        self.ui.YUpdateB.clicked.connect(self.setYMagnitude)
        

    # Slot to show the image given by display thread
    def showGivenImage(self, image):
        #print("GUI: Updating")
        b = perf_counter()
        self.scanPixmap.convertFromImage(image)
        self.scanLabel.setPixmap(self.scanPixmap)
        #print("GUI: Update time: ", perf_counter() - b)
        return
    
    # Sets the peak-peak potential of the X axis in volts
    def setXMagnitude(self):
        magnitude = float(self.ui.XZoomSlider.value() / 100.0)
        self._MCUInterface.setDacMagnitude(0, magnitude)
        self._MCUInterface.pauseEvents()
        self._MCUInterface.beginEvents()
        
        
    # Sets the peak-peak potential of the Y axis in volts
    def setYMagnitude(self):
        magnitude = float(self.ui.YZoomSlider.value() / 100.0)
        self._MCUInterface.setDacMagnitude(1, magnitude)
        self._MCUInterface.pauseEvents()
        self._MCUInterface.beginEvents()

    # Connects Scan button to Main.py's startScanning and endScanning
    def toggleScanning(self, active):
        if active:
            self.startScanning.emit()
        else:
            self.endScanning.emit()
