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
#      PyQt tutorial:       http://pythonforengineers.com/your-first-gui-app-with-python-and-pyqt/
#      Redirecting prints:  https://stackoverflow.com/questions/44432276/print-out-python-console-output-to-qtextedit
#      Multithreading pref:
#   Image processing:
#      Simple Itk:          http://www.simpleitk.org
#      Simple elastix:      https://simpleelastix.github.io
#
#   Notes:
#       - Attempted to use mpipe but worked inconsistently on my windows laptop
#
#   Moving Forward:
#       - Apparently one thread is faster than two for data acquisition and handling, we
#         should look into multiprocessing, even the raspberry pi has more than one core.
#       - Work on and integrate analysis module. Use simpleitk
#       - Find a framework to make preformance timing easier
#
#   TODO:
#       - Only 5 of the 6 default settings for driving waveform trigger a callback when setting defaults, should check everything else as well
#       - Seems like the scrolling message box does not update until a user interacts with it,
#         the whole thing might be a waste of time anyway. I was trying to make seeing errors easier
#         for non-developer users.
#       - Seems like there might be rollover or some sort of timing issue for the latter half of the rising part
#         of some waveforms. They temporarily become very choppy.

doChangeCPU = False # Set to true to set CPU affinity manually

import scipy
import ast
import psutil
import os
import glob
import sys
import numpy
import datetime
from   scipy                         import signal
from   matplotlib                    import cm
from   matplotlib                    import pyplot as plt
from   matplotlib.backends.backend_agg import FigureCanvasAgg
from   qimage2ndarray                import byte_view
from   qimage2ndarray                import array2qimage
from   PyQt5.QtCore                  import *
from   PyQt5.QtGui                   import *
from   PyQt5.QtWidgets               import *
from   PyQt5                         import uic
from   AWESEM_PiPion_Interface       import AWESEM_PiPion_Interface
import AWESEM_Constants              as Const
import AWESEM_Register               as Register
import AWESEM_Analysis               as Analysis

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

Ui_MainWindow, QtBaseClass = uic.loadUiType("TestBench.ui")

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

    # Internal components
    __MCUInterface      = None
    __registerTh        = None
    __consoleOut        = None
    __ScanImage         = QImage(Const.PATH_BACKGROUNDIMAGE).scaled(Const.RES_W, Const.RES_H)
    __ColorMap          = cm.get_cmap('viridis')
    __UiElems           = None
    __WaveTables        = None # Dictionary of {"Name": tableArray}
    __SystemModels      = None # Dictionary of {"Name": signalContinousLTIModel}

    # Trackers for GUI elements, used so that the menu will bounce back to previous menu item after selecting option to load custom data
    __currentXWaveformOpt  = None
    __currentYWaveformOpt  = None
    
    
    __currentLUTModeOpt    = None
    # Tracker for current scale so that files can have these when exported, set to None to disable axis
    __currentXLength        = None # (microns)
    __currentYLength        = None # (microns)

    def __init__(self, *args, **kwargs):
        super(TestBench, self).__init__(*args, **kwargs)
        # Structure is MCU -(interface)-> dataTh -(double buffer)-> registerTh -(callback)-> monitor
        self.__UiElems = Ui_MainWindow()
        self.__UiElems.setupUi(self)
        self.__MCUInterface = AWESEM_PiPion_Interface()
        self.__registerTh   = Register.Register(self.updateQTImage, self.__MCUInterface)
        self.setUiProperties()
        self.loadDefaultWaveTables()
        self.loadDefaultModels()
        self.setDefaults()
        self.linkUiCallbacks()
        self.__registerTh.start()


        self.updateWaveforms()

    def __del__(self):
        self.shutdownResources()

    def shutdownResources(self):
        print("Closing Resources")
        self.__MCUInterface.close()


        self.__registerTh.close()
        print("Resources Closed")
        sys.stdout = sys.__stdout__ # Sets print mode back to normal

    def loadModel(self, filePath):
        _, systemFullName = os.path.split(filePath) # Returns path and file name
        systemName, _ = os.path.splitext(systemFullName) # Returns extension and name
        if self.__UiElems.Sampling_LUT_Combobox.findText(systemName) == -1:
            try:
                with open(filePath,'r') as inf:
                    systemParameters = ast.literal_eval(inf.read())
                self.__SystemModels[systemName] = signal.ZerosPolesGain(systemParameters['Zeros'], systemParameters['Poles'], systemParameters['Gain'])
                self.__UiElems.Sampling_LUT_Combobox.blockSignals(True)
                self.__UiElems.Sampling_LUT_Combobox.insertItem(0, systemName)
                self.__UiElems.Sampling_LUT_Combobox.blockSignals(False)
            except Exception as e:
                print("Error: Failed to load model \"%s\" with error \"%s\"" % (filePath, e))
        else:
            print("Error: Stopped attempted load of redundant model, existing model at: %s" % (self.__UiElems.Sampling_LUT_Combobox.findText(waveName)))

    def loadDefaultModels(self):
        # Adds default options
        self.__UiElems.Sampling_LUT_Combobox.blockSignals(True)
        self.__UiElems.Sampling_LUT_Combobox.insertItem(0, "Import Model")
        self.__UiElems.Sampling_LUT_Combobox.insertItem(0, "Linear")
        self.__UiElems.Sampling_LUT_Combobox.insertItem(0, "Axis Waveform")
        self.__UiElems.Sampling_LUT_Combobox.blockSignals(False)
        # Loads in files
        self.__SystemModels = dict()
        availableModels = glob.glob(os.path.join(os.path.abspath(''), "SysModels", "*.txt"))
        for filePath in availableModels:
            self.loadModel(filePath)
        self.__UiElems.Sampling_LUT_Combobox.setCurrentIndex(0)

    # Loads wave table at the given directory into available waveform dictionary
    def loadWaveform(self, filePath):
        _, waveFullName = os.path.split(filePath) # Returns path and file name
        waveName, _ = os.path.splitext(waveFullName) # Returns extension and name
        if self.__UiElems.Vertical_Waveform_Combobox.findText(waveName) == -1:
            try:
                dataVals = numpy.genfromtxt(filePath)
                if(dataVals.shape[0] != 256):
                    print("Error: Failed to load waveform \"%s\", length of %s not 256" % (filePath, dataVals.shape[0]))
                elif(numpy.any(numpy.logical_or(dataVals > 32767, dataVals < -32767))):
                    print("Error: Failed to load waveform \"%s\", some values larger than 16 bit limit" % (filePath))
                else:
                    self.__WaveTables[waveName] = dataVals
                    self.__UiElems.Vertical_Waveform_Combobox.blockSignals(True)
                    self.__UiElems.Horizontal_Waveform_Combobox.blockSignals(True)
                    self.__UiElems.Horizontal_Waveform_Combobox.insertItem(0, waveName)
                    self.__UiElems.Vertical_Waveform_Combobox.insertItem(0, waveName)
                    self.__UiElems.Vertical_Waveform_Combobox.blockSignals(False)
                    self.__UiElems.Horizontal_Waveform_Combobox.blockSignals(False)
            except Exception as e:
                print("Error: Failed to load waveform \"%s\" with error \"%s\"" % (filePath, e))
        else:
            print("Error: Stopped attempted load of redundant waveform, existing waveform at: %s" % (self.__UiElems.Vertical_Waveform_Combobox.findText(waveName)))

    # Loads any waveform tables already in the "Waveforms" directory
    def loadDefaultWaveTables(self):
        # Add default options
        self.__UiElems.Vertical_Waveform_Combobox.blockSignals(True)
        self.__UiElems.Horizontal_Waveform_Combobox.blockSignals(True)
        self.__UiElems.Horizontal_Waveform_Combobox.insertItem(0, "Load Custom")
        self.__UiElems.Vertical_Waveform_Combobox.insertItem(0, "Load Custom")
        self.__UiElems.Vertical_Waveform_Combobox.blockSignals(False)
        self.__UiElems.Horizontal_Waveform_Combobox.blockSignals(False)
        # Load files from other directories
        self.__WaveTables = dict()
        availableTables = glob.glob(os.path.join(os.path.abspath(''), "Waveforms", "*.csv"))
        for filePath in availableTables:
            self.loadWaveform(filePath)
        self.__UiElems.Vertical_Waveform_Combobox.setCurrentIndex(0)
        self.__UiElems.Horizontal_Waveform_Combobox.setCurrentIndex(0)

    def setUiProperties(self):
        self.__UiElems.Vertical_Waveform_Combobox.setInsertPolicy(QComboBox.InsertAtTop)
        self.__UiElems.Horizontal_Waveform_Combobox.setInsertPolicy(QComboBox.InsertAtTop)
        self.__UiElems.Sampling_LUT_Combobox.setInsertPolicy(QComboBox.InsertAtTop)

    #
    # Description:
    #   Links functions to button presses
    #
    def linkUiCallbacks(self):
        # Scan Controls
        self.__UiElems.Scan_Pushbutton.clicked.connect(self.toggleScanning)
        self.__UiElems.Save_Pushbutton.clicked.connect(self.saveImage)
        self.__UiElems.Clear_Pushbutton.clicked.connect(self.clearScreen)

        # Vertical Axis
        self.__UiElems.Vertical_Waveform_Combobox.currentTextChanged.connect(self.updateWaveforms)
        self.__UiElems.Vertical_Amplitude_Spinbox.valueChanged.connect(self.updateWaveforms)
        self.__UiElems.Vertical_Frequency_Spinbox.valueChanged.connect(self.updateWaveforms)

        # Horizontal Axis
        self.__UiElems.Horizontal_Waveform_Combobox.currentTextChanged.connect(self.updateWaveforms)
        self.__UiElems.Horizontal_Amplitude_Spinbox.valueChanged.connect(self.updateWaveforms)
        self.__UiElems.Horizontal_Frequency_Spinbox.valueChanged.connect(self.updateWaveforms)

        # Sampling
        self.__UiElems.Sampling_Frequency_Spinbox.valueChanged.connect(self.updateSamplingFrequency)
        # self.__UiElems.Sampling_Averages_Spinbox.valueChanged.connect(self.setSamplingAverages)
        self.__UiElems.Sampling_Phase_Vertical_Spinbox.valueChanged.connect(self.updateSamplingReconstruction)
        self.__UiElems.Sampling_Phase_Horizontal_Spinbox.valueChanged.connect(self.updateSamplingReconstruction)
        self.__UiElems.Sampling_LUT_Combobox.currentIndexChanged.connect(self.updateSamplingReconstruction)
        self.__UiElems.Sampling_Horizontal_Collection_Combobox.currentIndexChanged.connect(self.updateSamplingReconstruction)
        self.__UiElems.Sampling_Vertical_Collection_Combobox.currentIndexChanged.connect(self.updateSamplingReconstruction)


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
        
        defaultVerticalWaveformIndex = self.__UiElems.Vertical_Waveform_Combobox.findText(Const.DEFAULT_VERTWAV)
        if(defaultVerticalWaveformIndex >= 0):
            self.__UiElems.Vertical_Waveform_Combobox.setCurrentIndex(defaultVerticalWaveformIndex)           
        else:
            print("Default set vertical waveform does not match a loaded file, check the value in the constants file.")
        self.__UiElems.Vertical_Amplitude_Spinbox.setValue(Const.DEFAULT_VERTAM)
        self.__UiElems.Vertical_Frequency_Spinbox.setValue(Const.DEFAULT_VERTHZ)
        self.__UiElems.Sampling_Phase_Vertical_Spinbox.setValue(Const.DEFAULT_VERTPHASE)

        # Horizontal Axis
        defaultHorizontalWaveformIndex = self.__UiElems.Horizontal_Waveform_Combobox.findText(Const.DEFAULT_HORZWAV)
        if(defaultHorizontalWaveformIndex >= 0):
            self.__UiElems.Horizontal_Waveform_Combobox.setCurrentIndex(defaultHorizontalWaveformIndex)           
        else:
            print("Default set horizontal waveform does not match a loaded file, check the value in the constants file.")
        self.__UiElems.Horizontal_Amplitude_Spinbox.setValue(Const.DEFAULT_HORZAM)
        self.__UiElems.Horizontal_Frequency_Spinbox.setValue(Const.DEFAULT_HORZHZ)
        self.__UiElems.Sampling_Phase_Horizontal_Spinbox.setValue(Const.DEFAULT_HORZPHASE)

        # Sampling and reconstruction
        defaultReconstructionIndex = self.__UiElems.Sampling_LUT_Combobox.findText(Const.DEFAULT_LUTMODEL)
        if(defaultReconstructionIndex >= 0):
            self.__UiElems.Sampling_LUT_Combobox.setCurrentIndex(defaultReconstructionIndex)           
        else:
            print("Default set LUT method does not match a loaded model or method, check the value in the constants file.")
        self.__UiElems.Sampling_Frequency_Spinbox.setValue(Const.DEFAULT_ADC_SAMPLEFREQUENCY)
        self.__UiElems.Sampling_Horizontal_Collection_Combobox.setCurrentIndex(Const.DEFAULT_HORZSRC)
        self.__UiElems.Sampling_Vertical_Collection_Combobox.setCurrentIndex(Const.DEFAULT_VERTSRC)
        # TODO sample averaging
        

        # Console
        self.__UiElems.Console_Preformance_Checkbox.setCheckState(1)
        self.__UiElems.Console_Verbose_Checkbox.setCheckState(1)

    #
    # Description:
    #   Function called as emission by stdo        self.linkUiCallbacks()ut replacement. Prints
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
            valueVectorColors = (self.__ColorMap(valueVectors[:, 2] / 255.0) * 255.0).astype(numpy.uint8) # Format is RGBA
            interiorView = byte_view(self.__ScanImage)
            valueVectors[:, 1] = -1 * (valueVectors[:, 1] - (Const.RES_H - 1)) # Flips coordinates so increasing goes from bottom up
            interiorView[valueVectors[:, 1], valueVectors[:, 0], 0] = valueVectorColors[:, 2] # Converts rgba to bgra
            interiorView[valueVectors[:, 1], valueVectors[:, 0], 1] = valueVectorColors[:, 1]
            interiorView[valueVectors[:, 1], valueVectors[:, 0], 2] = valueVectorColors[:, 0]
            interiorView[valueVectors[:, 1], valueVectors[:, 0], 3] = valueVectorColors[:, 3]
            self.__UiElems.Plotter_Label.setPixmap(QPixmap.fromImage(self.__ScanImage).scaled(self.__UiElems.Plotter_Label.width(), self.__UiElems.Plotter_Label.height()))

    #
    # Description:
    #   Starts and stops data acquisiton and waveform generation. Updates button
    #   text as well.
    #
    def toggleScanning(self):
        if(self.__MCUInterface.isScanning()):
            self.__UiElems.Scan_Pushbutton.setText("Start Scanning")
            self.__MCUInterface.pauseEvents()
            self.__registerTh.halt()
        else:
            self.__UiElems.Scan_Pushbutton.setText("Stop Scanning")
            self.__MCUInterface.beginEvents()
            self.__registerTh.commence()

    #
    # Description:
    #   Saves image currenly on display to memory under the "Captures"
    #   folder.
    #
    def saveImage(self):
        settingsString = "[%s, %s]-[%0.2f,%0.2f](Hz)-[%0.2f,%0.2f](Vpp)-[%s, %s](Microns)" % (self.__UiElems.Horizontal_Waveform_Combobox.currentText(), self.__UiElems.Vertical_Waveform_Combobox.currentText(), self.__UiElems.Horizontal_Frequency_Spinbox.value(), self.__UiElems.Vertical_Frequency_Spinbox.value(), self.__UiElems.Horizontal_Amplitude_Spinbox.value(), self.__UiElems.Vertical_Amplitude_Spinbox.value(), self.__currentXLength, self.__currentYLength)
        totalString    = "Capture_%s_%s.bmp" % (datetime.datetime.now().strftime("%Y-%m-%d[%H-%M-%S]"), settingsString)
        if not self.__ScanImage.save(os.path.join(os.getcwd(), 'Captures', totalString), format = "BMP"):
            print("Failed to Save Image")

    #
    # Description:
    #   Clears image currently on monitor.
    #
    def clearScreen(self):
        self.__ScanImage = QImage(Const.PATH_BACKGROUNDIMAGE).scaled(Const.RES_W, Const.RES_H)
        self.__UiElems.Plotter_Label.setPixmap(QPixmap.fromImage(self.__ScanImage).scaled(self.__UiElems.Plotter_Label.width(), self.__UiElems.Plotter_Label.height()))

    #
    # Description:
    #   Does a frequency survey to approximate the impulse response of the system.
    #   See phase demo for details.
    #
    def calibrateLTIModel(self):
        print("LTI Calibration not fully implemented")

    #
    # Description:
    #   Builds a displacement map to capture non-linear displacement distortion
    #   not accounted for by the LTI model.
    #
    def calibrateDisplacementGrid(self):
        print("Displacement Grid Calibration not fully implemented.")

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
    def updateWaveforms(self):
        # Handles vertical
        verticalLabel = self.__UiElems.Vertical_Waveform_Combobox.currentText()
        if verticalLabel in self.__WaveTables: # Is an existing waveform
            self.__MCUInterface.setDacMagnitude(1, self.__UiElems.Vertical_Amplitude_Spinbox.value())
            self.__MCUInterface.setDacFrequency(1, self.__UiElems.Vertical_Frequency_Spinbox.value())
            self.__MCUInterface.setCustomWaveformData(1, self.__WaveTables[verticalLabel])
            self.__MCUInterface.setDacWaveform(1, 4)
            self.__currentYWaveformOpt = self.__UiElems.Vertical_Waveform_Combobox.currentIndex()
        elif verticalLabel == "Load Custom": # Loads new waveform
            directories =  QFileDialog.getOpenFileNames(caption = "Select one or more waveform files.", directory = os.path.join(os.path.abspath(''), "Waveforms"));
            for currentDirectoryIndex in range(len(directories) - 1): # Last item is a status code
                currentDirectory = directories[currentDirectoryIndex]
                if(len(currentDirectory) > 0): # See above
                    self.loadWaveform(currentDirectory[0])
            self.__UiElems.Vertical_Waveform_Combobox.setCurrentIndex(self.__currentYWaveformOpt)
            return
        else:
            print("Error: Invalid Waveform Choice for Vertical")
            return

        # Handles vertical
        horizontalLabel = self.__UiElems.Horizontal_Waveform_Combobox.currentText()
        if horizontalLabel in self.__WaveTables: # Is an existing waveform
            self.__MCUInterface.setDacMagnitude(0, self.__UiElems.Horizontal_Amplitude_Spinbox.value())
            self.__MCUInterface.setDacFrequency(0, self.__UiElems.Horizontal_Frequency_Spinbox.value())
            self.__MCUInterface.setCustomWaveformData(0, self.__WaveTables[horizontalLabel])
            self.__MCUInterface.setDacWaveform(0, 4)
            self.__currentXWaveformOpt = self.__UiElems.Horizontal_Waveform_Combobox.currentIndex()
        elif horizontalLabel == "Load Custom": # Loads new waveform
            directories =  QFileDialog.getOpenFileNames(caption = "Select one or more waveform files.", directory = os.path.join(os.path.abspath(''), "Waveforms"));
            for currentDirectoryIndex in range(len(directories) - 1): # Last item is a status code
                currentDirectory = directories[currentDirectoryIndex]
                if(len(currentDirectory) > 0): # See above
                    self.loadWaveform(currentDirectory[0])
            self.__UiElems.Horizontal_Waveform_Combobox.setCurrentIndex(self.__currentXWaveformOpt)
            return
        else:
            print("Error: Invalid Waveform Choice for Horizontal")
            return

        # Updates
        self.updateSamplingReconstruction()
        # Refreshes MCU
        if(self.__MCUInterface.isScanning()): # If not scanning will take effect on startup anyway
            self.__MCUInterface.pauseEvents()
            self.__MCUInterface.beginEvents()

    #
    # Description
    #   Trims image to smallest bounding box that contains pixels whose alpha
    #   value is greater than 1 (not fully transparent).
    #
    def cropInvisAway(self, image):
        imageInverseMask = numpy.logical_not(numpy.logical_or(image[:, :, 3] == 0, numpy.sum(image[:, :, :], axis = 2) == 255 * 4)) # Areas where plotting occured have high alpha values, others have an alpha value of zero or are white
        imageHorizontalSums = numpy.sum(imageInverseMask, axis = 0)
        nonZeroHoriz = numpy.nonzero(imageHorizontalSums)[0]
        firstHoriz   = nonZeroHoriz[0]
        lastHoriz    = nonZeroHoriz[-1]
        imageVerticalSums = numpy.sum(imageInverseMask, axis = 1)
        nonZeroVert  = numpy.nonzero(imageVerticalSums)[0]
        firstVert    = nonZeroVert[0]
        lastVert     = nonZeroVert[-1]
        croppedImage = image[(firstVert):(lastVert + 2), (firstHoriz):(lastHoriz + 2), :]
        return croppedImage

    #
    # Description
    #   Adds scale labels to edges of the image in microns. If None is passed
    #   for xMaxMicrons or yMaxMicrons than the corresponding axis is set to
    #   appear blank.
    #
    def __updateXAxisLabel(self, xMaxMicrons):
        xAxisImage = numpy.zeros((10, 10, 4)) # Does not really matter, just has to be x, x, 4 b/c it will be scaled
        if xMaxMicrons is not None and xMaxMicrons > 0.0:
            fig, ax = plt.subplots(dpi = 300)
            ax.set_aspect(0.1)
            ax.set_yticks([])
            ax.tick_params(
                axis='y',          # changes apply to the x-axis
                which='both',      # both major and minor ticks are affected
                bottom=False,      # ticks along the bottom edge are off
                top=False,         # ticks along the top edge are off
                labelbottom=False) # labels along the bottom edge are off
            ax.set_xlim(0, xMaxMicrons)
            xTick_objects = ax.xaxis.get_major_ticks()
            xTick_objects[0].label1.set_horizontalalignment('left')   # left align first tick
            xTick_objects[-1].label1.set_horizontalalignment('right') # right align last tick
            plt.xlabel("Microns")
            # > Gets canvas buffer
            canvas = FigureCanvasAgg(fig);
            canvas.draw();
            s, (width, height) = canvas.print_to_buffer()
            xAxisImage = self.cropInvisAway(numpy.frombuffer(s, numpy.uint8).reshape((height, width, 4)))

        self.__UiElems.Horizontal_Scale_Label.setPixmap(QPixmap.fromImage(array2qimage(xAxisImage.copy()).scaled(self.__UiElems.Horizontal_Scale_Label.width(), self.__UiElems.Horizontal_Scale_Label.height())))

    def __updateYAxisLabel(self, yMaxMicrons):
        yAxisImage = numpy.zeros((10, 10, 4)) # As Alpha is zero will appear blank
        if yMaxMicrons is not None and yMaxMicrons > 0.0:
            fig, ax = plt.subplots(dpi = 300)
            ax.set_aspect(1000)
            ax.set_xticks([])
            ax.tick_params(
                axis='x',          # changes apply to the x-axis
                which='both',      # both major and minor ticks are affected
                bottom=False,      # ticks along the bottom edge are off
                top=False,         # ticks along the top edge are off
                labelbottom=False) # labels along the bottom edge are off
            ax.set_ylim(0, yMaxMicrons)
            yTick_objects = ax.yaxis.get_major_ticks()
            yTick_objects[0].label1.set_verticalalignment('bottom')   # left align first tick
            yTick_objects[-1].label1.set_verticalalignment('top') # right align last tick
            plt.ylabel("Microns")
            # > Gets canvas buffer
            canvas = FigureCanvasAgg(fig);
            canvas.draw();
            s, (width, height) = canvas.print_to_buffer()
            yAxisImage = self.cropInvisAway(numpy.frombuffer(s, numpy.uint8).reshape((height, width, 4)))

        self.__UiElems.Vertical_Scale_Label.setPixmap(QPixmap.fromImage(array2qimage(yAxisImage.copy()).scaled(self.__UiElems.Vertical_Scale_Label.width(), self.__UiElems.Vertical_Scale_Label.height())))

    #
    # Description
    #   Returns an executable callback that filters timestamps based on whether
    #   they correspond to times in the displacement LUT where the stage is rising
    #   (after the lowest displacement point and before the highest point)
    #   or falling. Returns None if no filtering should occur based on the filter
    #   text.
    #
    def getTimestampFilterFunc(self, filteringText, frequency, stableLUT, stableTimes):
        period   = (1.0 / frequency)
        filterFunction  = None
        crestTime   = stableTimes[numpy.argmax(stableLUT)]
        troughTime  = stableTimes[numpy.argmin(stableLUT)]
        if filteringText == "Rising":
            def filterFunction(inputTime):
                inputTime = numpy.fmod(inputTime, period)
                if troughTime < crestTime: # rising during midpoint
                    return numpy.logical_and(troughTime < inputTime, inputTime < crestTime)
                # falling during midpoint
                return numpy.logical_or(troughTime < inputTime, inputTime < crestTime)
        elif filteringText == "Falling":
            def filterFunction(inputTime):
                inputTime = numpy.fmod(inputTime, period) # TODO mod makes me sad
                if crestTime < troughTime: # falling during midpoint
                    return numpy.logical_and(crestTime < inputTime, inputTime < troughTime)
                # rising during midpoint
                return numpy.logical_or(crestTime < inputTime, inputTime < troughTime)
        return filterFunction

    #
    # Desription:
    #   Updates the lookup methods and modes used for
    #   interpreting sampled data.
    #
    def updateSamplingReconstruction(self):
        # What we have
        xPhase          = self.__UiElems.Sampling_Phase_Horizontal_Spinbox.value() # Only used for "Axis Waveform" mode currently
        yPhase          = self.__UiElems.Sampling_Phase_Vertical_Spinbox.value()
        xFrequency      = self.__UiElems.Horizontal_Frequency_Spinbox.value() # Spinbox is hz
        yFrequency      = self.__UiElems.Vertical_Frequency_Spinbox.value()   # Spinbox is hz
        xVpp            = self.__UiElems.Horizontal_Amplitude_Spinbox.value()
        yVpp            = self.__UiElems.Vertical_Amplitude_Spinbox.value()
        currentLUTMode  = self.__UiElems.Sampling_LUT_Combobox.currentText()
        # What will be determined
        xFunction       = None
        yFunction       = None
        xTotalLength    = None # Width of image in microns
        yTotalLength    = None # Height of image in microns
        xFilterFunction = None
        yFilterFunction = None
        xTimeOffset     = 0.0
        yTimeOffset     = 0.0

        # Import new LTI model
        if(currentLUTMode == "Import Model"):
            directories =  QFileDialog.getOpenFileNames(caption = "Select one or more system model files.", directory = os.path.join(os.path.abspath(''), "SysModels"))
            for currentDirectoryIndex in range(len(directories) - 1): # Last item is a status code
                currentDirectory = directories[currentDirectoryIndex]
                if(len(currentDirectory) > 0):
                    self.loadModel(currentDirectory[0])
            self.__UiElems.Sampling_LUT_Combobox.setCurrentIndex(self.__currentLUTModeOpt)
            return
        else:
            self.__currentLUTModeOpt = self.__UiElems.Sampling_LUT_Combobox.currentIndex()

        # Selected an existing system model
        if currentLUTMode in self.__SystemModels:
            systemModel = self.__SystemModels[currentLUTMode]
            # X Axis
            xPeriod     = 1.0 / xFrequency
            xWaveText   = self.__UiElems.Horizontal_Waveform_Combobox.currentText()
            xWaveTable  = self.__WaveTables[xWaveText]
            xStableTimes, xStableLUT = Analysis.findSteadyStateResp(systemModel, xWaveTable, xFrequency, xVpp)
            xScreenLUT, xTotalLength = Analysis.normalizeDisplacement(xStableLUT, Const.RES_W)
            xFunction     = lambda times: numpy.interp(x = times, xp = xStableTimes, fp = xScreenLUT, period = xPeriod)
            # Y Axis
            yPeriod     = 1.0 / yFrequency
            yWaveText   = self.__UiElems.Vertical_Waveform_Combobox.currentText()
            yWaveTable  = self.__WaveTables[yWaveText]
            yStableTimes, yStableLUT = Analysis.findSteadyStateResp(systemModel, yWaveTable, yFrequency, yVpp)
            yScreenLUT, yTotalLength = Analysis.normalizeDisplacement(yStableLUT, Const.RES_H)
            yFunction     = lambda times: numpy.interp(x = times, xp = yStableTimes, fp = yScreenLUT, period = yPeriod)

            # Sets filter
            xFilteringText = self.__UiElems.Sampling_Horizontal_Collection_Combobox.currentText()
            xFilterFunction = self.getTimestampFilterFunc(xFilteringText, xFrequency, xScreenLUT, xStableTimes)
            yFilteringText = self.__UiElems.Sampling_Vertical_Collection_Combobox.currentText()
            yFilterFunction = self.getTimestampFilterFunc(yFilteringText, yFrequency, yScreenLUT, yStableTimes)


        # Lays out data into modern art image for testing and calibration
        elif(currentLUTMode == "Linear"):
            xFunction = lambda inputTime : Analysis.sawTooth(inputTime, (Const.RES_W * 0.5) - 1, xFrequency, 0.0)
            yFunction = lambda inputTime : Analysis.sawTooth(inputTime, (Const.RES_H * 0.5) - 1, yFrequency, 0.0)

        # Assumes that system plant is 1 (no distortion) and allows for manual phase adjustment
        elif currentLUTMode == "Axis Waveform":
            # X Axis
            xPeriod       = 1.0 / xFrequency
            xWaveText     = self.__UiElems.Horizontal_Waveform_Combobox.currentText()
            xWaveTable    = self.__WaveTables[xWaveText]
            xStableLUT    = numpy.append(xWaveTable, xWaveTable[0]) # Forces wraparound
            xStableTimes  = numpy.linspace(start = 0, stop = xPeriod, num = xStableLUT.shape[0])
            xScreenLUT, _ = Analysis.normalizeDisplacement(xStableLUT, Const.RES_W)
            xFunction     = lambda times: numpy.interp(x = times, xp = xStableTimes, fp = xScreenLUT, period = xPeriod)
            # Y Axis
            yPeriod       = 1.0 / yFrequency
            yWaveText     = self.__UiElems.Vertical_Waveform_Combobox.currentText()
            yWaveTable    = self.__WaveTables[yWaveText]
            yStableLUT    = numpy.append(yWaveTable, yWaveTable[0]) # Forces wraparound
            yStableTimes  = numpy.linspace(start = 0, stop = yPeriod, num = yStableLUT.shape[0])
            yScreenLUT, _ = Analysis.normalizeDisplacement(yStableLUT, Const.RES_H)
            yFunction     = lambda times: numpy.interp(x = times, xp = yStableTimes, fp = yScreenLUT, period = yPeriod)

            # Sets filter
            xFilteringText = self.__UiElems.Sampling_Horizontal_Collection_Combobox.currentText()
            xFilterFunction = self.getTimestampFilterFunc(xFilteringText, xFrequency, xScreenLUT, xStableTimes)
            yFilteringText = self.__UiElems.Sampling_Vertical_Collection_Combobox.currentText()
            yFilterFunction = self.getTimestampFilterFunc(yFilteringText, yFrequency, yScreenLUT, yStableTimes)

            # Assigns offset
            xTimeOffset = xPhase * (1.0 / xFrequency)
            yTimeOffset = yPhase * (1.0 / yFrequency)

        else:
            print("Error: Main_updateSamplingReconstruction, bad mode '%s'" % (currentLUTMode))
            return

        # Sets reconstruction functions
        if(xFunction is not None and yFunction is not None):
            self.__registerTh.setDataTranslateX(xFunction)
            self.__registerTh.setDataTranslateY(yFunction)
        else:
            print("Error: Main_updateSamplingReconstruction, bad translation functions")
        # Sets filtering function
        self.__registerTh.setDataFilterX(xFilterFunction)
        self.__registerTh.setDataFilterY(yFilterFunction)
        # Sets time offset
        self.__registerTh.setDataOffsetX(xTimeOffset)
        self.__registerTh.setDataOffsetY(yTimeOffset)
        # Sets axis labels
        if self.__currentXLength != xTotalLength:
            self.__updateXAxisLabel(xTotalLength)
            self.__currentXLength = xTotalLength

        if self.__currentYLength != yTotalLength:
            self.__updateYAxisLabel(yTotalLength)
            self.__currentYLength = yTotalLength

    #
    # Description:
    #   Increases sampling frequency.
    #
    def updateSamplingFrequency(self):
        newFrequency = self.__UiElems.Sampling_Frequency_Spinbox.value() * 1000.0 # Spinbox shows kHz, need to provide hz
        self.__MCUInterface.setAdcFrequency(newFrequency)
        if(self.__MCUInterface.isScanning()):
            self.__MCUInterface.pauseEvents()
            self.__MCUInterface.beginEvents()

if __name__ == "__main__":
    if doChangeCPU:
        P = psutil.Process()
        P.cpu_affinity([0])
   # P.nice(psutil.HIGH_PRIORITY_CLASS)
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    window = TestBench()
    window.show()
    exitStatus = app.exec_()
    sys.exit(exitStatus)
    
    
