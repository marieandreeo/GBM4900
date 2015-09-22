# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Eddie\Documents\Projet\articular-measures\LMPY\filesUi\mainPage.ui'
#
# Created: Wed Apr 08 20:33:43 2015
#      by: pyside-uic 0.2.14 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
import os

global path_script
path_script = os.path.dirname(__file__) + '/'
# Main du UI
class Ui_MainWindow(object):
    global path_script
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 500)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 500))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(path_script+"/filesUi/imagesUi/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "OPTIGON", None, QtGui.QApplication.UnicodeUTF8))

