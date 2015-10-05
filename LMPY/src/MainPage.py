#!/usr/bin/python
# -*- coding: utf-8 -*-

import pageUi                       # Import py of Qt Designer
import mainPageUi
from PySide import QtGui, QtCore    # For GUI functions
from Page import *

class MainPage(QtGui.QMainWindow, mainPageUi.Ui_MainWindow):

    # Function for initialisation MainWindow
    def __init__(self, parent=None):

        # Initialisation of class
        super(MainPage, self).__init__(parent)
        self.setupUi(self)

        # Create tab widget for GUI
        self.widget = Page()

        # Set central widget of main window
        self.setCentralWidget(self.widget)

        # Status bar font
        self.statusbar.setStyleSheet("font: italic 100 14pt \"Book Antiqua\";\n""color: rgb(255, 0, 0);\n")
