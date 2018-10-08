# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 650)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 650))
        MainWindow.setMaximumSize(QtCore.QSize(1000, 650))
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.CaptureB = QtWidgets.QPushButton(self.centralWidget)
        self.CaptureB.setGeometry(QtCore.QRect(800, 50, 141, 31))
        self.CaptureB.setObjectName("CaptureB")
        self.ScanB = QtWidgets.QPushButton(self.centralWidget)
        self.ScanB.setGeometry(QtCore.QRect(610, 50, 131, 31))
        self.ScanB.setCheckable(True)
        self.ScanB.setObjectName("ScanB")
        self.RefreshLabel = QtWidgets.QLabel(self.centralWidget)
        self.RefreshLabel.setGeometry(QtCore.QRect(620, 487, 161, 31))
        self.RefreshLabel.setObjectName("RefreshLabel")
        self.refreshRate = QtWidgets.QSpinBox(self.centralWidget)
        self.refreshRate.setGeometry(QtCore.QRect(780, 491, 45, 25))
        self.refreshRate.setAccelerated(True)
        self.refreshRate.setCorrectionMode(QtWidgets.QAbstractSpinBox.CorrectToNearestValue)
        self.refreshRate.setKeyboardTracking(True)
        self.refreshRate.setMinimum(10)
        self.refreshRate.setMaximum(60)
        self.refreshRate.setObjectName("refreshRate")
        self.ref_secondsT = QtWidgets.QLabel(self.centralWidget)
        self.ref_secondsT.setGeometry(QtCore.QRect(840, 490, 71, 24))
        self.ref_secondsT.setObjectName("ref_secondsT")
        self.XZoomGroup = QtWidgets.QGroupBox(self.centralWidget)
        self.XZoomGroup.setGeometry(QtCore.QRect(570, 100, 401, 171))
        self.XZoomGroup.setTitle("")
        self.XZoomGroup.setObjectName("XZoomGroup")
        self.XResetB = QtWidgets.QPushButton(self.XZoomGroup)
        self.XResetB.setGeometry(QtCore.QRect(240, 130, 93, 28))
        self.XResetB.setObjectName("XResetB")
        self.XUpdateB = QtWidgets.QPushButton(self.XZoomGroup)
        self.XUpdateB.setGeometry(QtCore.QRect(56, 130, 121, 28))
        self.XUpdateB.setObjectName("XUpdateB")
        self.label_14 = QtWidgets.QLabel(self.XZoomGroup)
        self.label_14.setGeometry(QtCore.QRect(234, 67, 16, 19))
        self.label_14.setText("")
        self.label_14.setObjectName("label_14")
        self.label_11 = QtWidgets.QLabel(self.XZoomGroup)
        self.label_11.setGeometry(QtCore.QRect(138, 67, 16, 19))
        self.label_11.setText("")
        self.label_11.setObjectName("label_11")
        self.XScanLabel = QtWidgets.QLabel(self.XZoomGroup)
        self.XScanLabel.setGeometry(QtCore.QRect(52, 23, 309, 36))
        self.XScanLabel.setObjectName("XScanLabel")
        self.label_6 = QtWidgets.QLabel(self.XZoomGroup)
        self.label_6.setGeometry(QtCore.QRect(154, 70, 27, 19))
        self.label_6.setObjectName("label_6")
        self.XZoomSlider = QtWidgets.QSlider(self.XZoomGroup)
        self.XZoomSlider.setGeometry(QtCore.QRect(70, 93, 271, 27))
        self.XZoomSlider.setMinimum(0)
        self.XZoomSlider.setMaximum(330)
        self.XZoomSlider.setSingleStep(5)
        self.XZoomSlider.setPageStep(20)
        self.XZoomSlider.setProperty("value", 165)
        self.XZoomSlider.setSliderPosition(165)
        self.XZoomSlider.setOrientation(QtCore.Qt.Horizontal)
        self.XZoomSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.XZoomSlider.setTickInterval(10)
        self.XZoomSlider.setObjectName("XZoomSlider")
        self.label_12 = QtWidgets.QLabel(self.XZoomGroup)
        self.label_12.setGeometry(QtCore.QRect(186, 67, 16, 19))
        self.label_12.setText("")
        self.label_12.setObjectName("label_12")
        self.label_2 = QtWidgets.QLabel(self.XZoomGroup)
        self.label_2.setGeometry(QtCore.QRect(7, 91, 61, 27))
        self.label_2.setObjectName("label_2")
        self.label_8 = QtWidgets.QLabel(self.XZoomGroup)
        self.label_8.setGeometry(QtCore.QRect(241, 70, 27, 19))
        self.label_8.setObjectName("label_8")
        self.label_3 = QtWidgets.QLabel(self.XZoomGroup)
        self.label_3.setGeometry(QtCore.QRect(350, 93, 41, 21))
        self.label_3.setObjectName("label_3")
        self.label_5 = QtWidgets.QLabel(self.XZoomGroup)
        self.label_5.setGeometry(QtCore.QRect(326, 70, 27, 19))
        self.label_5.setObjectName("label_5")
        self.label_7 = QtWidgets.QLabel(self.XZoomGroup)
        self.label_7.setGeometry(QtCore.QRect(70, 70, 27, 19))
        self.label_7.setObjectName("label_7")
        self.XZoomGroup_2 = QtWidgets.QGroupBox(self.centralWidget)
        self.XZoomGroup_2.setGeometry(QtCore.QRect(570, 290, 401, 171))
        self.XZoomGroup_2.setTitle("")
        self.XZoomGroup_2.setObjectName("XZoomGroup_2")
        self.YResetB = QtWidgets.QPushButton(self.XZoomGroup_2)
        self.YResetB.setGeometry(QtCore.QRect(240, 130, 93, 28))
        self.YResetB.setObjectName("YResetB")
        self.YUpdateB = QtWidgets.QPushButton(self.XZoomGroup_2)
        self.YUpdateB.setGeometry(QtCore.QRect(56, 130, 121, 28))
        self.YUpdateB.setObjectName("YUpdateB")
        self.label_15 = QtWidgets.QLabel(self.XZoomGroup_2)
        self.label_15.setGeometry(QtCore.QRect(234, 67, 16, 19))
        self.label_15.setText("")
        self.label_15.setObjectName("label_15")
        self.label_13 = QtWidgets.QLabel(self.XZoomGroup_2)
        self.label_13.setGeometry(QtCore.QRect(138, 67, 16, 19))
        self.label_13.setText("")
        self.label_13.setObjectName("label_13")
        self.YScanLabel = QtWidgets.QLabel(self.XZoomGroup_2)
        self.YScanLabel.setGeometry(QtCore.QRect(52, 23, 309, 36))
        self.YScanLabel.setObjectName("YScanLabel")
        self.label_9 = QtWidgets.QLabel(self.XZoomGroup_2)
        self.label_9.setGeometry(QtCore.QRect(154, 70, 27, 19))
        self.label_9.setObjectName("label_9")
        self.YZoomSlider = QtWidgets.QSlider(self.XZoomGroup_2)
        self.YZoomSlider.setGeometry(QtCore.QRect(70, 93, 271, 27))
        self.YZoomSlider.setMinimum(0)
        self.YZoomSlider.setMaximum(330)
        self.YZoomSlider.setSingleStep(5)
        self.YZoomSlider.setPageStep(20)
        self.YZoomSlider.setProperty("value", 165)
        self.YZoomSlider.setSliderPosition(165)
        self.YZoomSlider.setOrientation(QtCore.Qt.Horizontal)
        self.YZoomSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.YZoomSlider.setTickInterval(10)
        self.YZoomSlider.setObjectName("YZoomSlider")
        self.label_16 = QtWidgets.QLabel(self.XZoomGroup_2)
        self.label_16.setGeometry(QtCore.QRect(186, 67, 16, 19))
        self.label_16.setText("")
        self.label_16.setObjectName("label_16")
        self.label_4 = QtWidgets.QLabel(self.XZoomGroup_2)
        self.label_4.setGeometry(QtCore.QRect(7, 91, 61, 27))
        self.label_4.setObjectName("label_4")
        self.label_10 = QtWidgets.QLabel(self.XZoomGroup_2)
        self.label_10.setGeometry(QtCore.QRect(241, 70, 27, 19))
        self.label_10.setObjectName("label_10")
        self.label_17 = QtWidgets.QLabel(self.XZoomGroup_2)
        self.label_17.setGeometry(QtCore.QRect(350, 93, 41, 21))
        self.label_17.setObjectName("label_17")
        self.label_18 = QtWidgets.QLabel(self.XZoomGroup_2)
        self.label_18.setGeometry(QtCore.QRect(326, 70, 27, 19))
        self.label_18.setObjectName("label_18")
        self.label_19 = QtWidgets.QLabel(self.XZoomGroup_2)
        self.label_19.setGeometry(QtCore.QRect(70, 70, 27, 19))
        self.label_19.setObjectName("label_19")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1000, 26))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menuBar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QtWidgets.QMenu(self.menuBar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.CaptureB.setText(_translate("MainWindow", "Capture Image"))
        self.ScanB.setText(_translate("MainWindow", "Scan"))
        self.RefreshLabel.setToolTip(_translate("MainWindow",
                                                "<html><head/><body><p>Change the time it takes for a full image refresh. Longer time ensures higher accuracy and less noise.</p></body></html>"))
        self.RefreshLabel.setText(_translate("MainWindow",
                                             "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; color:#00007f;\">Refresh Rate: </span></p></body></html>"))
        self.ref_secondsT.setText(_translate("MainWindow",
                                             "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">seconds</span></p></body></html>"))
        self.XResetB.setText(_translate("MainWindow", "Reset"))
        self.XUpdateB.setText(_translate("MainWindow", "Update"))
        self.XScanLabel.setToolTip(_translate("MainWindow",
                                              "<html><head/><body><p>Change zoom level across horizontal axis.</p></body></html>"))
        self.XScanLabel.setText(_translate("MainWindow",
                                           "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; color:#00007f;\">X-Magnitude (Vpp)</span></p></body></html>"))
        self.label_6.setText(_translate("MainWindow",
                                        "<html><head/><body><p><span style=\" vertical-align:super;\"></span></p></body></html>"))
        self.label_2.setText(_translate("MainWindow",
                                        "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">0</span><span style=\" font-size:10pt; font-weight:600; font-style:italic;\"></span></p></body></html>"))
        self.label_8.setText(_translate("MainWindow",
                                        "<html><head/><body><p><span style=\" vertical-align:super;\"></span></p></body></html>"))
        self.label_3.setText(_translate("MainWindow",
                                        "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">3.3</span><span style=\" font-size:10pt; font-weight:600; font-style:italic;\"></span></p></body></html>"))
        self.label_5.setText(_translate("MainWindow",
                                        "<html><head/><body><p><span style=\" vertical-align:super;\"></span></p></body></html>"))
        self.label_7.setText(_translate("MainWindow",
                                        "<html><head/><body><p><span style=\" vertical-align:super;\"></span></p></body></html>"))
        self.YResetB.setText(_translate("MainWindow", "Reset"))
        self.YUpdateB.setText(_translate("MainWindow", "Update"))
        self.YScanLabel.setToolTip(
            _translate("MainWindow", "<html><head/><body><p>Change zoom level across vertical axis.</p></body></html>"))
        self.YScanLabel.setText(_translate("MainWindow",
                                           "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; color:#00007f;\">Y-Magnitude (Vpp)</span></p></body></html>"))
        self.label_9.setText(_translate("MainWindow",
                                        "<html><head/><body><p><span style=\" vertical-align:super;\"></span></p></body></html>"))
        self.label_4.setText(_translate("MainWindow",
                                        "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">0</span><span style=\" font-size:8pt; font-weight:600; font-style:italic;\"></span></p></body></html>"))
        self.label_10.setText(_translate("MainWindow",
                                         "<html><head/><body><p><span style=\" vertical-align:super;\"></span></p></body></html>"))
        self.label_17.setText(_translate("MainWindow",
                                         "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">3.3</span><span style=\" font-size:10pt; font-weight:600; font-style:italic;\"></span></p></body></html>"))
        self.label_18.setText(_translate("MainWindow",
                                         "<html><head/><body><p><span style=\" vertical-align:super;\"></span></p></body></html>"))
        self.label_19.setText(_translate("MainWindow",
                                         "<html><head/><body><p><span style=\" vertical-align:super;\"></span></p></body></html>"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
