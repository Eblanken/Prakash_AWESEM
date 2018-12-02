#
# File: AWESEM_Testbench_Main.py
# ------------------------------
# Authors: Brion Ye, Erick Blankenberg
# Date: 9/28/2018
#
# Description:
#   This class starts the application and ties
#   everything together. This also sets up and contains
#   functions that handle GUI requests. See the docs folder
#   for an overview of the system.
#
#   General:
#      PyQt tutorial:      http://pythonforengineers.com/your-first-gui-app-with-python-and-pyqt/
#      Redirecting prints: https://stackoverflow.com/questions/44432276/print-out-python-console-output-to-qtextedit
#   Image processing:
#      Simple Itk:         http://www.simpleitk.org
#      Simple elastix:     https://simpleelastix.github.io
#
#   To successfully run this application
#   download the following: Anaconda, pyqt (installed using conda), numpy-indexed
#
#   Notes:
#       - Attempted to use mpipe but worked inconsistently on my windows laptop
#
#   Moving Forward:
#       - Work on and integrate analysis module. Use simpleitk
#       - Find a framework to make preformance timing easier
#
#   TODO:
#       - Only 5 of the 6 default settings for driving waveform trigger a callback when setting defaults, should check everything else as well
#       - Seems like the scrolling message box does not update until a user interacts with it,
#         the whole thing might be a waste of time anyway. I was trying to make seeing errors easier
#         for non-developer users.
#       - GUI Scaling is bad on windows, serial is bad on mac (may not be fixable / may be jus my mac,
#         Stroffgen has had simililar problems and has not been able to solve)
#       - MPipe would be nice but appears to be broken on my windows machine / not cooperative on mac either
#       - Random offset in sample timing upon initialization in MCU (at least in fast axis, bad setting of the offset intervalCounter)

#from   time                          import perf_counter
from   collections                   import deque
import sys
import numpy
import numpy_indexed
from   threading                     import Lock
from   matplotlib                    import cm
from   PyQt5.QtCore                  import *
from   PyQt5.QtGui                   import *
from   PyQt5.QtWidgets               import *
from   AWESEM_Testbench_Autocode     import Ui_MainWindow
from   AWESEM_PiPion_Interface       import AWESEM_PiPion_Interface
import AWESEM_Constants              as Const
import AWESEM_Data                   as Data
import AWESEM_Register               as Register
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
    __registerTh        = None
    __displayTh         = None
    __consoleOut        = None
    __ScanImage         = QImage('grid.png')
    __ColorMap          = cm.get_cmap('viridis')
    __UiElems           = None

    __DequeDataToRegister = deque(maxlen = Const.BUFFLEN_DATA_TO_REGISTER)

    def __init__(self, *args, **kwargs):
        super(TestBench, self).__init__(*args, **kwargs)
        # Structure is MCU -(interface)-> dataTh -(double buffer)-> registerTh -(callback)-> monitor
        self.__MCUInterface = AWESEM_PiPion_Interface()
        self.__registerTh   = Register.Register(self.__DequeDataToRegister, self.updateQTImage)
        self.__dataTh       = Data.DataIn(self.__MCUInterface, self.__DequeDataToRegister)

        self.setupTheUi()
        self.setDefaults()

        self.__dataTh.start()
        self.__registerTh.start()

    def __del__(self):
        sys.stdout = sys.__stdout__ # Sets print mode back to normal

    #
    # Description:
    # TODO LUT, ScanMode, saveImage, imageCorrection
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
        # self.__UiElems.Sampling_Averages_Spinbox.valueChanged.connect(self.setSamplingAverages) # TODO MCU only handles specific averaging quantites, need to create list in GUI
        self.__UiElems.Sampling_Phase_Vertical_Spinbox.valueChanged.connect(self.setSamplingReconstruction)
        self.__UiElems.Sampling_Phase_Horizontal_Spinbox.valueChanged.connect(self.setSamplingReconstruction)
        self.__UiElems.Sampling_LUT_Combobox.currentIndexChanged.connect(self.setSamplingReconstruction)
        self.__UiElems.Sampling_Collection_Combobox.currentIndexChanged.connect(self.setSamplingReconstruction)

        # Window 
        self.__UiElems.Plotter_Label.setPixmap(QPixmap.fromImage(self.__ScanImage).scaled(self.__UiElems.Plotter_Label.width(), self.__UiElems.Plotter_Label.height()))

        # Console output
        #sys.stdout = self.__consoleOut # COMBAK:
        self.__UiElems.Console_Preformance_Checkbox.stateChanged.connect(self.setConsolePreferences)
        self.__UiElems.Console_Verbose_Checkbox.stateChanged.connect(self.setConsolePreferences)
        self.__consoleOut    = Stream(newText = self.onUpdateText)

    def setDefaults(self):
        # Remember that when the combobox values are changed, this triggers the
        # callbacks and so the MCU is updated etc.

        # Scan Controls

        # Vertical Axis
        self.__UiElems.Vertical_Waveform_Combobox.setCurrentIndex(Const.DEFAULT_VERTWA)
        self.__UiElems.Vertical_Amplitude_Spinbox.setValue(Const.DEFAULT_VERTAM)
        self.__UiElems.Vertical_Frequency_Spinbox.setValue(Const.DEFAULT_VERTHZ)

        # Horizontal Axis
        self.__UiElems.Horizontal_Waveform_Combobox.setCurrentIndex(Const.DEFAULT_HORZWA)
        self.__UiElems.Horizontal_Amplitude_Spinbox.setValue(Const.DEFAULT_HORZAM)
        self.__UiElems.Horizontal_Frequency_Spinbox.setValue(Const.DEFAULT_HORZHZ)

        # Sampling
        self.__UiElems.Sampling_Frequency_Spinbox.setValue(Const.DEFAULT_ADC_SAMPLEFREQUENCY)
        self.__UiElems.Sampling_Phase_Vertical_Spinbox.setValue(Const.DEFAULT_HORZPHASE)
        self.__UiElems.Sampling_Phase_Horizontal_Spinbox.setValue(Const.DEFAULT_VERTPHASE)
        # TODO Averages

        # Console
        self.__UiElems.Console_Preformance_Checkbox.setCheckState(1)
        self.__UiElems.Console_Verbose_Checkbox.setCheckState(1)

    #
    # Description:
    #   Function called as emission by stdout replacement. Prints
    #   the console contents to the monitor. TODO Current monitor
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
        if valueVectors is not None:
            # Updates QT image
            colorTool = QColor()
            number = 0
            for value in valueVectors: # TODO this complicated color conversion makes me sad
                number = number + 1
                colorVector = self.__ColorMap(float(value[2]) / 255.0)
                colorTool.setRgb(colorVector[0] * 255, colorVector[1] * 255, colorVector[2] * 255)
                self.__ScanImage.setPixel(int(value[0]), int(value[1]), colorTool.rgb())
                #print("Value: %d, %d, %d" % (int(value[0]), int(value[1]), colorTool.rgb()))
            self.__UiElems.Plotter_Label.setPixmap(QPixmap.fromImage(self.__ScanImage).scaled(self.__UiElems.Plotter_Label.width(), self.__UiElems.Plotter_Label.height()))

    def toggleScanning(self):
        if(self.__MCUInterface.isScanning()):
            self.__UiElems.Scan_Pushbutton.setText("Start Scanning")
            self.__DequeDataToRegister.clear()
            self.__MCUInterface.pauseEvents()
            self.__dataTh.halt()
        else:
            self.__UiElems.Scan_Pushbutton.setText("Stop Scanning")
            self.__MCUInterface.beginEvents()
            self.__dataTh.commence()

    #
    # Description:
    #   Brings up dialog to save the image currently on the monitor to the disk.
    #
    def saveImage(self):
        print("Saving Not Implimented") # TODO Saving

    #
    # Description:
    #
    #
    def calibrate(self):
        # Calibration procedure is:
        # 1). Acquire data for full period of slowest axis
        # 2). Assign linear positions to all data ("Modern Art") and determine
        #     phase offsets.
        # 3). Re-assign positions from driving function with the found phase
        #     offsets.
        # 4). Segment this image, from momnents and size of blobs that are not
        #     touching the edge determine average spacing and make up a model
        #     grid of squares to try to fit to this.
        # 5). Run simpleelastix registration to do final adjustment fitting the
        #     model grid to the observed data.
        print("Calibration not fully implemented")

    #
    # Descripion:
    #   Used to set filters for strings printed to the console.
    #
    def setConsolePreferences(self):
        self.__consoleOut.includePrefix("Error", True)
        self.__consoleOut.includePrefix("Pref", self.__UiElems.Console_Preformance_Checkbox.isChecked())
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
            self.__DequeDataToRegister.clear()
            self.__dataTh.halt()
            self.__dataTh.commence()
            self.__MCUInterface.beginEvents()

        # Updates LUT methods to reflect new waveform
        self.setSamplingReconstruction()

    #
    # Desription:
    #   Updates the lookup methods and modes used for
    #   interpreting sampled data.
    #
    def setSamplingReconstruction(self):
        xFunction       = None
        yFunction       = None
        xFilterFunction = None
        yFilterFunction = None
        xPhase          = self.__UiElems.Sampling_Phase_Horizontal_Spinbox.value()
        yPhase          = self.__UiElems.Sampling_Phase_Vertical_Spinbox.value()
        xFrequency      = self.__UiElems.Horizontal_Frequency_Spinbox.value() # Spinbox is hz
        yFrequency      = self.__UiElems.Vertical_Frequency_Spinbox.value()   # Spinbox is hz
        xAmplitude      = self.__UiElems.Plotter_Label.width() * 0.5  # Fits into display image, centered in middle
        yAmplitude      = self.__UiElems.Plotter_Label.height() * 0.5 # Fits into display image, centered in middle
        currentLUTMode  = self.__UiElems.Sampling_LUT_Combobox.currentText()
        # TODO add image analysis distortion correction mode
        if(currentLUTMode == "Linear"):
            xFunction = lambda inputTime : Analysis.sawTooth(inputTime, xAmplitude, xFrequency, xPhase)
            yFunction = lambda inputTime : Analysis.sawTooth(inputTime, yAmplitude, yFrequency, yPhase)
            
        elif currentLUTMode == "Axis Waveform":
            waveformFunctions = { # Values correspond to those on Teensy
                    "Sine"     : Analysis.cos,
                    "Sawtooth" : Analysis.sawTooth, # Square is 2). currently unused
                    "Triangle" : Analysis.triangle
                    }
            # Assigns waveform
            xWaveText = self.__UiElems.Horizontal_Waveform_Combobox.currentText()
            yWaveText = self.__UiElems.Vertical_Waveform_Combobox.currentText()
            xFunction = lambda inputTime : waveformFunctions.get(xWaveText)(inputTime, xAmplitude, xFrequency, xPhase)
            yFunction = lambda inputTime : waveformFunctions.get(yWaveText)(inputTime, yAmplitude, yFrequency, yPhase)
            
            # Takes into account filtering data based on fast axis (eg. ignore while rising, falling, etc.)
            filteringText = self.__UiElems.Sampling_Collection_Combobox.currentText()
            # Finds fastest axis
            fastestPhase     = yPhase
            fastestFrequency = yFrequency
            fastestWaveText  = yWaveText
            if xFrequency > yFrequency:
                fastestPhase     = xPhase
                fastestFrequency = xFrequency
                fastestWaveText  = xWaveText
            # Creates filter, definition of waveform functions is falling edge if less than period / 2
            fastestPeriod   = (1.0 / fastestFrequency)
            filterFunction  = None
            filterCenter  = (fastestPeriod * (0.5 + fastestPhase)) # TODO does not handle phases greater than +0.5 or less than -0.5 atm
            if not filteringText == "All" and not fastestWaveText == "Sawtooth": # No filtering on sawtooth waveform or when none requested
                if filteringText == "Rising Fast":
                    def filterFunction(inputTime):
                        inputTime = numpy.fmod(inputTime, fastestPeriod) # TODO mod makes me sad, should be handled by MCU
                        return inputTime > filterCenter
                elif filteringText == "Falling Fast":
                    def filterFunction(inputTime):
                        inputTime = numpy.fmod(inputTime, fastestPeriod) # TODO mod makes me sad, should be handled by MCU
                        return inputTime < filterCenter
                else:
                    print("Error: Main_setSamplingReconstruction, bad sample filtering '%s'" % (filteringText))
                    return
            
            # Assigns filter function
            if xFrequency > yFrequency:
                xFilterFunction = filterFunction
            else:
                yFilterFunction = filterFunction
        else:
            print("Error: Main_setSamplingReconstruction, bad mode '%s'" % (currentLUTMode))
            return
        
        # Sets filtering function
        self.__registerTh.setDataFilterX(xFilterFunction)        
        self.__registerTh.setDataFilterY(yFilterFunction) 
            
        # Sets reconstruction functions
        if(xFunction is not None and yFunction is not None):
            self.__registerTh.setDataTranslateX(xFunction)
            self.__registerTh.setDataTranslateY(yFunction)
        else:
            print("Error: Main_setSamplingReconstruction, bad translation functions")

    #
    # Description:
    #   Increases sampling frequency and also alters sysem timing to
    #   keep up.
    #
    def setSamplingFrequency(self): # TODO
        newFrequency = self.__UiElems.Sampling_Frequency_Spinbox.value() * 1000.0 # Spinbox shows kHz, need to provide hz
        self.__dataTh.setPollFrequency((newFrequency / Const.ADC_BUFFERSIZE) * 5)
        self.__MCUInterface.setAdcFrequency(newFrequency)
        if(self.__MCUInterface.isScanning()):
            self.__MCUInterface.pauseEvents()
            self.__dataTh.halt()
            self.__dataTh.commence()
            self.__DequeDataToRegister.clear()
            self.__MCUInterface.beginEvents()

if __name__ == "__main__":
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance() 
    window = TestBench()
    window.show()
    sys.exit(app.exec_())
