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
#
#   To successfully run this application
#   download the following: Anaconda, pyqt (installed using conda), 
#
#   TODO:
#       Work on and integrate analysis module. Find a framework to make
#       preformance timing easier etc. Maybe use multiprocessing instead
#       of threads.
#

from   time                          import perf_counter
import sys
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
class Stream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)
    def write(self, text):
        self.newText.emit(str(text))

# The main program
class TestBench(QMainWindow, Ui_MainWindow):
    
    self.isScanning   = False
    self.MCUInterface = None
    self.dataTh       = None
    self.displayTh    = None
    
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        
        self.Analysis      = Analysis()
        self.MCUInterface  = AWESEM_PiPion_Interface()
        self.dataTh        = Data.DataIn(self._MCUInterface)
        self.displayTh     = Display.Display(self.Plotter_Label)
        
        self.setupUi()
        self.setDefaults()

    def __del__(self):
        sys.stdout = sys.__stdout__ # Sets print mode back to normal

    #
    # Description:
    # Connect all the signals and slots
    # TODO LUT, Console Checkboxes, ScanMode, saveImage
    #
    def setupUI(self):
        # Scan Controls
        self.Scan_Pushbutton.clicked.connect(self.toggleScanning)
        self.Save_Pushbutton.clicked.connect(self.saveImage)
        
        # Vertical Axis
        self.Vertical_Waveform_Combobox.currentTextChanged.connect(self.setWaveforms)
        self.Vertical_Amplitude_Spinbox.valueChanged.connect(self.setWaveforms)
        self.Vertical_Frequency_Spinbox.valueChanged.connect(self.setWaveforms)
        
        # Horizontal Axis
        self.Horizontal_Waveform_Combobox.currentTextChanged.connect(self.setWaveforms)
        self.Horizontal_Amplitude_Spinbox.valueChanged.connect(self.setWaveforms)
        self.Horizontal_Frequency_Spinbox.valueChanged.connect(self.setWaveforms)
        
        # Sampling
        self.Sampling_Frequency_Spinbox.valueChanged.connect(self.setSamplingFrequency)
        # self.Sampling_Averages_Spinbox.valueChanged.connect(self.setSamplingAverages) # TODO
        self.Sampling_Phase_Vertical_Spinbox.valueChanged.connect(self.setSamplingReconstruction)
        self.Sampling_Phase_Horizontal_Spinbox.valueChanged.connect(self.setSamplingReconstruction)
        # self.Sampling_LUT_Combobox.textChanged.connect(self.setSamplingReconstruction) # TODO
        self.Sampling_Collection_Combobox.textChanged.connect(self.setSamplingReconstruction)
        
        # Console output
        sys.stdout = Stream(newText = self.onUpdateText)
        self.Console_Preformance_Checkbox.connect(self.setConsolePreferences)
        self.Console_Verbose_Checkbox.connect(self.setConsolePreferences)
        # TODO write verbose and preformance checkboxes
        # TODO further setup for console?

    def setDefaults(self):  
        # Scan Controls
        self.ScanPixMap.setFixedWidth(Const.RES_W)
        self.ScanPixMap.setFixedHeight(Const.RES_H)
        
        # Vertical Axis
        self.Vertical_Amplitude_Spinbox.setValue(Const.DEFAULT_VERTAM)
        self.setVerticalAmplitude(Const.DEFAULT_VERTAM)
        self.Vertical_Frequency_Spinbox.setValue(Const.DEFAULT_VERTADC_BUFFERSIZE)
        self.setVerticalFrequency(Const.DEFAULT_VERTHZ)
        
        # Horizontal Axis
        self.Horizontal_Amplitude_Spinbox.setValue(Const.DEFAULT_HORZAM)
        self.setHorizontalAmplitude(Const.DEFAULT_HORZAM)
        self.Horizontal_Frequency_Spinbox.setValue(Const.DEFAULT_HORZHZ)
        self.setHorizontalAmplitude(Const.DEFAULT_HORZHZ)
        
        # Sampling
        self.Sampling_Frequency_Spinbox.setValue(Cons.DEFAULT_ADC_SAMPLEFREQUENCY)
        self.setSamplingFrequency(Const.DEFAULT_ADC_SAMPLEFREQUENCY)
        # self.Sampling_Phase_Spinbox.setValue() TODO
        # TODO Averages, phase, LUT, scanMode
        
        # Console
        # TODO
    
    def onUpdateText(self, text):
        cursor = self.Console_Output_TextBox.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.Console_Output_TextBox.setTextCursor(cursor)
        self.Console_Output_TextBox.ensureCursorVisible()
    
    #
    # Callback to show the image given by display thread
    #
    def showGivenImage(self, image):
        #print("GUI: Updating") # TODO
        #b = perf_counter()
        self.ScanPixmap.convertFromImage(image)
        self.Plotter_Label.setPixmap(self.ScanPixmap)# TODO self.ScanPixmap.scaled(self.Plotter_Label., self., Qt.KeepAspectRatio)) # TODO may impact preformance
        #print("GUI: Update time: ", perf_counter() - b)
        return
    
    def toggleScanning(self):
        if(self.isScanning):
            self.Scan_Pushbutton.setText("Start Scanning")
            self.isScanning = False
            self.MCUInterface.pauseEvents()
            self.displayTh.stop()
            self.dataTh.stop()
        else:
            self.Scan_Pushbutton.setText("Stop Scanning")
            self.isScanning = True
            self.MCUInterface.beginEvents()
            self.displayTh.start()
            self.dataTh.start()
        
    def saveImage(self):
        print("Saving Not Implimented") # TODO Saving
    
    #
    # Descripion:
    #   Used to set filters for strings printed to the console.
    #
    def setConsolePreferences(self):
        # TODO
        
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
        self.MCUInterface.setDacMagnitude(0, self.Vertical_Amplitude_Spinbox.value())
        self.MCUInterface.setDacFrequency(0, self.Vertical_Frequency_Spinbox.value() * 1000.0) # Spinbox is khz
        result = waveformLabels.get(self.Vertical_Type_Combobox.currentText())
        if(result is not None):
            self.MCUInterface.setDacWaveform(0, result)

        # Handles horizontal
        self.MCUInterface.setDacMagnitude(1, self.Horizontal_Amplitude_Spinbox.value())
        self.MCUInterface.setDacFrequency(1, self.Horizontal_Frequency_Spinbox.value() * 1000.0) # Spinbox is khz
        result = waveformLabels.get(self.Horizontal_Type_Combobox.currentText())
        if(result is not None):
            self.MCUInterface.setDacWaveform(1, result)
            
        # Refreshes MCU
        if(self.isScanning): # If not scanning will take effect on startup anyway
            self.MCUInterface.pauseEvents()
            self.MCUInterface.beginEvents()
        
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
        xPhase  = self.Sampling_Phase_Horizontal_Spinbox.getValue()
        yPhase  = self.Sampling_Phase_Vertical_Spinbox.getValue()
        xFrequency = self.Horizontal_Frequency_Spinbox.value() * 1000.0 # Spinbox is hz
        yFrequency = self.Vertical_Frequency_Spinbox.value() * 1000.0   # Spinbox is hz
        
        currentLUTMode = self.Sampling_LUT_Combobox.currentText()
        if(currentLUTMode = "Linear"):
            xLambda = lambda (inputTime, amplitude) : Analysis.sawTooth(inputTime, amplitude, xFrequency, xPhase)
            yLambda = lambda (inputTime, amplitude) : Analysis.sawTooth(inputTime, amplitude, xFrequency, yPhase)
        elif(currentLUTMode = "Axis Waveform"):
            waveformLabels = { # Values correspond to those on Teensy
                    "Sine"     : Analysis.sine,
                    "Sawtooth" : Analysis.sawTooth, # Square is 2). currently unused
                    "Triangle" : Analysis.triangle
                    }
            # Handles horizontal
            result = waveformLabels.get(self.Horizontal_Type_Combobox.currentText())
            if(result is not None):
                sLambda = lambda (inputTime, amplitude):
            
            # Handles vertical
            self.Sampling_Phase_Vertical_Spinbox.getValue()
             if(result is not None):
                self.Display.setDataTranslateX()
                yLambda = lambda (inputTime, amplitude): 
            
    if(xLambda is not None and yLambda is not None):
        self.Display.setDataTranslateX(xLambda)
        self.Display.setDataTranslateY(yLambda)
        
    #
    # Description:
    #   Increases sampling frequency and also alters sysem timing to
    #   keep up.
    #
    def setSamplingFrequency(self): # TODO
        newFrequency = self.Sampling_Frequency_Spinbox.value() * 1000.0 # Spinbox shows kHz
        self.MCUInterface.setAdcFrequency(newFrequency)
        self.displayTh. # TODO
        self.dataTh. # TODO
        if(self.isScanning):
            self.MCUInterface.pauseEvents()
            self.MCUInterface.beginEvents()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = TestBench()
    window.show()
    sys.exit(app.exec_())
