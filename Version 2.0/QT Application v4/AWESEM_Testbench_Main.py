#
# File: AWESEM_Testbench_Main.py
# ------------------------------
# Authors: Brion Ye, Erick Blankenberg
# Date: 9/28/2018
#
# Description:
#   This class starts the application and ties
#   everything together. This also sets up and contains
#   functions that handle GUI requests.
#
#   PyQt tutorial:      http://pythonforengineers.com/your-first-gui-app-with-python-and-pyqt/
#   Redirecting prints: https://stackoverflow.com/questions/44432276/print-out-python-console-output-to-qtextedit
#   MPipe cookbook:     http://vmlaker.github.io/mpipe/cookbook.html
#
#   To successfully run this application
#   download the following: Anaconda, pyqt (installed using conda), mpipe
#
#   Moving Forward:
#       - Data should be a subclass of mpipe orderedWorker but without an entry point.
#         It should generate its own data and enter that into the pipe.
#       - Work on and integrate analysis module.
#       - Find a framework to make preformance timing easier
#

from   time                          import perf_counter
import sys
import mpipe
import numpy
from   threading                     import Lock
from   matplotlib                    import cm
from   PyQt5.QtCore                  import *
from   PyQt5.QtGui                   import *
from   PyQt5.QtWidgets               import *
from   AWESEM_Testbench_Autocode     import Ui_MainWindow
from   AWESEM_PiPion_Interface       import AWESEM_PiPion_Interface
import AWESEM_Constants              as Const
import AWESEM_Data                   as Data
import AWESEM_Display                as Display
import AWESEM_Analysis               as Analysis

# Used for redirecting console output
class Stream(QObject):
    newText    = pyqtSignal(str)
    __allowAll   = True
    __allowedSet = set()

    def allowAll(self, doAllow):
        self.__allowAll = doAllow

    def includePrefix(self, token, doInclude):
        if(doInclude):
            if(token not in self.__allowedSet):
                self.__allowedSet.add(token)
                return True
            return False
        else:
            if(token in self.__allowedSet):
                self.__allowedSet.remove(token)
                return True
            return False

    def write(self, text):
        if not self.__allowAll:
            for token in self.__allowedSet:
                if(text.startswith(token)):
                    self.newText.emit(str(text))
                    return
        else:
            self.newText.emit(str(text))

# The main program
class TestBench(QMainWindow):

    __MCUInterface      = None
    __dataTh            = None
    __displayTh         = None
    __consoleOut        = None
    __ProcessingPipe    = None
    __updatingImageLock = Lock()
    __ScanPixmap        = None
    __ColorMap          = cm.get_cmap('viridis')
    __UiElems           = None
    __ScanPixmap        = None

    def __init__(self):
        super().__init__()
        self.__MCUInterface  = AWESEM_PiPion_Interface()
        self.__dataTh        = Data.DataIn(self.__MCUInterface, self.__ProcessingPipe)
        self.__displayTh     = Display.Display()
        self.__consoleOut    = Stream(newText = self.onUpdateText)

        # Starts
        self.__dataTh.start()

        self.setupTheUi()
        self.setDefaults()

        """
        displayStage    = mpipe.Stage(self.__displayTh, 1)
        self.__ProcessingPipe = mpipe.Pipeline(displayStage.link(mpipe.OrderedStage(updateQTImage, 1))) # Recieves input from
        """


    def __del__(self):
        sys.stdout = sys.__stdout__ # Sets print mode back to normal

    #
    # Description:
    # Connect all the signals and slots
    # TODO LUT, Console Checkboxes, ScanMode, saveImage
    #
    def setupTheUi(self):
        self.__UiElems = Ui_MainWindow()
        self.__UiElems.setupUi(self)

        # Scan Controls
        self.__UiElems.Scan_Pushbutton.clicked.connect(self.toggleScanning)
        self.__UiElems.Save_Pushbutton.clicked.connect(self.saveImage)

        # Vertical Axis
        self.__UiElems.Vertical_Waveform_Combobox.currentTextChanged.connect(self.setWaveforms)
        self.__UiElems.Vertical_Amplitude_Spinbox.valueChanged.connect(self.setWaveforms)
        self.__UiElems.Vertical_Frequency_Spinbox.valueChanged.connect(self.setWaveforms)

        # Horizontal Axis
        self.__UiElems.Horizontal_Waveform_Combobox.currentTextChanged.connect(self.setWaveforms)
        self.__UiElems.Horizontal_Amplitude_Spinbox.valueChanged.connect(self.setWaveforms)
        self.__UiElems.Horizontal_Frequency_Spinbox.valueChanged.connect(self.setWaveforms)

        # Sampling
        self.__UiElems.Sampling_Frequency_Spinbox.valueChanged.connect(self.setSamplingFrequency)
        # self.Sampling_Averages_Spinbox.valueChanged.connect(self.setSamplingAverages) # TODO
        self.__UiElems.Sampling_Phase_Vertical_Spinbox.valueChanged.connect(self.setSamplingReconstruction)
        self.__UiElems.Sampling_Phase_Horizontal_Spinbox.valueChanged.connect(self.setSamplingReconstruction)
        # self.Sampling_LUT_Combobox.textChanged.connect(self.setSamplingReconstruction) # TODO
        self.__UiElems.Sampling_Collection_Combobox.currentTextChanged.connect(self.setSamplingReconstruction)

        # Console output
        #sys.stdout = self.__consoleOut # COMBAK:
        self.__UiElems.Console_Preformance_Checkbox.stateChanged.connect(self.setConsolePreferences)
        self.__UiElems.Console_Verbose_Checkbox.stateChanged.connect(self.setConsolePreferences)

    def setDefaults(self):
        # Scan Controls

        # Vertical Axis
        self.__UiElems.Vertical_Amplitude_Spinbox.setValue(Const.DEFAULT_VERTAM)
        self.__UiElems.Vertical_Frequency_Spinbox.setValue(Const.DEFAULT_VERTHZ)

        # Horizontal Axis
        self.__UiElems.Horizontal_Amplitude_Spinbox.setValue(Const.DEFAULT_HORZAM)
        self.__UiElems.Horizontal_Frequency_Spinbox.setValue(Const.DEFAULT_HORZHZ)

        # Sampling
        self.__UiElems.Sampling_Frequency_Spinbox.setValue(Const.DEFAULT_ADC_SAMPLEFREQUENCY)
        # self.Sampling_Phase_Spinbox.setValue() TODO
        # TODO Averages, scanMode

        # Console
        self.__UiElems.Console_Preformance_Checkbox.setCheckState(1)
        self.__UiElems.Console_Verbose_Checkbox.setCheckState(1)

        # Resets all
        self.setWaveforms()
        self.setSamplingReconstruction()
        self.setSamplingFrequency()
        #self.setConsolePreferences()

    #
    # Description:
    #   Function called as emission by stdout replacement. Prints
    #   the console contents to the monitor. # TODO Current monitor
    #   is too small and the user is allowed to edit the contents manually
    #   also the monitor should be self-clearing
    #
    def onUpdateText(self, text):
        cursor = self.__UiElems.Console_Output_TextBox.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.__UiElems.Console_Output_TextBox.setTextCursor(cursor)
        self.__UiElems.Console_Output_TextBox.ensureCursorVisible()

    # Description:
    #   Updates the reference qt object from the given mapped data
    #
    # Parameters:
    #   'valueVectors'  Numpy array of mapped image intensities of the format [xPosition, yPosition, intensityValue];[...]...
    #
    def updateQTImage(self, valueVectors):
        valueVectors[:, 0] = valueVectors[:, 0] * self.Plotter_Label.width()
        valueVectors[:, 1] = valueVectors[:, 1] * self.Plotter_Label.height()
        valueVectors.astype(int)
        # Ordered workers from mpipe will return in order but might process however they
        # want. We really want access to the qpixmap to be exclusive.
        self.__updatingImageLock.acquire(True)
        for value in valueVectors:
            self.__ScanPixmap.setPixelColor(value[0], value[1], self._ColorMap(float(value[2]) / 255.0))
        self.__UiElems.Plotter_Label.setPixMap(self.__ScanPixmap.scaled(self.Plotter_Label.width(), self.Plotter_Label.height()))
        self.__updatingImageLock.release()

    def toggleScanning(self):
        if(self.__MCUInterface.isScanning()):
            self.__UiElems.Scan_Pushbutton.setText("Start Scanning")
            self.__MCUInterface.pauseEvents()
            self.__dataTh.end()
        else:
            self.__UiElems.Scan_Pushbutton.setText("Stop Scanning")
            self.__MCUInterface.beginEvents()
            self.__dataTh.begin()

    def saveImage(self):
        print("Saving Not Implimented") # TODO Saving

    #
    # Descripion:
    #   Used to set filters for strings printed to the console.
    #
    def setConsolePreferences(self):
        self.__consoleOut.includePrefix("ERROR", True)
        self.__consoleOut.includePrefix("PREF", self.__UiElems.Console_Preformance_Checkbox.isChecked())
        self.__consoleOut.allowAll(self.__UiElems.Console_Verbose_Checkbox.isChecked())

    #
    # Description:
    #   Updates the output waveforms to whatever is currently listed in
    #   the GUI.
    #
    def setWaveforms(self):
        waveformLabels = { # Values correspond to those on Teensy
                "Sine"     : 0,
                "Sawtooth" : 1, # Square is 2). currently unused
                "Triangle" : 3
                }
        # Handles vertical
        self.__MCUInterface.setDacMagnitude(0, self.__UiElems.Vertical_Amplitude_Spinbox.value())
        self.__MCUInterface.setDacFrequency(0, self.__UiElems.Vertical_Frequency_Spinbox.value())
        result = waveformLabels.get(self.__UiElems.Vertical_Waveform_Combobox.currentText())
        if(result is not None):
            self.__MCUInterface.setDacWaveform(0, result)

        # Handles horizontal
        self.__MCUInterface.setDacMagnitude(1, self.__UiElems.Horizontal_Amplitude_Spinbox.value())
        self.__MCUInterface.setDacFrequency(1, self.__UiElems.Horizontal_Frequency_Spinbox.value())
        result = waveformLabels.get(self.__UiElems.Horizontal_Waveform_Combobox.currentText())
        if(result is not None):
            self.__MCUInterface.setDacWaveform(1, result)

        # Refreshes MCU
        if(self.__MCUInterface.isScanning()): # If not scanning will take effect on startup anyway
            self.__MCUInterface.pauseEvents()
            self.__MCUInterface.beginEvents()

        # Updates LUT methods to reflect new waveform
        self.setSamplingReconstruction()

    #
    # Desription:
    #   Updates the lookup methods and modes used for
    #   interpreting sampled data.
    #
    def setSamplingReconstruction(self):
        xLambda = None
        yLambda = None
        xPhase  = self.__UiElems.Sampling_Phase_Horizontal_Spinbox.value()
        yPhase  = self.__UiElems.Sampling_Phase_Vertical_Spinbox.value()
        xFrequency = self.__UiElems.Horizontal_Frequency_Spinbox.value() * 1000.0 # Spinbox is hz
        yFrequency = self.__UiElems.Vertical_Frequency_Spinbox.value() * 1000.0   # Spinbox is hz
        currentLUTMode = self.__UiElems.Sampling_LUT_Combobox.currentText()
        # TODO add image analysis distortion correction mode
        if(currentLUTMode == "Linear"):
            xLambda = lambda inputTime, amplitude : Analysis.sawTooth(inputTime, xFrequency, xPhase)
            yLambda = lambda inputTime, amplitude : Analysis.sawTooth(inputTime, yFrequency, yPhase)
        elif currentLUTMode == "Axis Waveform":
            waveformLabels = { # Values correspond to those on Teensy
                    "Sine"     : Analysis.sine,
                    "Sawtooth" : Analysis.sawTooth, # Square is 2). currently unused
                    "Triangle" : Analysis.triangle
                    }
            # Assigns waveform
            xLambda = waveformLabels.get(self.__UiElems.Horizontal_Waveform_Combobox.currentText())
            yLambda = waveformLabels.get(self.__UiElems.Vertical_Waveform_Combobox.currentText())
        # Sets reconstruction functions
        if(xLambda is not None and yLambda is not None):
            self.__displayTh.setDataTranslateX(xLambda)
            self.__displayTh.setDataTranslateY(yLambda)

    #
    # Description:
    #   Increases sampling frequency and also alters sysem timing to
    #   keep up.
    #
    def setSamplingFrequency(self): # TODO
        newFrequency = self.__UiElems.Sampling_Frequency_Spinbox.value() * 1000.0 # Spinbox shows kHz
        self.__dataTh.setPollFrequency(newFrequency)
        self.__MCUInterface.setAdcFrequency(newFrequency)
        if(self.__MCUInterface.isScanning):
            self.__MCUInterface.pauseEvents()
            self.__MCUInterface.beginEvents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestBench()
    window.show()
    sys.exit(app.exec_())
