#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pageUi                       # Import py of Qt Designer
import mainPageUi
from PySide import QtGui, QtCore    # For GUI functions
import Leap
from SampleListener import *
from LeapThread import *

Min, Value, Max = 0, 1, 2                                   # Define type of data
MP, IPP, IPD = 0, 1, 2                                      # Define type of each joint
Thumb, Index, Middle, Ring, Pinky = 0, 1, 2, 3, 4           # Define type of each finger
Left, Right = 0, 1  

User_Choices =  [[Left, Right],                             # List of hand selected by user
                    [[Thumb, [MP, IPP]],                        # Finger joints : [finger 1,[list of joints selected]]
                    [Index, [MP, IPP, IPD]],                    # Finger joints : [finger 2,[list of joints selected]]
                    [Middle, [MP, IPP, IPD]],                   # Finger joints : [finger 3,[list of joints selected]]
                    [Ring, [MP, IPP, IPD]],                     # Finger joints : [finger 4,[list of joints selected]]
                    [Pinky, [MP, IPP, IPD]]]]                   # Finger joints : [finger 5,[list of joints selected]]


class upateThread(QtCore.QThread):

    # Create a signal for angles list
    progress = QtCore.Signal(list)

    # Function for initialisation thread
    def __init__(self,parent=None):
        super(upateThread,self).__init__(parent)    # Initialisation of class
        self.exiting = False                        # Disable thread at beginning of program  
        self.parent = parent

    # Function for running thread
    def run(self):
        print 'run'

    def emitData(self, data):
        # self.progress.emit(data)
        self.parent.updateText(data)


class Page(QtGui.QTabWidget, pageUi.Ui_TabWidget):

    def __init__(self, parent=None):
        super(Page, self).__init__(parent)
        self.setupUi(self)
        self.i = 0
        self.path_script = os.getcwd() + '/'
        self.modeMain = True
         # Save name of angles buttons created in Qt Designer for display
        self.labels = [[[['T_MP_L_Min', 'T_MP_L_Value', 'T_MP_L_Max'], ['T_IPP_L_Min', 'T_IPP_L_Value', 'T_IPP_L_Max']], [['I_MP_L_Min', 'I_MP_L_Value', 'I_MP_L_Max'], ['I_IPP_L_Min', 'I_IPP_L_Value', 'I_IPP_L_Max'], ['I_IPD_L_Min', 'I_IPD_L_Value', 'I_IPD_L_Max']], [['M_MP_L_Min', 'M_MP_L_Value', 'M_MP_L_Max'], ['M_IPP_L_Min', 'M_IPP_L_Value', 'M_IPP_L_Max'], ['M_IPD_L_Min', 'M_IPD_L_Value', 'M_IPD_L_Max']], [['R_MP_L_Min', 'R_MP_L_Value', 'R_MP_L_Max'], ['R_IPP_L_Min', 'R_IPP_L_Value', 'R_IPP_L_Max'], ['R_IPD_L_Min', 'R_IPD_L_Value', 'R_IPD_L_Max']], [['P_MP_L_Min', 'P_MP_L_Value', 'P_MP_L_Max'], ['P_IPP_L_Min', 'P_IPP_L_Value', 'P_IPP_L_Max'], ['P_IPD_L_Min', 'P_IPD_L_Value', 'P_IPD_L_Max']]], [[['T_MP_R_Min', 'T_MP_R_Value', 'T_MP_R_Max'], ['T_IPP_R_Min', 'T_IPP_R_Value', 'T_IPP_R_Max']], [['I_MP_R_Min', 'I_MP_R_Value', 'I_MP_R_Max'], ['I_IPP_R_Min', 'I_IPP_R_Value', 'I_IPP_R_Max'], ['I_IPD_R_Min', 'I_IPD_R_Value', 'I_IPD_R_Max']], [['M_MP_R_Min', 'M_MP_R_Value', 'M_MP_R_Max'], ['M_IPP_R_Min', 'M_IPP_R_Value', 'M_IPP_R_Max'], ['M_IPD_R_Min', 'M_IPD_R_Value', 'M_IPD_R_Max']], [['R_MP_R_Min', 'R_MP_R_Value', 'R_MP_R_Max'], ['R_IPP_R_Min', 'R_IPP_R_Value', 'R_IPP_R_Max'], ['R_IPD_R_Min', 'R_IPD_R_Value', 'R_IPD_R_Max']], [['P_MP_R_Min', 'P_MP_R_Value', 'P_MP_R_Max'], ['P_IPP_R_Min', 'P_IPP_R_Value', 'P_IPP_R_Max'], ['P_IPD_R_Min', 'P_IPD_R_Value', 'P_IPD_R_Max']]]]

        # Save name of angles buttons created in Qt Designer for select user choices
        self.buttons = [[[['Thumb_MP_L', 'Thumb_MP_L', 'Thumb_MP_L'], ['Thumb_IPP_L', 'Thumb_IPP_L', 'Thumb_IPP_L']], [['Index_MP_L', 'Index_MP_L', 'Index_MP_L'], ['Index_IPP_L', 'Index_IPP_L', 'Index_IPP_L'], ['Index_IPD_L', 'Index_IPD_L', 'Index_IPD_L']], [['Middle_MP_L', 'Middle_MP_L', 'Middle_MP_L'], ['Middle_IPP_L', 'Middle_IPP_L', 'Middle_IPP_L'], ['Middle_IPD_L', 'Middle_IPD_L', 'Middle_IPD_L']], [['Ring_MP_L', 'Ring_MP_L', 'Ring_MP_L'], ['Ring_IPP_L', 'Ring_IPP_L', 'Ring_IPP_L'], ['Ring_IPD_L', 'Ring_IPD_L', 'Ring_IPD_L']], [['Pinky_MP_L', 'Pinky_MP_L', 'Pinky_MP_L'], ['Pinky_IPP_L', 'Pinky_IPP_L', 'Pinky_IPP_L'], ['Pinky_IPD_L', 'Pinky_IPD_L', 'Pinky_IPD_L']]], [[['Thumb_MP_R', 'Thumb_MP_R', 'Thumb_MP_R'], ['Thumb_IPP_R', 'Thumb_IPP_R', 'Thumb_IPP_R']], [['Index_MP_R', 'Index_MP_R', 'Index_MP_R'], ['Index_IPP_R', 'Index_IPP_R', 'Index_IPP_R'], ['Index_IPD_R', 'Index_IPD_R', 'Index_IPD_R']], [['Middle_MP_R', 'Middle_MP_R', 'Middle_MP_R'], ['Middle_IPP_R', 'Middle_IPP_R', 'Middle_IPP_R'], ['Middle_IPD_R', 'Middle_IPD_R', 'Middle_IPD_R']], [['Ring_MP_R', 'Ring_MP_R', 'Ring_MP_R'], ['Ring_IPP_R', 'Ring_IPP_R', 'Ring_IPP_R'], ['Ring_IPD_R', 'Ring_IPD_R', 'Ring_IPD_R']], [['Pinky_MP_R', 'Pinky_MP_R', 'Pinky_MP_R'], ['Pinky_IPP_R', 'Pinky_IPP_R', 'Pinky_IPP_R'], ['Pinky_IPD_R', 'Pinky_IPD_R', 'Pinky_IPD_R']]]]

        # Table
        self.cellV = [[[[1, 1, 2], [3, 3, 4]], [[5, 5, 6], [7, 7, 8], [9, 9, 10]], [[11, 11, 12], [13, 13, 14], [15, 15, 16]], [[17, 17, 18], [19, 19, 20], [21, 21, 22]], [[23, 23, 24], [25, 25, 26], [27, 27, 28]]], [[[1, 1, 2], [3, 3, 4]], [[5, 5, 6], [7, 7, 8], [9, 9, 10]], [[11, 11, 12], [13, 13, 14], [15, 15, 16]], [[17, 17, 18], [19, 19, 20], [21, 21, 22]], [[23, 23, 24], [25, 25, 26], [27, 27, 28]]]]
        self.cellH = [[[[3, 3, 3], [3, 3, 3]], [[3, 3, 3], [3, 3, 3], [3, 3, 3]], [[3, 3, 3], [3, 3, 3], [3, 3, 3]], [[3, 3, 3], [3, 3, 3], [3, 3, 3]], [[3, 3, 3], [3, 3, 3], [3, 3, 3]]], [[[7, 7, 7], [7, 7, 7]], [[7, 7, 7], [7, 7, 7], [7, 7, 7]], [[7, 7, 7], [7, 7, 7], [7, 7, 7]], [[7, 7, 7], [7, 7, 7], [7, 7, 7]], [[7, 7, 7], [7, 7, 7], [7, 7, 7]]]]

        # Select all angles
        self.tous.click()

        # Select all two movements
        self.combine.click()

        self.acquisitionMode = False
        self.updateThread = upateThread(self)
        self.leapThread = LeapThread(self.updateThread)

    def copyData(self):
        print 'CopyData'

    def changeModeMainTableau(self):
        print 'ChangeModeMainTableau'
        # Pass to reverse mode
        self.modeMain = not self.modeMain

        # When it is hand mode
        if self.modeMain:

            self.effacer.setEnabled(True)

            self.tableWidget.setVisible(False)
            self.widget_2.setVisible(True)
            self.mains_d_2.setVisible(True)

            # Create icon
            newIcon = QtGui.QIcon()
            newIcon.addPixmap(QtGui.QPixmap(
                self.path_script + "filesUi/imagesUi/table.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

            # Modify icon
            self.Mode_M_T.setIcon(newIcon)

            # Modify text
            self.message_D_3.setText(QtGui.QApplication.translate(
                "TabWidget", "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">VUE DORSALE</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

        # When it is table mode
        if not self.modeMain:

            # Create table

            self.effacer.setEnabled(False)

            self.gridLayout_7.addWidget(self.tableWidget, 2, 2, 1, 4)
            self.tableWidget.horizontalHeader().setDefaultSectionSize(self.widget_2.width() / 8)
            self.tableWidget.verticalHeader().setDefaultSectionSize(self.widget_2.height() / 29)
            self.message_D_3.setText(QtGui.QApplication.translate(
                "TabWidget", "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">TABLEAU</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

            font = QtGui.QFont()
            font.setPointSize(14)
            font.setFamily("Book Antiqua")
            self.tableWidget.setFont(font)

            font.setBold(True)
            item = QtGui.QTableWidgetItem("Main gauche")
            item.setFont(font)
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(0, 0, item)
            self.tableWidget.setSpan(0, 0, 1, 4)

            item = QtGui.QTableWidgetItem("Main droite")
            item.setFont(font)
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(0, 4, item)
            self.tableWidget.setSpan(0, 4, 1, 4)

            item = QtGui.QTableWidgetItem("D1")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(1, 0, item)
            self.tableWidget.setSpan(1, 0, 4, 1)
            item = QtGui.QTableWidgetItem("D1")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(1, 4, item)
            self.tableWidget.setSpan(1, 4, 4, 1)

            item = QtGui.QTableWidgetItem("D2")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(5, 0, item)
            self.tableWidget.setSpan(5, 0, 6, 1)
            item = QtGui.QTableWidgetItem("D2")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(5, 4, item)
            self.tableWidget.setSpan(5, 4, 6, 1)

            item = QtGui.QTableWidgetItem("D3")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(11, 0, item)
            self.tableWidget.setSpan(11, 0, 6, 1)
            item = QtGui.QTableWidgetItem("D3")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(11, 4, item)
            self.tableWidget.setSpan(11, 4, 6, 1)

            item = QtGui.QTableWidgetItem("D4")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(17, 0, item)
            self.tableWidget.setSpan(17, 0, 6, 1)
            item = QtGui.QTableWidgetItem("D4")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(17, 4, item)
            self.tableWidget.setSpan(17, 4, 6, 1)

            item = QtGui.QTableWidgetItem("D5")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(23, 0, item)
            self.tableWidget.setSpan(23, 0, 6, 1)
            item = QtGui.QTableWidgetItem("D5")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(23, 4, item)
            self.tableWidget.setSpan(23, 4, 6, 1)

            item = QtGui.QTableWidgetItem("MP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(1, 1, item)
            self.tableWidget.setSpan(1, 1, 2, 1)
            item = QtGui.QTableWidgetItem("MP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(1, 5, item)
            self.tableWidget.setSpan(1, 5, 2, 1)

            item = QtGui.QTableWidgetItem("MP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(5, 1, item)
            self.tableWidget.setSpan(5, 1, 2, 1)
            item = QtGui.QTableWidgetItem("MP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(5, 5, item)
            self.tableWidget.setSpan(5, 5, 2, 1)

            item = QtGui.QTableWidgetItem("MP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(11, 1, item)
            self.tableWidget.setSpan(11, 1, 2, 1)
            item = QtGui.QTableWidgetItem("MP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(11, 5, item)
            self.tableWidget.setSpan(11, 5, 2, 1)

            item = QtGui.QTableWidgetItem("MP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(17, 1, item)
            self.tableWidget.setSpan(17, 1, 2, 1)
            item = QtGui.QTableWidgetItem("MP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(17, 5, item)
            self.tableWidget.setSpan(17, 5, 2, 1)

            item = QtGui.QTableWidgetItem("MP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(23, 1, item)
            self.tableWidget.setSpan(23, 1, 2, 1)
            item = QtGui.QTableWidgetItem("MP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(23, 5, item)
            self.tableWidget.setSpan(23, 5, 2, 1)

            item = QtGui.QTableWidgetItem("IP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(3, 1, item)
            self.tableWidget.setSpan(3, 1, 2, 1)
            item = QtGui.QTableWidgetItem("IP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(3, 5, item)
            self.tableWidget.setSpan(3, 5, 2, 1)

            item = QtGui.QTableWidgetItem("IPP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(7, 1, item)
            self.tableWidget.setSpan(7, 1, 2, 1)
            item = QtGui.QTableWidgetItem("IPP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(7, 5, item)
            self.tableWidget.setSpan(7, 5, 2, 1)

            item = QtGui.QTableWidgetItem("IPP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(13, 1, item)
            self.tableWidget.setSpan(13, 1, 2, 1)
            item = QtGui.QTableWidgetItem("IPP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(13, 5, item)
            self.tableWidget.setSpan(13, 5, 2, 1)

            item = QtGui.QTableWidgetItem("IPP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(19, 1, item)
            self.tableWidget.setSpan(19, 1, 2, 1)
            item = QtGui.QTableWidgetItem("IPP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(19, 5, item)
            self.tableWidget.setSpan(19, 5, 2, 1)

            item = QtGui.QTableWidgetItem("IPP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(25, 1, item)
            self.tableWidget.setSpan(25, 1, 2, 1)
            item = QtGui.QTableWidgetItem("IPP")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(25, 5, item)
            self.tableWidget.setSpan(25, 5, 2, 1)

            item = QtGui.QTableWidgetItem("IPD")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(9, 1, item)
            self.tableWidget.setSpan(9, 1, 2, 1)
            item = QtGui.QTableWidgetItem("IPD")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(9, 5, item)
            self.tableWidget.setSpan(9, 5, 2, 1)

            item = QtGui.QTableWidgetItem("IPD")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(15, 1, item)
            self.tableWidget.setSpan(15, 1, 2, 1)
            item = QtGui.QTableWidgetItem("IPD")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(15, 5, item)
            self.tableWidget.setSpan(15, 5, 2, 1)

            item = QtGui.QTableWidgetItem("IPD")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(21, 1, item)
            self.tableWidget.setSpan(21, 1, 2, 1)
            item = QtGui.QTableWidgetItem("IPD")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(21, 5, item)
            self.tableWidget.setSpan(21, 5, 2, 1)

            item = QtGui.QTableWidgetItem("IPD")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(27, 1, item)
            self.tableWidget.setSpan(27, 1, 2, 1)
            item = QtGui.QTableWidgetItem("IPD")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget.setItem(27, 5, item)
            self.tableWidget.setSpan(27, 5, 2, 1)

            for i in range(0, 14):
                item = QtGui.QTableWidgetItem("ext")
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget.setItem(2 * i + 1, 2, item)
                item = QtGui.QTableWidgetItem("")
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget.setItem(2 * i + 1, 3, item)
                item = QtGui.QTableWidgetItem("ext")
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget.setItem(2 * i + 1, 6, item)
                item = QtGui.QTableWidgetItem("")
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget.setItem(2 * i + 1, 7, item)

                item = QtGui.QTableWidgetItem("flex")
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget.setItem(2 * i + 2, 2, item)
                item = QtGui.QTableWidgetItem("")
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget.setItem(2 * i + 2, 3, item)
                item = QtGui.QTableWidgetItem("flex")
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget.setItem(2 * i + 2, 6, item)
                item = QtGui.QTableWidgetItem("")
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget.setItem(2 * i + 2, 7, item)

            self.tableWidget.setEditTriggers(
                QtGui.QAbstractItemView.NoEditTriggers)

            self.tableWidget.setVisible(True)
            self.widget_2.setVisible(False)
            self.mains_d_2.setVisible(False)

            # Create icon
            newIcon = QtGui.QIcon()
            newIcon.addPixmap(QtGui.QPixmap(
                self.path_script + "filesUi/imagesUi/main.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

            # Modify icon
            self.Mode_M_T.setIcon(newIcon)

    def updateGraphiqueTableau(self):
        print 'updateGraphiqueTableau'

    def changeModeGraphiqueTableau(self, patient):
        print 'changeModeGraphiqueTableau'

    def copyDataSuivi(self):
        print 'copyDataSuivi'

    def printDataSuivi(self):
        print 'printDataSuivi'

    def saveDataSuivi(self):
        print 'saveDataSuivi'

    def updateBegin(self):
        print 'updateBegin'

    def readLabels(self):
        print 'readLabels'

    def goToPageAfter(self):
        self.setCurrentIndex(self.currentIndex() + 1)

    def goToPageBefore(self):
        self.setCurrentIndex(self.currentIndex() - 1)

    def goToPageSuivi(self):
        self.setCurrentIndex(4)

    def disableData(self):
        print 'disableData'

    def activateDeleteMode(self):
        print 'activateDeleteMode'

    def startAcquisition(self):
        print 'startAcqisition'

        self.animated = True

        # Create icon
        newIcon = QtGui.QIcon()
        newIcon.addPixmap(QtGui.QPixmap(self.path_script+"filesUi/imagesUi/green_circle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        # Modify icon
        self.circle_signal.setIcon(newIcon)


        # Start acquisition
        self.setupUpdateThread()

        # Create icon for stop button
        newIcon = QtGui.QIcon()
        newIcon.addPixmap(QtGui.QPixmap(self.path_script+"filesUi/imagesUi/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        # Modify icon
        self.start.setIcon(newIcon)

    def saveData(self):
        print 'saveData'

    def printData(self):
        print 'printData'

    def save(self):
        print 'save'

    def setupUpdateThread(self):
        print 'setupUpdateThread'
        # Connect thread for get angles calculated
        self.updateThread.progress.connect(self.updateText, QtCore.Qt.BlockingQueuedConnection)
        # Start thread if it is not running
        if not self.updateThread.isRunning():
            self.updateThread.start()
            self.leapThread.start()

    def updateText(self, text):
        print 'updateText'

        for Hand_select in User_Choices[0]:
            for Finger_select in User_Choices[1]:
                for Joint_select in Finger_select[1]:
                    for Data_select in [Min, Value, Max]:
                        intVal = int(text[Hand_select][Finger_select[0]][Joint_select][Data_select])
                        stringVal = str(intVal).zfill(3)

                        label = getattr(self, self.labels[Hand_select][Finger_select[0]][Joint_select][Data_select])
                        label.setText (stringVal)

    def zoomDelete(self):
        print 'zoomDelete'

    def clickT_MP_L_Min(self):

        # When user click delete button --> he want to reset an value
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Thumb, MP, Min

        # When user not click delete button --> he want to zoom an value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Thumb, MP, Min

    def clickT_MP_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Thumb, MP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Thumb, MP, Value

    def clickT_MP_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Thumb, MP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Thumb, MP, Max

    def clickT_IPP_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Thumb, IPP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Thumb, IPP, Min

    def clickT_IPP_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Thumb, IPP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Thumb, IPP, Value

    def clickT_IPP_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Thumb, IPP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Thumb, IPP, Max

    def clickI_MP_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Index, MP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Index, MP, Min

    def clickI_MP_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Index, MP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Index, MP, Value

    def clickI_MP_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Index, MP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Index, MP, Max

    def clickI_IPP_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Index, IPP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Index, IPP, Min

    def clickI_IPP_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Index, IPP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Index, IPP, Value

    def clickI_IPP_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Index, IPP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Index, IPP, Max

    def clickI_IPD_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Index, IPD, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Index, IPD, Min

    def clickI_IPD_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Index, IPD, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Index, IPD, Value

    def clickI_IPD_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Index, IPD, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Index, IPD, Max

    def clickM_MP_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Middle, MP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Middle, MP, Min

    def clickM_MP_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Middle, MP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Middle, MP, Value

    def clickM_MP_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Middle, MP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Middle, MP, Max

    def clickM_IPP_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Middle, IPP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Middle, IPP, Min

    def clickM_IPP_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Middle, IPP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Middle, IPP, Value

    def clickM_IPP_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Middle, IPP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Middle, IPP, Max

    def clickM_IPD_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Middle, IPD, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Middle, IPD, Min

    def clickM_IPD_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Middle, IPD, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Middle, IPD, Value

    def clickM_IPD_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Middle, IPD, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Middle, IPD, Max

    def clickR_MP_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Ring, MP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Ring, MP, Min

    def clickR_MP_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Ring, MP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Ring, MP, Value

    def clickR_MP_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Ring, MP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Ring, MP, Max

    def clickR_IPP_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Ring, IPP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Ring, IPP, Min

    def clickR_IPP_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Ring, IPP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Ring, IPP, Value

    def clickR_IPP_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Ring, IPP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Ring, IPP, Max

    def clickR_IPD_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Ring, IPD, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Ring, IPD, Min

    def clickR_IPD_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Ring, IPD, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Ring, IPD, Value

    def clickR_IPD_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Ring, IPD, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Ring, IPD, Max

    def clickP_MP_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Pinky, MP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Pinky, MP, Min

    def clickP_MP_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Pinky, MP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Pinky, MP, Value

    def clickP_MP_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Pinky, MP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Pinky, MP, Max

    def clickP_IPP_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Pinky, IPP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Pinky, IPP, Min

    def clickP_IPP_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Pinky, IPP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Pinky, IPP, Value

    def clickP_IPP_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Pinky, IPP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Pinky, IPP, Max

    def clickP_IPD_L_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Pinky, IPD, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Pinky, IPD, Min

    def clickP_IPD_L_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Pinky, IPD, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Pinky, IPD, Value

    def clickP_IPD_L_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Left, Pinky, IPD, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Left, Pinky, IPD, Max

    def clickT_MP_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Thumb, MP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Thumb, MP, Min

    def clickT_MP_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Thumb, MP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Thumb, MP, Value

    def clickT_MP_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Thumb, MP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Thumb, MP, Max

    def clickT_IPP_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Thumb, IPP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Thumb, IPP, Min

    def clickT_IPP_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Thumb, IPP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Thumb, IPP, Value

    def clickT_IPP_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Thumb, IPP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Thumb, IPP, Max

    def clickI_MP_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Index, MP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Index, MP, Min

    def clickI_MP_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Index, MP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Index, MP, Value

    def clickI_MP_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Index, MP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Index, MP, Max

    def clickI_IPP_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Index, IPP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Index, IPP, Min

    def clickI_IPP_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Index, IPP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Index, IPP, Value

    def clickI_IPP_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Index, IPP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Index, IPP, Max

    def clickI_IPD_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Index, IPD, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Index, IPD, Min

    def clickI_IPD_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Index, IPD, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Index, IPD, Value

    def clickI_IPD_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Index, IPD, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Index, IPD, Max

    def clickM_MP_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Middle, MP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Middle, MP, Min

    def clickM_MP_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Middle, MP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Middle, MP, Value

    def clickM_MP_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Middle, MP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Middle, MP, Max

    def clickM_IPP_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Middle, IPP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Middle, IPP, Min

    def clickM_IPP_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Middle, IPP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Middle, IPP, Value

    def clickM_IPP_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Middle, IPP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Middle, IPP, Max

    def clickM_IPD_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Middle, IPD, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Middle, IPD, Min

    def clickM_IPD_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Middle, IPD, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Middle, IPD, Value

    def clickM_IPD_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Middle, IPD, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Middle, IPD, Max

    def clickR_MP_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Ring, MP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Ring, MP, Min

    def clickR_MP_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Ring, MP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Ring, MP, Value

    def clickR_MP_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Ring, MP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Ring, MP, Max

    def clickR_IPP_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Ring, IPP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Ring, IPP, Min

    def clickR_IPP_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Ring, IPP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Ring, IPP, Value

    def clickR_IPP_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Ring, IPP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Ring, IPP, Max

    def clickR_IPD_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Ring, IPD, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Ring, IPD, Min

    def clickR_IPD_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Ring, IPD, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Ring, IPD, Value

    def clickR_IPD_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Ring, IPD, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Ring, IPD, Max

    def clickP_MP_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Pinky, MP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Pinky, MP, Min

    def clickP_MP_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Pinky, MP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Pinky, MP, Value

    def clickP_MP_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Pinky, MP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Pinky, MP, Max

    def clickP_IPP_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Pinky, IPP, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Pinky, IPP, Min

    def clickP_IPP_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Pinky, IPP, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Pinky, IPP, Value

    def clickP_IPP_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Pinky, IPP, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Pinky, IPP, Max

    def clickP_IPD_R_Min(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Pinky, IPD, Min
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Pinky, IPD, Min

    def clickP_IPD_R_Value(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Pinky, IPD, Value
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Pinky, IPD, Value

    def clickP_IPD_R_Max(self):
        if self.deleteMode == True:
            self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = Right, Pinky, IPD, Max
        else:
            self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = Right, Pinky, IPD, Max
