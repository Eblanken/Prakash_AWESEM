# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Testbench.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Vertical_Amplitude_Spinbox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.Vertical_Amplitude_Spinbox.setGeometry(QtCore.QRect(540, 60, 111, 24))
        self.Vertical_Amplitude_Spinbox.setKeyboardTracking(False)
        self.Vertical_Amplitude_Spinbox.setMaximum(3.3)
        self.Vertical_Amplitude_Spinbox.setSingleStep(0.1)
        self.Vertical_Amplitude_Spinbox.setObjectName("Vertical_Amplitude_Spinbox")
        self.Vertical_Frequency_Spinbox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.Vertical_Frequency_Spinbox.setGeometry(QtCore.QRect(540, 90, 111, 24))
        self.Vertical_Frequency_Spinbox.setKeyboardTracking(False)
        self.Vertical_Frequency_Spinbox.setMinimum(0.01)
        self.Vertical_Frequency_Spinbox.setMaximum(99.0)
        self.Vertical_Frequency_Spinbox.setSingleStep(0.01)
        self.Vertical_Frequency_Spinbox.setObjectName("Vertical_Frequency_Spinbox")
        self.Horizontal_Frequency_Spinbox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.Horizontal_Frequency_Spinbox.setGeometry(QtCore.QRect(540, 200, 111, 24))
        self.Horizontal_Frequency_Spinbox.setKeyboardTracking(False)
        self.Horizontal_Frequency_Spinbox.setMinimum(0.01)
        self.Horizontal_Frequency_Spinbox.setMaximum(99.0)
        self.Horizontal_Frequency_Spinbox.setSingleStep(0.01)
        self.Horizontal_Frequency_Spinbox.setObjectName("Horizontal_Frequency_Spinbox")
        self.Horizontal_Amplitude_Spinbox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.Horizontal_Amplitude_Spinbox.setGeometry(QtCore.QRect(540, 170, 111, 24))
        self.Horizontal_Amplitude_Spinbox.setKeyboardTracking(False)
        self.Horizontal_Amplitude_Spinbox.setMaximum(3.3)
        self.Horizontal_Amplitude_Spinbox.setSingleStep(0.1)
        self.Horizontal_Amplitude_Spinbox.setObjectName("Horizontal_Amplitude_Spinbox")
        self.Horizontal_Title_Label = QtWidgets.QLabel(self.centralwidget)
        self.Horizontal_Title_Label.setGeometry(QtCore.QRect(540, 120, 241, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Horizontal_Title_Label.setFont(font)
        self.Horizontal_Title_Label.setObjectName("Horizontal_Title_Label")
        self.Vertical_Title_Label = QtWidgets.QLabel(self.centralwidget)
        self.Vertical_Title_Label.setGeometry(QtCore.QRect(540, 10, 191, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Vertical_Title_Label.setFont(font)
        self.Vertical_Title_Label.setObjectName("Vertical_Title_Label")
        self.Horizontal_Amplitude_Label = QtWidgets.QLabel(self.centralwidget)
        self.Horizontal_Amplitude_Label.setGeometry(QtCore.QRect(660, 170, 111, 21))
        self.Horizontal_Amplitude_Label.setObjectName("Horizontal_Amplitude_Label")
        self.Horizontal_Frequency_Label = QtWidgets.QLabel(self.centralwidget)
        self.Horizontal_Frequency_Label.setGeometry(QtCore.QRect(660, 200, 101, 21))
        self.Horizontal_Frequency_Label.setObjectName("Horizontal_Frequency_Label")
        self.Vertical_Waveform_Combobox = QtWidgets.QComboBox(self.centralwidget)
        self.Vertical_Waveform_Combobox.setGeometry(QtCore.QRect(540, 30, 111, 21))
        self.Vertical_Waveform_Combobox.setObjectName("Vertical_Waveform_Combobox")
        self.Vertical_Waveform_Combobox.addItem("")
        self.Vertical_Waveform_Combobox.addItem("")
        self.Vertical_Waveform_Combobox.addItem("")
        self.Horizontal_Waveform_Combobox = QtWidgets.QComboBox(self.centralwidget)
        self.Horizontal_Waveform_Combobox.setGeometry(QtCore.QRect(540, 140, 111, 20))
        self.Horizontal_Waveform_Combobox.setObjectName("Horizontal_Waveform_Combobox")
        self.Horizontal_Waveform_Combobox.addItem("")
        self.Horizontal_Waveform_Combobox.addItem("")
        self.Horizontal_Waveform_Combobox.addItem("")
        self.Vertical_Amplitude_Label = QtWidgets.QLabel(self.centralwidget)
        self.Vertical_Amplitude_Label.setGeometry(QtCore.QRect(660, 60, 101, 21))
        self.Vertical_Amplitude_Label.setObjectName("Vertical_Amplitude_Label")
        self.Vertical_Frequency_Label = QtWidgets.QLabel(self.centralwidget)
        self.Vertical_Frequency_Label.setGeometry(QtCore.QRect(660, 90, 101, 21))
        self.Vertical_Frequency_Label.setObjectName("Vertical_Frequency_Label")
        self.Save_Pushbutton = QtWidgets.QPushButton(self.centralwidget)
        self.Save_Pushbutton.setGeometry(QtCore.QRect(150, 510, 131, 32))
        self.Save_Pushbutton.setObjectName("Save_Pushbutton")
        self.Sampling_Title_Label = QtWidgets.QLabel(self.centralwidget)
        self.Sampling_Title_Label.setGeometry(QtCore.QRect(540, 230, 181, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Sampling_Title_Label.setFont(font)
        self.Sampling_Title_Label.setObjectName("Sampling_Title_Label")
        self.Sampling_Frequency_Spinbox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.Sampling_Frequency_Spinbox.setGeometry(QtCore.QRect(540, 250, 111, 24))
        self.Sampling_Frequency_Spinbox.setKeyboardTracking(False)
        self.Sampling_Frequency_Spinbox.setMaximum(50.0)
        self.Sampling_Frequency_Spinbox.setProperty("value", 20.0)
        self.Sampling_Frequency_Spinbox.setObjectName("Sampling_Frequency_Spinbox")
        self.Sampling_Frequency_Label = QtWidgets.QLabel(self.centralwidget)
        self.Sampling_Frequency_Label.setGeometry(QtCore.QRect(660, 250, 101, 21))
        self.Sampling_Frequency_Label.setObjectName("Sampling_Frequency_Label")
        self.Sampling_Averages_Label = QtWidgets.QLabel(self.centralwidget)
        self.Sampling_Averages_Label.setGeometry(QtCore.QRect(660, 280, 101, 21))
        self.Sampling_Averages_Label.setObjectName("Sampling_Averages_Label")
        self.Sampling_Averages_Spinbox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.Sampling_Averages_Spinbox.setGeometry(QtCore.QRect(540, 280, 111, 24))
        self.Sampling_Averages_Spinbox.setKeyboardTracking(False)
        self.Sampling_Averages_Spinbox.setDecimals(0)
        self.Sampling_Averages_Spinbox.setMaximum(50.0)
        self.Sampling_Averages_Spinbox.setProperty("value", 20.0)
        self.Sampling_Averages_Spinbox.setObjectName("Sampling_Averages_Spinbox")
        self.Scan_Pushbutton = QtWidgets.QPushButton(self.centralwidget)
        self.Scan_Pushbutton.setGeometry(QtCore.QRect(10, 510, 131, 32))
        self.Scan_Pushbutton.setObjectName("Scan_Pushbutton")
        self.Sampling_LUT_Combobox = QtWidgets.QComboBox(self.centralwidget)
        self.Sampling_LUT_Combobox.setGeometry(QtCore.QRect(540, 340, 111, 21))
        self.Sampling_LUT_Combobox.setObjectName("Sampling_LUT_Combobox")
        self.Sampling_LUT_Combobox.addItem("")
        self.Sampling_LUT_Combobox.addItem("")
        self.Sampling_LUT_Label = QtWidgets.QLabel(self.centralwidget)
        self.Sampling_LUT_Label.setGeometry(QtCore.QRect(660, 340, 101, 21))
        self.Sampling_LUT_Label.setObjectName("Sampling_LUT_Label")
        self.Sampling_Phase_Horizontal_Spinbox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.Sampling_Phase_Horizontal_Spinbox.setGeometry(QtCore.QRect(540, 370, 111, 24))
        self.Sampling_Phase_Horizontal_Spinbox.setKeyboardTracking(False)
        self.Sampling_Phase_Horizontal_Spinbox.setMaximum(0.5)
        self.Sampling_Phase_Horizontal_Spinbox.setMinimum(-0.5)
        self.Sampling_Phase_Horizontal_Spinbox.setSingleStep(0.01)
        self.Sampling_Phase_Horizontal_Spinbox.setProperty("value", 0.0)
        self.Sampling_Phase_Horizontal_Spinbox.setObjectName("Sampling_Phase_Horizontal_Spinbox")
        self.Sampling_Phase_Horizonal_Label = QtWidgets.QLabel(self.centralwidget)
        self.Sampling_Phase_Horizonal_Label.setGeometry(QtCore.QRect(660, 370, 121, 21))
        self.Sampling_Phase_Horizonal_Label.setObjectName("Sampling_Phase_Horizonal_Label")
        self.Console_Output_TextBox = QtWidgets.QTextEdit(self.centralwidget)
        self.Console_Output_TextBox.setGeometry(QtCore.QRect(530, 460, 231, 41))
        self.Console_Output_TextBox.setObjectName("Console_Output_TextBox")
        self.Console_Title_Label = QtWidgets.QLabel(self.centralwidget)
        self.Console_Title_Label.setGeometry(QtCore.QRect(540, 430, 181, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Console_Title_Label.setFont(font)
        self.Console_Title_Label.setObjectName("Console_Title_Label")
        self.Console_Verbose_Checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.Console_Verbose_Checkbox.setGeometry(QtCore.QRect(540, 500, 72, 20))
        self.Console_Verbose_Checkbox.setObjectName("Console_Verbose_Checkbox")
        self.Console_Preformance_Checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.Console_Preformance_Checkbox.setGeometry(QtCore.QRect(620, 500, 91, 20))
        self.Console_Preformance_Checkbox.setObjectName("Console_Preformance_Checkbox")
        self.Plotter_Label = QtWidgets.QLabel(self.centralwidget)
        self.Plotter_Label.setGeometry(QtCore.QRect(0, 0, 500, 500))
        self.Plotter_Label.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Plotter_Label.setText("")
        self.Plotter_Label.setObjectName("Plotter_Label")
        self.Sampling_Phase_Vertical_Spinbox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.Sampling_Phase_Vertical_Spinbox.setGeometry(QtCore.QRect(540, 400, 111, 24))
        self.Sampling_Phase_Vertical_Spinbox.setKeyboardTracking(False)
        self.Sampling_Phase_Vertical_Spinbox.setMaximum(0.5)
        self.Sampling_Phase_Vertical_Spinbox.setMinimum(-0.5)
        self.Sampling_Phase_Vertical_Spinbox.setSingleStep(0.01)
        self.Sampling_Phase_Vertical_Spinbox.setProperty("value", 0.0)
        self.Sampling_Phase_Vertical_Spinbox.setObjectName("Sampling_Phase_Vertical_Spinbox")
        self.Sampling_Phase_Vertical_Label = QtWidgets.QLabel(self.centralwidget)
        self.Sampling_Phase_Vertical_Label.setGeometry(QtCore.QRect(660, 400, 121, 21))
        self.Sampling_Phase_Vertical_Label.setObjectName("Sampling_Phase_Vertical_Label")
        self.Vertical_Waveform_Label = QtWidgets.QLabel(self.centralwidget)
        self.Vertical_Waveform_Label.setGeometry(QtCore.QRect(660, 30, 101, 21))
        self.Vertical_Waveform_Label.setObjectName("Vertical_Waveform_Label")
        self.Horizontal_Waveform_Label = QtWidgets.QLabel(self.centralwidget)
        self.Horizontal_Waveform_Label.setGeometry(QtCore.QRect(660, 140, 101, 21))
        self.Horizontal_Waveform_Label.setObjectName("Horizontal_Waveform_Label")
        self.Sampling_Collection_Label = QtWidgets.QLabel(self.centralwidget)
        self.Sampling_Collection_Label.setGeometry(QtCore.QRect(660, 310, 101, 21))
        self.Sampling_Collection_Label.setObjectName("Sampling_Collection_Label")
        self.Sampling_Collection_Combobox = QtWidgets.QComboBox(self.centralwidget)
        self.Sampling_Collection_Combobox.setGeometry(QtCore.QRect(540, 310, 111, 21))
        self.Sampling_Collection_Combobox.setObjectName("Sampling_Collection_Combobox")
        self.Sampling_Collection_Combobox.addItem("")
        self.Sampling_Collection_Combobox.addItem("")
        self.Sampling_Collection_Combobox.addItem("")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionLoad_Calibration = QtWidgets.QAction(MainWindow)
        self.actionLoad_Calibration.setObjectName("actionLoad_Calibration")
        self.actionStart_Calibration = QtWidgets.QAction(MainWindow)
        self.actionStart_Calibration.setObjectName("actionStart_Calibration")
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionLoad_Calibration)
        self.menuFile.addAction(self.actionStart_Calibration)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Horizontal_Title_Label.setText(_translate("MainWindow", "Horizontal Axis"))
        self.Vertical_Title_Label.setText(_translate("MainWindow", "Vertical Axis"))
        self.Horizontal_Amplitude_Label.setText(_translate("MainWindow", "Amplitude (Vpp)"))
        self.Horizontal_Frequency_Label.setText(_translate("MainWindow", "Frequency (Hz)"))
        self.Vertical_Waveform_Combobox.setItemText(0, _translate("MainWindow", "Sine"))
        self.Vertical_Waveform_Combobox.setItemText(1, _translate("MainWindow", "Triangle"))
        self.Vertical_Waveform_Combobox.setItemText(2, _translate("MainWindow", "Sawtooth"))
        self.Horizontal_Waveform_Combobox.setItemText(0, _translate("MainWindow", "Sine"))
        self.Horizontal_Waveform_Combobox.setItemText(1, _translate("MainWindow", "Triangle"))
        self.Horizontal_Waveform_Combobox.setItemText(2, _translate("MainWindow", "Sawtooth"))
        self.Vertical_Amplitude_Label.setText(_translate("MainWindow", "Amplitude (Vpp)"))
        self.Vertical_Frequency_Label.setText(_translate("MainWindow", "Frequency (Hz)"))
        self.Save_Pushbutton.setText(_translate("MainWindow", "Clear Screen"))
        self.Sampling_Title_Label.setText(_translate("MainWindow", "Sampling"))
        self.Sampling_Frequency_Label.setText(_translate("MainWindow", "Frequency (kHz)"))
        self.Sampling_Averages_Label.setText(_translate("MainWindow", "Averages"))
        self.Scan_Pushbutton.setText(_translate("MainWindow", "Start Scanning"))
        self.Sampling_LUT_Combobox.setItemText(0, _translate("MainWindow", "Axis Waveform"))
        self.Sampling_LUT_Combobox.setItemText(1, _translate("MainWindow", "Linear"))
        self.Sampling_LUT_Label.setText(_translate("MainWindow", "LUT Mode"))
        self.Sampling_Phase_Horizonal_Label.setText(_translate("MainWindow", "Horizontal Phase (*2Pi)"))
        self.Console_Title_Label.setText(_translate("MainWindow", "Console Output"))
        self.Console_Verbose_Checkbox.setText(_translate("MainWindow", "Verbose"))
        self.Console_Preformance_Checkbox.setText(_translate("MainWindow", "Preformance"))
        self.Sampling_Phase_Vertical_Label.setText(_translate("MainWindow", "Vertical Phase (*2Pi)"))
        self.Vertical_Waveform_Label.setText(_translate("MainWindow", "Driving Waveform"))
        self.Horizontal_Waveform_Label.setText(_translate("MainWindow", "Driving Waveform"))
        self.Sampling_Collection_Label.setText(_translate("MainWindow", "Data Collection"))
        self.Sampling_Collection_Combobox.setItemText(0, _translate("MainWindow", "Falling Fast"))
        self.Sampling_Collection_Combobox.setItemText(1, _translate("MainWindow", "Rising Fast"))
        self.Sampling_Collection_Combobox.setItemText(2, _translate("MainWindow", "All"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave.setText(_translate("MainWindow", "Save Calibration"))
        self.actionLoad_Calibration.setText(_translate("MainWindow", "Load Calibration"))
        self.actionStart_Calibration.setText(_translate("MainWindow", "Start Calibration"))

