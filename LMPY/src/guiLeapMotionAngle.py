#!/usr/bin/python
# -*- coding: utf-8 -*-

# @package guiLeapMotionAngle
#
# - very nice GUI of displaying angle in clinical context
#
# DEPENDENCIES
# ----------------------------------------------------------------------------------------------------------------------
#
# EXTERNAL PYTHON PACKAGES
# - Leap Motion SDK : <https://developer.leapmotion.com/>
#
# ----------------------------------------------------------------------------------------------------------------------
# Copyright (c) 2015 GBM4900, Polytechnique Montreal
# Authors: Aldo ZAIMI, Vincent GAGNON, Eden ABITBOL, Eddie MAGNIDE
#
# License: See LICENSE file
# ======================================================================================================================

# == IMPORTS =============================================================

import sys                          # For using system parameters
import math                         # For calculating angle
import time                         # For extracting time
import datetime                     # For extracting date
import csv                          # For saving data in file
import os                           # For extracting path
import glob                         # For extracting path
import pageUi                       # Import py of Qt Designer
import mainPageUi
from PySide import QtGui, QtCore    # For GUI functions

sys.path.insert(0, "../lib")  # CHANGEMENT ICI

# Check if the correct LeapMotion library is installed
try:
    import Leap
except ImportError:
    print '\n---------------------------- Leap Motion Library not installed --------------------------\n'
    print 'Install library at   : <https://developer.leapmotion.com/downloads/skeletal-beta> '
    print 'For more information : <https://www.youtube.com/watch?v=T9k7rdY625M> \n'
    print '---------------------------------------Exit program. ------------------------------------\n'
    sys.exit(2)

# Check if the correct python version in installed
if not sys.version_info[:3] >= (2, 7, 6):
    print '\n--------------------- The correct version of python is not installed --------------------\n'
    print 'You need to install Python 2.7.6 '
    print '1. Delete your version of python '
    print '2. Install Canopy: <https://store.enthought.com/> '
    print '3. Configure new Canopy python 2.7.6 in PyCharm \n'
    print '---------------------------------------Exit program. ------------------------------------\n'
    sys.exit(2)

#=========================================================================

#== FUNCTION: Do dot product: returns dot product of 2 3D unit vectors ===


def dot_product(v1, v2):
    a = v1[0]                   # x for vector 1
    b = v2[0]                   # x for vector 2
    c = v1[1]                   # y for vector 1
    d = v2[1]                   # y for vector 2
    e = v1[2]                   # z for vector 1
    f = v2[2]                   # z for vector 2
    g = a * b + c * d + e * f   # do dot product of v1 and v2
    return g

#=========================================================================

#== CLASS: SampleListener; receives events from controller and executes ac

class SampleListener(Leap.Listener):

    def on_init(self, controller):
        print "Initialisé"

    def on_connect(self, controller):
        print 'Connecté'

    # Function executed for each frame:
    def on_frame(self, controller):
        print "ON EST DANS ON FRAME WOUHOUUUU"

        # Global variables for user interaction
        global signalWarning
        global warningMessage

        # Get the most recent frame and report some basic information
        frame = controller.frame()
        #----------------------------------------------------
        # Get hands (for each hand in the current frame...):
        #----------------------------------------------------

        # Initialisation
        i = 0
        stop = bool
        confidence = 0
        distance = 0

        # Count hand number
        for hand_count in frame.hands:
            i += 1

            # Calculate mean of hand confidences
            confidence = confidence + hand_count.confidence

            # Calculate maximum of distance between LM and the hands
            if distance < hand_count.palm_position[1]:
                distance = hand_count.palm_position[1]

        # When there are no hand detected by LM
        if i == 0:

            # Activate warning and set message for display
            signalWarning = True
            warningMessage = "L'acquisition est interrompue, aucune main n'est détectée par la Leap Motion"
            print warningMessage
            # Stop acquisition
            stop = True

        # When there are more than 2 hands detected by LM
        if i > 2:

            # Activate warning and set message for display
            signalWarning = True
            warningMessage = "L'acquisition est interrompue, la Leap Motion détecte plus de deux mains"
            print warningMessage
            # Stop acquisition
            stop = True

        # When there are one or two hands detected by LM
        if i == 2 or i == 1:

            # Disable warning and permit acquisition
            signalWarning = False
            stop = False

            # Low confidence
            if confidence < 0.5:

                # Activate warning and set message for display
                signalWarning = True
                warningMessage = "L'acquisition est interrompue, l’efficacité de la Leap Motion est trop faible : " + \
                    str(int(confidence * 10)) + "%"
                print warningMessage
                # Stop acquisition
                stop = True

            # High distance
            if distance > 250:

                # Activate warning and set message for display
                signalWarning = True
                warningMessage = "L'acquisition est interrompue, la distance entre la Leap Motion et la main est trop élevée : " + \
                    str(int(distance)) + "mm"
                print warningMessage
                # Stop acquisition
                stop = True

        # Start acquisition when it permits
        if not stop:

            for hand in frame.hands:

                # Find out which hand is in the frame (h = 0 for left and 1 for
                # right)
                h = 0 if hand.is_left else 1

                #--------------------------------------------------------------
                # Get fingers (for each finger of each hand in the current frame...):
                #--------------------------------------------------------------
                for finger in hand.fingers:

                    #----------------------------------------------------------
                    # Get bones (for each bone of each finger of each hand in the current frame...):
                    #----------------------------------------------------------
                    # If its a thumb...
                    if finger.type == 0:

                        # Iterate through Proximal, Intermediate and Distal (no
                        # Metacarpal).
                        for b in range(2, 4):

                            # Determinate joint type
                            j = b - 2

                            # Identification of the previous bone
                            bone1 = finger.bone(b - 1)

                            # Identification of the actual bone
                            bone2 = finger.bone(b)

                            # For MP
                            if b == 2:

                                # Store direction unit vector of previous bone
                                # in v0
                                v0 = bone1.basis.y_basis
                                # Store direction unit vector of actual bone
                                v1 = bone2.basis.y_basis
                                # Calculate scalar product
                                sp = dot_product(v0, v1)

                                # Verify if scalar product is valid, i.e. it
                                # between -1 and 1
                                if (sp <= 1) and (sp >= -1) and (v0 != v1):

                                    # Get angle (in radians) between the 2 unit
                                    # vectors
                                    angle_in_radians = math.acos(sp)
                                    # Get angle in degrees
                                    angle_in_degrees = math.degrees(
                                        angle_in_radians)

                                    # Detect hyper-extension with direction
                                    # bone1 and normal bone2
                                    if dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                                        angle_in_degrees = -angle_in_degrees

                                    #------------------------------------------
                                    # Determinate minimum and maximum
                                    #------------------------------------------

                                    # Replace maximum value if the new value is
                                    # superior
                                    if Hands_Angle[h][finger.type][j][Max] < angle_in_degrees:
                                        Hands_Angle[h][finger.type][j][
                                            Max] = angle_in_degrees

                                    # Replace minimum value if the new value is
                                    # inferior
                                    if Hands_Angle[h][finger.type][j][Min] > angle_in_degrees:
                                        # Change value of min
                                        Hands_Angle[h][finger.type][j][
                                            Min] = angle_in_degrees

                                    # Store actual value of angle
                                    Hands_Angle[h][finger.type][j][
                                        Value] = angle_in_degrees

                            # For others joints
                            else:

                                # Determinate each length in triangle
                                length_a = bone1.length
                                length_b = bone2.length
                                length_c = bone2.next_joint.distance_to(
                                    bone1.prev_joint)

                                # Apply cos law
                                sp = (length_c * length_c - length_b * length_b -
                                      length_a * length_a) / (2 * length_a * length_b)

                                # Verify if scalar product is valid, i.e. it
                                # between -1 and 1
                                if (sp <= 1) and (sp >= -1):

                                    # Get angle (in radians) between the 2 unit
                                    # vectors
                                    angle_in_radians = math.acos(sp)
                                    # Get angle in degrees
                                    angle_in_degrees = math.degrees(
                                        angle_in_radians)

                                    # Detect hyper-extension with direction
                                    # bone1 and normal bone2
                                    if dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                                        angle_in_degrees = -angle_in_degrees

                                    #------------------------------------------
                                    # Determinate minimum and maximum
                                    #------------------------------------------

                                    # Replace maximum value if the new value is
                                    # superior
                                    if Hands_Angle[h][finger.type][j][Max] < angle_in_degrees:
                                        Hands_Angle[h][finger.type][j][
                                            Max] = angle_in_degrees

                                    # Replace minimum value if the new value is
                                    # inferior
                                    if Hands_Angle[h][finger.type][j][Min] > angle_in_degrees:
                                        # Change value of min
                                        Hands_Angle[h][finger.type][j][
                                            Min] = angle_in_degrees

                                    # Store actual value of angle
                                    Hands_Angle[h][finger.type][j][
                                        Value] = angle_in_degrees

                    # ... otherwise (i.e., if its NOT a thumb)...
                    else:

                        # Iterate through Proximal, Intermediate and Distal (no
                        # Metacarpal).
                        for b in range(1, 4):

                            # Determinate joint type
                            j = b - 1

                            # Identification of the previous bone
                            bone1 = finger.bone(b - 1)

                            # Identification of the actual bone
                            bone2 = finger.bone(b)

                            # For MP
                            if b == 1:

                                # Store direction unit vector of previous bone
                                # in v0
                                v0 = bone1.basis.y_basis
                                # Store direction unit vector of actual bone
                                v1 = bone2.basis.y_basis
                                # Calculate scalar product
                                sp = dot_product(v0, v1)

                                # Verify if scalar product is valid, i.e. it
                                # between -1 and 1
                                if (sp <= 1) and (sp >= -1) and (v0 != v1):

                                    # Get angle (in radians) between the 2 unit
                                    # vectors
                                    angle_in_radians = math.acos(sp)
                                    # Get angle in degrees
                                    angle_in_degrees = math.degrees(
                                        angle_in_radians)

                                    # Detect hyper-extension with direction
                                    # bone1 and normal bone2
                                    if dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                                        angle_in_degrees = -angle_in_degrees

                                    #------------------------------------------
                                    # Determinate minimum and maximum
                                    #------------------------------------------

                                    # Replace maximum value if the new value is
                                    # superior
                                    if Hands_Angle[h][finger.type()][j][Max] < angle_in_degrees:
                                        Hands_Angle[h][finger.type()][j][
                                            Max] = angle_in_degrees

                                    # Replace minimum value if the new value is
                                    # inferior
                                    if Hands_Angle[h][finger.type()][j][Min] > angle_in_degrees:
                                        # Change value of min
                                        Hands_Angle[h][finger.type()][j][
                                            Min] = angle_in_degrees

                                    # Store actual value of angle
                                    Hands_Angle[h][finger.type()][j][
                                        Value] = angle_in_degrees

                            # For others joints
                            else:

                                # Determinate each length in triangle
                                length_a = bone1.length
                                length_b = bone2.length
                                length_c = bone2.next_joint.distance_to(
                                    bone1.prev_joint)

                                # Apply cos law
                                sp = (length_c * length_c - length_b * length_b -
                                      length_a * length_a) / (2 * length_a * length_b)

                                # Verify if scalar product is valid, i.e. it
                                # between -1 and 1
                                if (sp <= 1) and (sp >= -1):

                                    # Get angle (in radians) between the 2 unit
                                    # vectors
                                    angle_in_radians = math.acos(sp)
                                    # Get angle in degrees
                                    angle_in_degrees = math.degrees(
                                        angle_in_radians)

                                    # Detect hyper-extension with direction
                                    # bone1 and normal bone2
                                    if dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                                        angle_in_degrees = -angle_in_degrees

                                    #------------------------------------------
                                    # Determinate minimum and maximum
                                    #------------------------------------------

                                    # Replace maximum value if the new value is
                                    # superior
                                    if Hands_Angle[h][finger.type()][j][Max] < angle_in_degrees:
                                        Hands_Angle[h][finger.type()][j][
                                            Max] = angle_in_degrees

                                    # Replace minimum value if the new value is
                                    # inferior
                                    if Hands_Angle[h][finger.type()][j][Min] > angle_in_degrees:
                                        # Change value of min
                                        Hands_Angle[h][finger.type()][j][
                                            Min] = angle_in_degrees

                                    # Store actual value of angle
                                    Hands_Angle[h][finger.type()][j][
                                        Value] = angle_in_degrees
                                        

#=========================================================================

#== FUNCTION:  three digits data format ==================================


def formatData(Hands_Angle):

    # Each hand chosen
    for Hand_select in User_Choices[0]:
        # Each finger chosen for each hand
        for Finger_select in User_Choices[1]:
            # Each joint chosen for each finger
            for Joint_select in Finger_select[1]:
                # Value, Min, Max
                for Data_select in [Min, Value, Max]:

                    # Define initial value of each data type
                    if Data_select == Min:
                        Data_select_initial = 180
                    if Data_select == Value:
                        Data_select_initial = 0
                    if Data_select == Max:
                        Data_select_initial = -180

                    # Check if Leap Motion acquire frame
                    if Hands_Angle[Hand_select][Finger_select[0]][Joint_select][Data_select] != Data_select_initial:

                        # Store temporarily the results
                        temp = Hands_Angle[Hand_select][
                            Finger_select[0]][Joint_select][Data_select]
                        # Round angle amplitude
                        temp = round(temp)
                        # Convert angle amplitude float to integer
                        temp = int(temp)

                        # Stock results in saving format
                        if Data_select == Min:
                            Results[Hand_select][Finger_select[0]][
                                Joint_select][Data_select] = str(temp).zfill(3)
                        if Data_select == Max:
                            Results[Hand_select][Finger_select[0]][
                                Joint_select][Data_select] = str(temp).zfill(3)
                        if Data_select == Value:
                            Results[Hand_select][Finger_select[0]][
                                Joint_select][Data_select] = str(temp).zfill(3)

#=========================================================================

#== CLASS: upateThread; send angles calculated to GUI ====================


class upateThread(QtCore.QThread):

    # Create a signal for angles list
    progress = QtCore.Signal(list)

    # Function for initialisation thread
    def __init__(self, parent=None):
        super(upateThread, self).__init__(parent)    # Initialisation of class
        self.exiting = False                        # Disable thread at beginning of program
        global Acquisition

    # Function for running thread
    def run(self):
        print 'Exécution du thread'
        # listener = SampleListener()
        # controller = Leap.Controller()

        # controller.add_listener(listener)

        if Acquisition:                         # Check if acquisition is permit
            acquisition_angle()                 # Acquire data of LM and calculate angles
        while True:
            # Emit angles calculated to GUI
            self.progress.emit(Results)
            # Put values in correct format (3 digits)
            formatData(Hands_Angle)


#=========================================================================

#== FUNCTION : start LM acquisition ======================================


def acquisition_angle():

    print "acquisition angle"

    # Create controller
    controller = Leap.Controller()

    # Global variables
    global signalWarning
    global warningMessage

    # Create a sample listener
    listener = SampleListener()

    # controller = Leap.Controller(listener)

    # Check if LM is connected
    # if not controller.is_connected:

    #     # Activate warning and display message
    #     signalWarning = True
    #     warningMessage = "L'acquisition est impossible, veuillez connecter votre Leap Motion à votre ordinateur"
    #     print "Veuillez connecter LM"



    # Have the sample listener receive events from the controller
    controller.add_listener(listener)
    print controller.is_connected

#=========================================================================

#== FUNCTION: replace_row ; Replace specific row in file .csv  ===========


def replace_row(file_path, number_row, data_to_replace):

    # Initialize list of file rows
    bottle_list = []

    # Read all data from the csv file
    with open(file_path, 'rb') as b:
        bottles = csv.reader(b)
        bottle_list.extend(bottles)
        b.close()

    # Data to override in the format {line_num_to_override:data_to_write}
    line_to_override = {number_row: data_to_replace}

    # Write data to the csv file and replace the line in the line_to_override
    # dict
    with open(file_path, 'wb') as b:
        writer = csv.writer(b, delimiter=';')
        for line, row in enumerate(bottle_list):
            data_row = line_to_override.get(line, row)
            writer.writerow(data_row)
        b.close()

    # Remove irrelevant character (") in file created
    s = open(file_path, 'r').read()
    chars = ('"')
    for c in chars:
        s = ''.join(s.split(c))
    out_file = open(file_path, 'w')
    out_file.write(s)
    out_file.close()

#=========================================================================

#== CLASS: page; TabWidget for GUI =======================================


class page(QtGui.QTabWidget, pageUi.Ui_TabWidget):

    # Function for initialisation TabWidget
    def __init__(self, parent=None):

        # Initialisation of class
        super(page, self).__init__(parent)
        self.setupUi(self)
        self.i = 0

        # Initialise marker for know if we must reinitialise angle after click
        self.deleteMode = False

        # Initialise the indices of angle which we must zoom
        self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = int, int, int, int

        # Initialise the indices of angle which we must reinitialise angle
        self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = int, int, int, int

        # Save name of angles buttons created in Qt Designer for display
        self.labels = [[[['T_MP_L_Min', 'T_MP_L_Value', 'T_MP_L_Max'], ['T_IPP_L_Min', 'T_IPP_L_Value', 'T_IPP_L_Max']], [['I_MP_L_Min', 'I_MP_L_Value', 'I_MP_L_Max'], ['I_IPP_L_Min', 'I_IPP_L_Value', 'I_IPP_L_Max'], ['I_IPD_L_Min', 'I_IPD_L_Value', 'I_IPD_L_Max']], [['M_MP_L_Min', 'M_MP_L_Value', 'M_MP_L_Max'], ['M_IPP_L_Min', 'M_IPP_L_Value', 'M_IPP_L_Max'], ['M_IPD_L_Min', 'M_IPD_L_Value', 'M_IPD_L_Max']], [['R_MP_L_Min', 'R_MP_L_Value', 'R_MP_L_Max'], ['R_IPP_L_Min', 'R_IPP_L_Value', 'R_IPP_L_Max'], ['R_IPD_L_Min', 'R_IPD_L_Value', 'R_IPD_L_Max']], [['P_MP_L_Min', 'P_MP_L_Value', 'P_MP_L_Max'], ['P_IPP_L_Min', 'P_IPP_L_Value', 'P_IPP_L_Max'], ['P_IPD_L_Min', 'P_IPD_L_Value', 'P_IPD_L_Max']]], [
            [['T_MP_R_Min', 'T_MP_R_Value', 'T_MP_R_Max'], ['T_IPP_R_Min', 'T_IPP_R_Value', 'T_IPP_R_Max']], [['I_MP_R_Min', 'I_MP_R_Value', 'I_MP_R_Max'], ['I_IPP_R_Min', 'I_IPP_R_Value', 'I_IPP_R_Max'], ['I_IPD_R_Min', 'I_IPD_R_Value', 'I_IPD_R_Max']], [['M_MP_R_Min', 'M_MP_R_Value', 'M_MP_R_Max'], ['M_IPP_R_Min', 'M_IPP_R_Value', 'M_IPP_R_Max'], ['M_IPD_R_Min', 'M_IPD_R_Value', 'M_IPD_R_Max']], [['R_MP_R_Min', 'R_MP_R_Value', 'R_MP_R_Max'], ['R_IPP_R_Min', 'R_IPP_R_Value', 'R_IPP_R_Max'], ['R_IPD_R_Min', 'R_IPD_R_Value', 'R_IPD_R_Max']], [['P_MP_R_Min', 'P_MP_R_Value', 'P_MP_R_Max'], ['P_IPP_R_Min', 'P_IPP_R_Value', 'P_IPP_R_Max'], ['P_IPD_R_Min', 'P_IPD_R_Value', 'P_IPD_R_Max']]]]

        # Save name of angles buttons created in Qt Designer for select user
        # choices
        self.buttons = [[[['Thumb_MP_L', 'Thumb_MP_L', 'Thumb_MP_L'], ['Thumb_IPP_L', 'Thumb_IPP_L', 'Thumb_IPP_L']], [['Index_MP_L', 'Index_MP_L', 'Index_MP_L'], ['Index_IPP_L', 'Index_IPP_L', 'Index_IPP_L'], ['Index_IPD_L', 'Index_IPD_L', 'Index_IPD_L']], [['Middle_MP_L', 'Middle_MP_L', 'Middle_MP_L'], ['Middle_IPP_L', 'Middle_IPP_L', 'Middle_IPP_L'], ['Middle_IPD_L', 'Middle_IPD_L', 'Middle_IPD_L']], [['Ring_MP_L', 'Ring_MP_L', 'Ring_MP_L'], ['Ring_IPP_L', 'Ring_IPP_L', 'Ring_IPP_L'], ['Ring_IPD_L', 'Ring_IPD_L', 'Ring_IPD_L']], [['Pinky_MP_L', 'Pinky_MP_L', 'Pinky_MP_L'], ['Pinky_IPP_L', 'Pinky_IPP_L', 'Pinky_IPP_L'], ['Pinky_IPD_L', 'Pinky_IPD_L', 'Pinky_IPD_L']]], [
            [['Thumb_MP_R', 'Thumb_MP_R', 'Thumb_MP_R'], ['Thumb_IPP_R', 'Thumb_IPP_R', 'Thumb_IPP_R']], [['Index_MP_R', 'Index_MP_R', 'Index_MP_R'], ['Index_IPP_R', 'Index_IPP_R', 'Index_IPP_R'], ['Index_IPD_R', 'Index_IPD_R', 'Index_IPD_R']], [['Middle_MP_R', 'Middle_MP_R', 'Middle_MP_R'], ['Middle_IPP_R', 'Middle_IPP_R', 'Middle_IPP_R'], ['Middle_IPD_R', 'Middle_IPD_R', 'Middle_IPD_R']], [['Ring_MP_R', 'Ring_MP_R', 'Ring_MP_R'], ['Ring_IPP_R', 'Ring_IPP_R', 'Ring_IPP_R'], ['Ring_IPD_R', 'Ring_IPD_R', 'Ring_IPD_R']], [['Pinky_MP_R', 'Pinky_MP_R', 'Pinky_MP_R'], ['Pinky_IPP_R', 'Pinky_IPP_R', 'Pinky_IPP_R'], ['Pinky_IPD_R', 'Pinky_IPD_R', 'Pinky_IPD_R']]]]

        # Table
        self.cellV = [[[[1, 1, 2], [3, 3, 4]], [[5, 5, 6], [7, 7, 8], [9, 9, 10]], [[11, 11, 12], [13, 13, 14], [15, 15, 16]], [[17, 17, 18], [19, 19, 20], [21, 21, 22]], [[23, 23, 24], [25, 25, 26], [27, 27, 28]]], [
            [[1, 1, 2], [3, 3, 4]], [[5, 5, 6], [7, 7, 8], [9, 9, 10]], [[11, 11, 12], [13, 13, 14], [15, 15, 16]], [[17, 17, 18], [19, 19, 20], [21, 21, 22]], [[23, 23, 24], [25, 25, 26], [27, 27, 28]]]]
        self.cellH = [[[[3, 3, 3], [3, 3, 3]], [[3, 3, 3], [3, 3, 3], [3, 3, 3]], [[3, 3, 3], [3, 3, 3], [3, 3, 3]], [[3, 3, 3], [3, 3, 3], [3, 3, 3]], [[3, 3, 3], [3, 3, 3], [3, 3, 3]]], [
            [[7, 7, 7], [7, 7, 7]], [[7, 7, 7], [7, 7, 7], [7, 7, 7]], [[7, 7, 7], [7, 7, 7], [7, 7, 7]], [[7, 7, 7], [7, 7, 7], [7, 7, 7]], [[7, 7, 7], [7, 7, 7], [7, 7, 7]]]]

        # Select all angles
        self.tous.click()

        # Select all two movements
        self.combine.click()

        # Create new object of upateThread class
        self.updateThread = upateThread()

        # Put last session at date of today
        self.derniere_seance.setDate(QtCore.QDate.currentDate())

        # Define global marker of acquisition which define emission or not
        global Acquisition

        # Not acquisition at beginning of program
        Acquisition = False

        # Define global variable of path
        global path_script

        # Save path of file folder
        path_script = os.getcwd() + '/'

        # Read files and save old data
        self.labels_F = ['G D1 MP flex', 'G D1 IP flex', 'G D2 MP flex', 'G D2 IPP flex', 'G D2 IPD flex', 'G D3 MP flex', 'G D3 IPP flex', 'G D3 IPD flex', 'G D4 MP flex', 'G D4 IPP flex', 'G D4 IPD flex', 'G D5 MP flex', 'G D5 IPP flex', 'G D5 IPD flex', 'D D1 MP flex', 'D D1 IP flex', 'D D2 MP flex', 'D D2 IPP flex', 'D D2 IPD flex', 'D D3 MP flex', 'D D3 IPP flex', 'D D3 IPD flex', 'D D4 MP flex', 'D D4 IPP flex', 'D D4 IPD flex', 'D D5 MP flex', 'D D5 IPP flex',
                         'D D5 IPD flex', 'G D1 MP ext', 'G D1 IP ext', 'G D2 MP ext', 'G D2 IPP ext', 'G D2 IPD ext', 'G D3 MP ext', 'G D3 IPP ext', 'G D3 IPD ext', 'G D4 MP ext', 'G D4 IPP ext', 'G D4 IPD ext', 'G D5 MP ext', 'G D5 IPP ext', 'G D5 IPD ext', 'D D1 MP ext', 'D D1 IP ext', 'D D2 MP ext', 'D D2 IPP ext', 'D D2 IPD ext', 'D D3 MP ext', 'D D3 IPP ext', 'D D3 IPD ext', 'D D4 MP ext', 'D D4 IPP ext', 'D D4 IPD ext', 'D D5 MP ext', 'D D5 IPP ext', 'D D5 IPD ext']
        self.index_labels_F = [int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int,
                               int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int]
        self.readLabels()
        self.modeMain = True

        # Create icon
        newIcon = QtGui.QIcon()

        # Modify icon
        self.circle_signal_2.setIcon(newIcon)

        # Initialisation for warning message
        global signalWarning
        signalWarning = False
        global warningMessage
        warningMessage = ""

    # Function for copy data in clipboard
    def copyData(self):

        # Screen shot of widget
        p = QtGui.QPixmap.grabWindow(self.widget_2.winId())
        p.save('resultats.png', 'png')

        # Copy file in clipboard
        data = QtCore.QMimeData()
        url = QtCore.QUrl.fromLocalFile(path_script + "resultats.png")
        data.setUrls([url])
        QtGui.QApplication.clipboard().setMimeData(data)

    # Function for switch between hand view or table view
    def changeModeMainTableau(self):

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
                path_script + "filesUi/imagesUi/table.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

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
                path_script + "filesUi/imagesUi/main.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

            # Modify icon
            self.Mode_M_T.setIcon(newIcon)

    # Function for update dat in widget "Suivi"
    def updateGraphiqueTableau(self):

        self.choix_dossier.setCurrentIndex(
            self.choix_dossier_2.currentIndex() + 1)

        # Initialisation of index for display labels
        self.index_labels_F = [int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int,
                               int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int]

        # Search index of report number select by user
        patient = 0
        for i in range(0, len(self.infos)):
            if (self.infos[i][4] == self.choix_dossier_2.currentText()):
                patient = i
                break

        # Add item for option to choice all angles
        self.choix_dossier_3.setItemText(0, QtGui.QApplication.translate(
            "TabWidget", "Tous", None, QtGui.QApplication.UnicodeUTF8))
        k = 1

        # Check if there are data read in files
        if self.infos != []:

            # Initialisation of ordinates and abscissa
            x = [list] * 56
            y = [list] * 56

            # For each session, read all angles saved
            for j in range(2, 58):
                for i in range(8, len(self.infos[patient])):
                    if self.infos[patient][i][j] != " " and self.infos[patient][i][j] != "":
                        if y[j - 2] == list:
                            y[j - 2] = [int(self.infos[patient][i][j])]
                            x[j - 2] = [self.infos[patient][i][0]]
                        else:
                            y[j - 2].append(int(self.infos[patient][i][j]))
                            x[j - 2].append(self.infos[patient][i][0])
                        self.index_labels_F[j - 2] = j - 2

            # Detect index of angle no valid
            ind = []
            for i in range(0, len(y)):
                if y[i] == list:
                    ind.append(i)

            # Delete all no valid angles
            x = [i for j, i in enumerate(x) if j not in ind]
            y = [i for j, i in enumerate(y) if j not in ind]

            # Save number of angles
            number_angle = len(y)

            # Add labels in combobox
            for j in range(2, 58):
                if self.index_labels_F[j - 2] != int:
                    self.choix_dossier_3.addItem("")
                    self.choix_dossier_3.setItemText(k, QtGui.QApplication.translate("TabWidget", self.labels_F[
                                                     self.index_labels_F[j - 2]], None, QtGui.QApplication.UnicodeUTF8))    # in UTF8 because accents
                    k += 1

            # Delete all others data
            while self.choix_dossier_3.count() > number_angle + 1:
                self.choix_dossier_3.removeItem(
                    self.choix_dossier_3.count() - 1)

            # Draw graphic axis for following patient
            H = self.graphicsView.height() - 5
            L = self.graphicsView.width() - 5

            l1 = L / 175
            h = (H) / 180

            scene = QtGui.QGraphicsScene(-L / 2, -H / 2, L, H)
            scene.addLine(-L / 2 + l1 * 10, H / 2 - l1 * 10, L / 2 -
                          l1 * 10, H / 2 - l1 * 10, QtGui.QPen(QtCore.Qt.black, 2))
            scene.addLine(-L / 2 + l1 * 10, H / 2 - l1 * 10, -L / 2 + l1 *
                          10, H / 2 - l1 * 10 - h * 180, QtGui.QPen(QtCore.Qt.black, 2))

            l = ((L - l1 * 20)) / 180
            ordinates = [float] * 181
            for i in range(0, 181):
                ordinates[i] = float(H / 2 - l1 * 10 - h * i)
                if i % 5 == 0:
                    scene.addLine(-L / 2 + l1 * 10, H / 2 - l1 * 10 - h * i, -L / 2 + l1 *
                                  10 - l * 3, H / 2 - l1 * 10 - h * i, QtGui.QPen(QtCore.Qt.black))
                    if i % 10 == 0:

                        t = QtGui.QGraphicsTextItem()
                        t.setPos(-L / 2 + l1 * 10 - l * 8, H /
                                 2 - l1 * 10 - h * i - h * 3)
                        t.setPlainText(str(i - 60))
                        font = QtGui.QFont()
                        font.setPointSize(8)
                        font.setFamily("Book Antiqua")
                        t.setFont(font)
                        scene.addItem(t)
                else:
                    scene.addLine(-L / 2 + l1 * 10, H / 2 - l1 * 10 - h * i, -L / 2 +
                                  l1 * 10 - l, H / 2 - l1 * 10 - h * i, QtGui.QPen(QtCore.Qt.black))

            # Draw table for following patient
            if self.choix_dossier_3.currentIndex() == 0:
                self.changeModeGraphiqueTableau(patient)

            # Draw graphic for following patient
            else:
                self.tableWidget_2.setVisible(False)
                self.graphicsView.setVisible(True)
                t = QtGui.QGraphicsTextItem()
                t.setPos(L / 2 - l1 * 30, H / 2 - l1 * 10 - h * 200)
                t.setPlainText(self.choix_dossier_3.currentText())
                font = QtGui.QFont()
                font.setPointSize(16)
                font.setBold(True)
                font.setFamily("Book Antiqua")
                t.setFont(font)
                scene.addItem(t)

                dates_number = len(x[self.choix_dossier_3.currentIndex() - 1])
                abscissa = [float] * dates_number
                l = (L / dates_number) * 0.80

                for i in range(1, dates_number + 1):

                    abscissa[i - 1] = -L / 2 + l1 * 10 + l * i
                    scene.addLine(-L / 2 + l1 * 10 + l * i, H / 2 - l1 * 10, -L / 2 + l1 *
                                  10 + l * i, H / 2 - l1 * 10 + h * 3, QtGui.QPen(QtCore.Qt.black))
                    t = QtGui.QGraphicsTextItem()
                    t.setPos(-L / 2 + l1 * 10 + l * i - 20, H / 2 - h)
                    t.setPlainText(
                        x[self.choix_dossier_3.currentIndex() - 1][i - 1])
                    font = QtGui.QFont()
                    font.setPointSize(8)
                    font.setFamily("Book Antiqua")
                    t.setFont(font)
                    t.rotate(-80)
                    scene.addItem(t)

                for i in range(0, len(y[self.choix_dossier_3.currentIndex() - 1])):
                    index = int(
                        60 + y[self.choix_dossier_3.currentIndex() - 1][i])
                    scene.addEllipse(abscissa[i], ordinates[index], 5, 5, QtGui.QPen(
                        QtCore.Qt.darkBlue), QtGui.QBrush(QtCore.Qt.black))
                    if i != 0:
                        index_p = int(
                            60 + y[self.choix_dossier_3.currentIndex() - 1][i - 1])
                        scene.addLine(abscissa[i], ordinates[index], abscissa[
                                      i - 1], ordinates[index_p], QtGui.QPen(QtCore.Qt.darkBlue))

                self.graphicsView.setScene(scene)

    # Function for switch between graphic view or table view for all angles
    def changeModeGraphiqueTableau(self, patient):

        # Clear and initialisation of table
        self.tableWidget_2.deleteLater()
        self.tableWidget_2 = QtGui.QTableWidget(self.suivi)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.horizontalHeader().setVisible(False)
        self.tableWidget_2.verticalHeader().setVisible(False)
        self.tableWidget_2.style().pixelMetric(QtGui.QStyle.PM_ScrollBarExtent)
        self.tableWidget_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.tableWidget_2.setVisible(False)

        # Adjust table with data read
        nb_date = len(self.infos[patient]) - 9
        self.tableWidget_2.setColumnCount(8 + nb_date * 2)
        self.tableWidget_2.setRowCount(29)

        # Create table
        self.gridLayout_16.addWidget(self.tableWidget_2, 1, 1, 1, 3)
        size_V = (self.height() * 696) / 808
        size_H = (self.width() * 1295) / 1600
        self.tableWidget_2.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(
            size_H / (8 + nb_date * 2))
        self.tableWidget_2.verticalHeader().setDefaultSectionSize(size_V / 29)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Book Antiqua")
        self.tableWidget_2.setFont(font)

        font.setBold(True)
        item = QtGui.QTableWidgetItem("Main gauche")
        item.setFont(font)
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(0, 0, item)
        self.tableWidget_2.setSpan(0, 0, 1, 3)

        item = QtGui.QTableWidgetItem("Main droite")
        item.setFont(font)
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(0, (8 + nb_date * 2) / 2, item)
        self.tableWidget_2.setSpan(0, (8 + nb_date * 2) / 2, 1, 3)

        item = QtGui.QTableWidgetItem("D1")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(1, 0, item)
        self.tableWidget_2.setSpan(1, 0, 4, 1)
        item = QtGui.QTableWidgetItem("D1")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(1, (8 + nb_date * 2) / 2, item)
        self.tableWidget_2.setSpan(1, (8 + nb_date * 2) / 2, 4, 1)

        item = QtGui.QTableWidgetItem("D2")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(5, 0, item)
        self.tableWidget_2.setSpan(5, 0, 6, 1)
        item = QtGui.QTableWidgetItem("D2")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(5, (8 + nb_date * 2) / 2, item)
        self.tableWidget_2.setSpan(5, (8 + nb_date * 2) / 2, 6, 1)

        item = QtGui.QTableWidgetItem("D3")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(11, 0, item)
        self.tableWidget_2.setSpan(11, 0, 6, 1)
        item = QtGui.QTableWidgetItem("D3")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(11, (8 + nb_date * 2) / 2, item)
        self.tableWidget_2.setSpan(11, (8 + nb_date * 2) / 2, 6, 1)

        item = QtGui.QTableWidgetItem("D4")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(17, 0, item)
        self.tableWidget_2.setSpan(17, 0, 6, 1)
        item = QtGui.QTableWidgetItem("D4")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(17, (8 + nb_date * 2) / 2, item)
        self.tableWidget_2.setSpan(17, (8 + nb_date * 2) / 2, 6, 1)

        item = QtGui.QTableWidgetItem("D5")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(23, 0, item)
        self.tableWidget_2.setSpan(23, 0, 6, 1)
        item = QtGui.QTableWidgetItem("D5")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(23, (8 + nb_date * 2) / 2, item)
        self.tableWidget_2.setSpan(23, (8 + nb_date * 2) / 2, 6, 1)

        item = QtGui.QTableWidgetItem("MP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(1, 1, item)
        self.tableWidget_2.setSpan(1, 1, 2, 1)
        item = QtGui.QTableWidgetItem("MP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(1, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(1, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("MP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(5, 1, item)
        self.tableWidget_2.setSpan(5, 1, 2, 1)
        item = QtGui.QTableWidgetItem("MP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(5, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(5, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("MP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(11, 1, item)
        self.tableWidget_2.setSpan(11, 1, 2, 1)
        item = QtGui.QTableWidgetItem("MP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(11, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(11, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("MP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(17, 1, item)
        self.tableWidget_2.setSpan(17, 1, 2, 1)
        item = QtGui.QTableWidgetItem("MP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(17, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(17, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("MP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(23, 1, item)
        self.tableWidget_2.setSpan(23, 1, 2, 1)
        item = QtGui.QTableWidgetItem("MP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(23, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(23, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("IP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(3, 1, item)
        self.tableWidget_2.setSpan(3, 1, 2, 1)
        item = QtGui.QTableWidgetItem("IP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(3, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(3, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("IPP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(7, 1, item)
        self.tableWidget_2.setSpan(7, 1, 2, 1)
        item = QtGui.QTableWidgetItem("IPP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(7, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(7, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("IPP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(13, 1, item)
        self.tableWidget_2.setSpan(13, 1, 2, 1)
        item = QtGui.QTableWidgetItem("IPP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(13, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(13, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("IPP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(19, 1, item)
        self.tableWidget_2.setSpan(19, 1, 2, 1)
        item = QtGui.QTableWidgetItem("IPP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(19, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(19, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("IPP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(25, 1, item)
        self.tableWidget_2.setSpan(25, 1, 2, 1)
        item = QtGui.QTableWidgetItem("IPP")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(25, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(25, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("IPD")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(9, 1, item)
        self.tableWidget_2.setSpan(9, 1, 2, 1)
        item = QtGui.QTableWidgetItem("IPD")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(9, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(9, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("IPD")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(15, 1, item)
        self.tableWidget_2.setSpan(15, 1, 2, 1)
        item = QtGui.QTableWidgetItem("IPD")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(15, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(15, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("IPD")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(21, 1, item)
        self.tableWidget_2.setSpan(21, 1, 2, 1)
        item = QtGui.QTableWidgetItem("IPD")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(21, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(21, (8 + nb_date * 2) / 2 + 1, 2, 1)

        item = QtGui.QTableWidgetItem("IPD")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(27, 1, item)
        self.tableWidget_2.setSpan(27, 1, 2, 1)
        item = QtGui.QTableWidgetItem("IPD")
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item.setBackground(QtGui.QColor(245, 245, 255))
        self.tableWidget_2.setItem(27, (8 + nb_date * 2) / 2 + 1, item)
        self.tableWidget_2.setSpan(27, (8 + nb_date * 2) / 2 + 1, 2, 1)

        for i in range(0, 14):
            item = QtGui.QTableWidgetItem("ext")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget_2.setItem(2 * i + 1, 2, item)
            item = QtGui.QTableWidgetItem("")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget_2.setItem(2 * i + 1, 3, item)
            item = QtGui.QTableWidgetItem("ext")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget_2.setItem(
                2 * i + 1, (8 + nb_date * 2) / 2 + 2, item)
            item = QtGui.QTableWidgetItem("")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget_2.setItem(
                2 * i + 1, (8 + nb_date * 2) / 2 + 3, item)

            item = QtGui.QTableWidgetItem("flex")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget_2.setItem(2 * i + 2, 2, item)
            item = QtGui.QTableWidgetItem("")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget_2.setItem(2 * i + 2, 3, item)
            item = QtGui.QTableWidgetItem("flex")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget_2.setItem(
                2 * i + 2, (8 + nb_date * 2) / 2 + 2, item)
            item = QtGui.QTableWidgetItem("")
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget_2.setItem(
                2 * i + 2, (8 + nb_date * 2) / 2 + 3, item)

        for i in range(8, len(self.infos[patient])):
            item = QtGui.QTableWidgetItem(self.infos[patient][i][0])
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget_2.setItem(0, 3 + i - 8, item)
            item = QtGui.QTableWidgetItem(self.infos[patient][i][0])
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor(245, 245, 255))
            self.tableWidget_2.setItem(
                0, (8 + nb_date * 2) / 2 + 3 + i - 8, item)
            for j in range(2, 16):
                item = QtGui.QTableWidgetItem(self.infos[patient][i][j])
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget_2.setItem(2 * (j - 2) + 2, 3 + i - 8, item)
            for j in range(16, 30):
                item = QtGui.QTableWidgetItem(self.infos[patient][i][j])
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget_2.setItem(
                    2 * (j - 16) + 2, ((8 + nb_date * 2) / 2) + 3 + i - 8, item)
            for j in range(30, 44):
                item = QtGui.QTableWidgetItem(self.infos[patient][i][j])
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget_2.setItem(2 * (j - 30) + 1, 3 + i - 8, item)
            for j in range(44, 58):
                item = QtGui.QTableWidgetItem(self.infos[patient][i][j])
                item.setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                item.setBackground(QtGui.QColor(245, 245, 255))
                self.tableWidget_2.setItem(
                    2 * (j - 44) + 1, ((8 + nb_date * 2) / 2) + 3 + i - 8, item)

        self.tableWidget_2.setEditTriggers(
            QtGui.QAbstractItemView.NoEditTriggers)

        self.tableWidget_2.setVisible(True)
        self.graphicsView.setVisible(False)

    # Function for copy data in clipboard for following window
    def copyDataSuivi(self):
        # Screen shot of widget
        p = QtGui.QPixmap.grabWindow(self.graphicsView.winId())
        p.save('suivi.png', 'png')

        # Copy file in clipboard
        data = QtCore.QMimeData()
        url = QtCore.QUrl.fromLocalFile(path_script + "suivi.png")
        data.setUrls([url])
        QtGui.QApplication.clipboard().setMimeData(data)

    # Print data for following window
    def printDataSuivi(self):

        p = QtGui.QPixmap.grabWindow(self.graphicsView.winId())
        p.save('suivi.png', 'png')

        image = QtGui.QImage()
        image.load(path_script + "suivi.png")

        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)

        printDialog = QtGui.QPrintDialog(printer, self)
        if printDialog.exec_() == QtGui.QDialog.Accepted:
            painter = QtGui.QPainter(printer)
            rect = painter.viewport()
            size = image.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(),
                                size.width(), size.height())
            painter.setWindow(image.rect())
            painter.drawImage(0, 0, image)
            painter.end()

    # Save data for following window
    def saveDataSuivi(self):
        # Display dialog box for select file name
        options = QtGui.QFileDialog.Options()
        fileName, filtr = QtGui.QFileDialog.getSaveFileName(self,
                                                            "Enregistrer le fichier", "",
                                                            "CSV Files (*.csv)", "", options)

        # When a file is selected
        if fileName:

            # Do the reading
            file1 = open(path_script + 'Results' + '/' +
                         self.choix_dossier_2.currentText() + '.csv', 'rb')
            reader = csv.reader(file1)
            new_rows_list = []
            for row in reader:
                new_rows_list.append(row)
            file1.close()

            # Do the writing
            file2 = open(fileName, 'wb')
            writer = csv.writer(file2)
            writer.writerows(new_rows_list)
            file2.close()

    # Update size and others thigs at beginning
    def updateBegin(self):

        global warningMessage
        mainPage.setMinimumSize(QtCore.QSize(
            mainPage.width(), mainPage.height()))
        self.centralwidget.setMinimumSize(
            QtCore.QSize(self.width(), self.height()))
        self.centralwidget.setMaximumSize(
            QtCore.QSize(self.width(), self.height()))
        self.setMinimumSize(QtCore.QSize(self.width(), self.height()))
        self.label_3_.setMinimumSize(QtCore.QSize(
            self.width() * 0.8, self.height() * 0.95))
        self.label_3_.setMaximumSize(QtCore.QSize(
            self.width() * 0.8, self.height() * 0.95))

        warningMessage = ""
        self.readLabels()
        if self.currentIndex() == 4:
            self.choix_dossier_3.setCurrentIndex(1)
            self.choix_dossier_3.setCurrentIndex(0)

    # Function for save old data
    def readLabels(self):

        # Define global variable of path
        global path_script

        # Initialisation of variable for save old data
        bottle = []
        self.infos = []

        # Read data in all files in folder of results
        if os.path.exists(path_script + 'Results'):
            # Extract all files of folder
            fileNames = glob.glob(path_script + 'Results' + '/*.csv')
            # Travel each file of folder
            for i in range(0, len(fileNames)):
                fileName = fileNames[i].replace(
                    '\\', '/')              # Correct file name
                # Check if file exist
                if os.path.exists(fileName):
                    # Initialisation variable of each file
                    bottle_list = []
                    with open(fileName, 'rb') as b:                     # Open csv file of folder
                        # Read all lines of file
                        bottles = csv.reader(b)
                        # Save all lines of file
                        bottle_list.extend(bottles)
                        b.close()                                       # Close csv file of folder
                    # Add data read at the end of list
                    bottle.append(bottle_list)

        # Travel each file data
        for i in range(0, len(bottle)):
            info_list = [bottle[i][0][0][7:],                           # Save first name
                         # Save last name
                         bottle[i][1][0][4:],
                         # Save birth date
                         bottle[i][2][0][18:],
                         # Save sex
                         bottle[i][3][0][5:],
                         # Save report number
                         bottle[i][4][0][18:],
                         # Save update date
                         bottle[i][5][0][20:],
                         # Save update hour
                         bottle[i][6][0][21:],
                         bottle[i][7][0][15:]]                          # Save user

            # For older sessions
            for j in range(13, len(bottle[i])):
                # Save old angles measured
                info_list.append(bottle[i][j][0].split(';'))

            # Add angles with other data
            self.infos.append(info_list)

            if self.choix_dossier.count() <= len(bottle):               # Check if there are all patient item
                # Add new patient item to combo box
                self.choix_dossier.addItem("")
                # Add new patient item to combo box
                self.choix_dossier_2.addItem("")

            self.choix_dossier.setItemText(i + 1,                         # Modify item text in correct
                                           QtGui.QApplication.translate("TabWidget",               # report number
                                                                        info_list[4], None, QtGui.QApplication.UnicodeUTF8))    # in UTF8 because accents

            self.choix_dossier_2.setItemText(i,                         # Modify item text in correct
                                             QtGui.QApplication.translate("TabWidget",               # report number
                                                                          info_list[4], None, QtGui.QApplication.UnicodeUTF8))    # in UTF8 because accents

    # Function for go to page after current page
    def goToPageAfter(self):
        self.setCurrentIndex(self.currentIndex() + 1)

    # Function for go to page before current page
    def goToPageBefore(self):
        self.setCurrentIndex(self.currentIndex() - 1)

    # Function for go to page for following patient
    def goToPageSuivi(self):
        self.setCurrentIndex(4)

    # Function for disable data if old patient is selected
    def disableData(self):

        global Hands_Angle
        global Results
        global Results_to_save

        # In the case where user select existent patient
        if self.choix_dossier.currentText() != "Nouveau patient":

            self.choix_dossier_2.setCurrentIndex(
                self.choix_dossier.currentIndex() - 1)

            # Search index of report number select by user
            patient = 0
            for i in range(0, len(self.infos)):
                if (self.infos[i][4] == self.choix_dossier.currentText()):
                    patient = i
                    break

            # Display all data of existent patient selected
            self.prenom.setText(self.infos[patient][0])
            self.nom.setText(self.infos[patient][1])
            self.date_naissance.setDate(QtCore.QDate(int(self.infos[patient][2].split(
                '-')[0]), int(self.infos[patient][2].split('-')[1]), int(self.infos[patient][2].split('-')[2])))
            if self.infos[patient][3] == "M":
                self.sexe.setCurrentIndex(0)
            if self.infos[patient][3] == "F":
                self.sexe.setCurrentIndex(1)
            self.derniere_seance.setDate(QtCore.QDate(int(self.infos[patient][len(self.infos[patient]) - 1][0].split('-')[0]), int(self.infos[
                                         patient][len(self.infos[patient]) - 1][0].split('-')[1]), int(self.infos[patient][len(self.infos[patient]) - 1][0].split('-')[2])))
            self.numero_dossier.setText(self.infos[patient][4])

            # Disable all data inputs
            self.nom_3.setEnabled(False)
            self.prenom_3.setEnabled(False)
            self.date_naissance_3.setEnabled(False)
            self.derniere_seance_3.setEnabled(False)
            self.numero_dossier_3.setEnabled(False)
            self.sexe_3.setEnabled(False)
            self.nom_2.setEnabled(False)
            self.prenom_2.setEnabled(False)
            self.date_naissance_2.setEnabled(False)
            self.derniere_seance_2.setEnabled(False)
            self.numero_dossier_2.setEnabled(False)
            self.sexe_2.setEnabled(False)
            self.nom.setEnabled(False)
            self.prenom.setEnabled(False)
            self.date_naissance.setEnabled(False)
            self.derniere_seance.setEnabled(False)
            self.numero_dossier.setEnabled(False)
            self.sexe.setEnabled(False)

        # In the case where user select new patient
        else:

            # List of finger extrema, joints, fingers and hands
            Hands_Angle = [[[[180, 0, -180], [180, 0, -180]],               # [Min, Value, Max]--> [MP][IPP] --> [Thumb]
                            # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Index]
                            [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                            # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Middle]
                            [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                            # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Ring]
                            [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                            [[180, 0, -180], [180, 0, -180], [180, 0, -180]]],      # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Pinky]
                           [[[180, 0, -180], [180, 0, -180]],                       # Same for right hand
                            # Same for right hand
                            [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                            # Same for right hand
                            [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                            # Same for right hand
                            [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                            [[180, 0, -180], [180, 0, -180], [180, 0, -180]]]]      # Same for right hand

            # Results for display
            Results = [[[[' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]],
                       [[[' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]]]

            # Results for save
            Results_to_save = [[[[' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]],
                               [[[' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]]]

            # Clear all data inputs
            self.prenom.setText("")
            self.nom.setText("")
            self.derniere_seance.setDate(QtCore.QDate.currentDate())
            self.numero_dossier.setText("")

            # Enable all data inputs
            self.nom_3.setEnabled(True)
            self.prenom_3.setEnabled(True)
            self.date_naissance_3.setEnabled(True)
            self.derniere_seance_3.setEnabled(True)
            self.numero_dossier_3.setEnabled(True)
            self.sexe_3.setEnabled(True)
            self.nom_2.setEnabled(True)
            self.prenom_2.setEnabled(True)
            self.date_naissance_2.setEnabled(True)
            self.derniere_seance_2.setEnabled(True)
            self.numero_dossier_2.setEnabled(True)
            self.sexe_2.setEnabled(True)
            self.nom.setEnabled(True)
            self.prenom.setEnabled(True)
            self.date_naissance.setEnabled(True)
            self.derniere_seance.setEnabled(True)
            self.numero_dossier.setEnabled(True)
            self.sexe.setEnabled(True)

    # Function for disable all others tabs when user click delete button
    def activateDeleteMode(self):

        # Pass in reverse mode
        self.deleteMode = not self.deleteMode

        # Disable all others tabs
        if self.deleteMode:
            self.setCursor(QtCore.Qt.PointingHandCursor)
            self.setTabEnabled(0, False)
            self.setTabEnabled(1, False)
            self.setTabEnabled(2, False)
            self.setTabEnabled(4, False)
            self.setTabEnabled(5, False)
            self.setTabEnabled(6, False)
            self.start.setEnabled(False)
            self.Print.setEnabled(False)
            self.copy.setEnabled(False)
            self.Mode_M_T.setEnabled(False)
            self.save_file.setEnabled(False)

        # Enable all others tabs
        if not self.deleteMode:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.setTabEnabled(0, True)
            self.setTabEnabled(1, True)
            self.setTabEnabled(2, True)
            self.setTabEnabled(4, True)
            self.setTabEnabled(5, True)
            self.setTabEnabled(6, True)
            self.start.setEnabled(True)
            self.Print.setEnabled(True)
            self.copy.setEnabled(True)
            self.Mode_M_T.setEnabled(True)
            self.save_file.setEnabled(True)

    # Function for acquisition mode when user click start button
    def startAcquisition(self):

        # Declaration of global variables
        global Results_to_save
        global Acquisition

        self.animated = True

        # Pass to reverse mode of acquisition
        Acquisition = not Acquisition

        # Initialise indices of angle for zoom
        self.handZoom, self.fingerZoom, self.jointZoom, self.dataZoom = int, int, int, int

        # Initialise indices of angle for delete
        self.handDelete, self.fingerDelete, self.jointDelete, self.dataDelete = int, int, int, int

        # Clear right zoom text
        self.zoom_droite.setText("")

        # Clear left zoom text
        self.zoom_gauche.setText("")

        # When it is acquisition mode
        if Acquisition:
            if not signalWarning:

                mainPage.statusbar.showMessage(QtGui.QApplication.translate(
                    "TabWidget", "", None, QtGui.QApplication.UnicodeUTF8))

                # Create icon
                newIcon = QtGui.QIcon()
                newIcon.addPixmap(QtGui.QPixmap(
                    path_script + "filesUi/imagesUi/green_circle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

                # Modify icon
                self.circle_signal.setIcon(newIcon)

            # Initialise data for saving
            Results_to_save = [[[[' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]],
                               [[[' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]]]

            # Start acquisition
            self.setupUpdateThread()

            # Create icon for stop button
            newIcon = QtGui.QIcon()
            newIcon.addPixmap(QtGui.QPixmap(
                path_script + "filesUi/imagesUi/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

            # Modify icon
            self.start.setIcon(newIcon)

            # Disable all others tabs
            self.setTabEnabled(0, False)
            self.setTabEnabled(1, False)
            self.setTabEnabled(2, False)
            self.setTabEnabled(4, False)
            self.setTabEnabled(5, False)
            self.setTabEnabled(6, False)

            # Disable all data inputs
            self.nom_3.setEnabled(False)
            self.prenom_3.setEnabled(False)
            self.date_naissance_3.setEnabled(False)
            self.derniere_seance_3.setEnabled(False)
            self.numero_dossier_3.setEnabled(False)
            self.sexe_3.setEnabled(False)
            self.gauche_2.setEnabled(False)
            self.droite_2.setEnabled(False)
            self.tous_2.setEnabled(False)
            self.flexion_2.setEnabled(False)
            self.extension_2.setEnabled(False)
            self.combine_2.setEnabled(False)
            self.effacer.setEnabled(False)
            self.save_file.setEnabled(False)
            self.Print.setEnabled(False)
            self.copy.setEnabled(False)

        # When it is not acquisition
        if not Acquisition:

            mainPage.statusbar.showMessage(QtGui.QApplication.translate(
                "TabWidget", warningMessage, None, QtGui.QApplication.UnicodeUTF8))

            # Create icon
            newIcon = QtGui.QIcon()
            newIcon.addPixmap(QtGui.QPixmap(
                path_script + "filesUi/imagesUi/red_circle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

            # Modify icon
            self.circle_signal.setIcon(newIcon)

            # Create icon for start button
            newIcon = QtGui.QIcon()
            newIcon.addPixmap(QtGui.QPixmap(
                path_script + "filesUi/imagesUi/start.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

            # Modify icon
            self.start.setIcon(newIcon)

            # Enable all others tabs
            self.setTabEnabled(0, True)
            self.setTabEnabled(1, True)
            self.setTabEnabled(2, True)
            self.setTabEnabled(4, True)
            self.setTabEnabled(5, True)
            self.setTabEnabled(6, True)
            self.gauche_2.setEnabled(True)
            self.droite_2.setEnabled(True)
            self.tous_2.setEnabled(True)
            self.flexion_2.setEnabled(True)
            self.extension_2.setEnabled(True)
            self.combine_2.setEnabled(True)
            self.effacer.setEnabled(True)
            self.save_file.setEnabled(True)
            self.Print.setEnabled(True)
            self.copy.setEnabled(True)

            if self.choix_dossier.currentText() != "Nouveau patient" and set(sum(sum(sum(Results_to_save, []), []), [])) != {' '}:
                self.save()

            if self.choix_dossier.currentText() == "Nouveau patient":

                # Enable all data inputs
                self.nom_3.setEnabled(True)
                self.prenom_3.setEnabled(True)
                self.date_naissance_3.setEnabled(True)
                self.derniere_seance_3.setEnabled(True)
                self.sexe_3.setEnabled(True)
                self.numero_dossier_3.setEnabled(True)

                # Warning message for save data
                reply = QtGui.QMessageBox.warning(self, "Enregistrement du patient",
                                                  QtGui.QApplication.translate("QMessageBox",
                                                                               "Êtes-vous sûr d'enregistrer ce patient ?",
                                                                               None, QtGui.QApplication.UnicodeUTF8),
                                                        QtGui.QMessageBox.Yes |
                                                  QtGui.QMessageBox.No)

                # In case where user confirm saving
                if reply == QtGui.QMessageBox.Yes:

                    # Check if report number is not empty
                    if self.numero_dossier_3.text() == "":

                        # Warning message for no correct report number
                        reply_2 = QtGui.QMessageBox.critical(self, "Enregistrement du patient",
                                                             QtGui.QApplication.translate("QMessageBox",
                                                                                          "Numéro de dossier invalide !",
                                                                                          None, QtGui.QApplication.UnicodeUTF8),
                                                             QtGui.QMessageBox.Ok)
                        if reply_2 == QtGui.QMessageBox.Ok:
                            pass

                    # If report number is not empty, save data
                    else:

                        if set(sum(sum(sum(Results_to_save, []), []), [])) == {' '}:

                            # Warning message for no correct report number
                            reply_3 = QtGui.QMessageBox.warning(self, "Enregistrement du patient",
                                                                QtGui.QApplication.translate("QMessageBox",
                                                                                             "Aucune donnée n'a été acquise !",
                                                                                             None, QtGui.QApplication.UnicodeUTF8),
                                                                QtGui.QMessageBox.Ok)
                            if reply_3 == QtGui.QMessageBox.Ok:
                                pass

                        else:
                            self.save()
                            self.readLabels()
                            self.choix_dossier.setCurrentIndex(self.choix_dossier.findText(
                                unicode(self.numero_dossier_3.text()), QtCore.Qt.MatchFixedString))

                # In case where user not confirm saving, don't save data
                else if reply == QtGui.QMessageBox.No:
                    pass

    # Function for save data in file when user click save button
    def saveData(self):
        print "save data"

        # Display dialog box for select file name
        options = QtGui.QFileDialog.Options()
        fileName, filtr = QtGui.QFileDialog.getSaveFileName(self,
                                                            "Enregistrer le fichier", "",
                                                            "CSV Files (*.csv)", "", options)

        # When a file is selected
        if fileName:

            # Save time between start time and actual time
            t = time.time() - start

            # Data to saving
            data = [str(t),
                    Results_to_save[Left][Thumb][MP][
                        Max], Results_to_save[Left][Thumb][IPP][Max],
                    Results_to_save[Left][Index][MP][Max], Results_to_save[Left][
                        Index][IPP][Max], Results_to_save[Left][Index][IPD][Max],
                    Results_to_save[Left][Middle][MP][Max], Results_to_save[Left][
                        Middle][IPP][Max], Results_to_save[Left][Middle][IPD][Max],
                    Results_to_save[Left][Ring][MP][Max], Results_to_save[Left][
                        Ring][IPP][Max], Results_to_save[Left][Ring][IPD][Max],
                    Results_to_save[Left][Pinky][MP][Max], Results_to_save[Left][
                        Pinky][IPP][Max], Results_to_save[Left][Pinky][IPD][Max],
                    Results_to_save[Right][Thumb][MP][
                        Max], Results_to_save[Right][Thumb][IPP][Max],
                    Results_to_save[Right][Index][MP][Max], Results_to_save[Right][
                        Index][IPP][Max], Results_to_save[Right][Index][IPD][Max],
                    Results_to_save[Right][Middle][MP][Max], Results_to_save[Right][
                        Middle][IPP][Max], Results_to_save[Right][Middle][IPD][Max],
                    Results_to_save[Right][Ring][MP][Max], Results_to_save[Right][
                        Ring][IPP][Max], Results_to_save[Right][Ring][IPD][Max],
                    Results_to_save[Right][Pinky][MP][Max], Results_to_save[Right][
                        Pinky][IPP][Max], Results_to_save[Right][Pinky][IPD][Max],
                    Results_to_save[Left][Thumb][MP][
                        Min], Results_to_save[Left][Thumb][IPP][Min],
                    Results_to_save[Left][Index][MP][Min], Results_to_save[Left][
                        Index][IPP][Min], Results_to_save[Left][Index][IPD][Min],
                    Results_to_save[Left][Middle][MP][Min], Results_to_save[Left][
                        Middle][IPP][Min], Results_to_save[Left][Middle][IPD][Min],
                    Results_to_save[Left][Ring][MP][Min], Results_to_save[Left][
                        Ring][IPP][Min], Results_to_save[Left][Ring][IPD][Min],
                    Results_to_save[Left][Pinky][MP][Min], Results_to_save[Left][
                        Pinky][IPP][Min], Results_to_save[Left][Pinky][IPD][Min],
                    Results_to_save[Right][Thumb][MP][
                        Min], Results_to_save[Right][Thumb][IPP][Min],
                    Results_to_save[Right][Index][MP][Min], Results_to_save[Right][
                        Index][IPP][Min], Results_to_save[Right][Index][IPD][Min],
                    Results_to_save[Right][Middle][MP][Min], Results_to_save[Right][
                        Middle][IPP][Min], Results_to_save[Right][Middle][IPD][Min],
                    Results_to_save[Right][Ring][MP][Min], Results_to_save[Right][
                        Ring][IPP][Min], Results_to_save[Right][Ring][IPD][Min],
                    Results_to_save[Right][Pinky][MP][Min], Results_to_save[Right][Pinky][IPP][Min], Results_to_save[Right][Pinky][IPD][Min]]

            # Write data in file .csv
            with open(fileName, 'wb') as fp:
                # Define format as excel format
                a = csv.writer(fp, delimiter=';')
                # Write all headers in file of raw data
                a.writerow(["Prenom", Patient_First_Name])
                a.writerow(["Nom", Patient_Name])
                a.writerow(["Date de naissance", Birth_Day])
                a.writerow(["Sexe", Sex])
                a.writerow(["Numero de dossier", Report_Number])
                a.writerow(["Date de la seance", str(
                    datetime.datetime.fromtimestamp(time.time())).split(' ')[0]])
                a.writerow(
                    ["Heure", str(datetime.datetime.fromtimestamp(time.time())).split(' ')[1][:8]])
                a.writerow(["Ergotherapeute", QtGui.QApplication.translate(
                    "TabWidget", User, None, QtGui.QApplication.UnicodeUTF8)])
                a.writerow(
                    "---------------------------------------------------------")
                a.writerow([" ",
                            "Flexion", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            "Extension", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " "])
                a.writerow([" ",
                            "Main Gauche", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            "Main Droite", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            "Main Gauche", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            "Main Droite", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " "])
                a.writerow([" ",
                            "D1", " ",
                            "D2", " ", " ",
                            "D3", " ", " ",
                            "D4", " ", " ",
                            "D5", " ", " ",
                            "D1", " ",
                            "D2", " ", " ",
                            "D3", " ", " ",
                            "D4", " ", " ",
                            "D5", " ", " ",
                            "D1", " ",
                            "D2", " ", " ",
                            "D3", " ", " ",
                            "D4", " ", " ",
                            "D5", " ", " ",
                            "D1", " ",
                            "D2", " ", " ",
                            "D3", " ", " ",
                            "D4", " ", " ",
                            "D5", " ", " "])
                a.writerow(["Temps [s]",
                            "MP", "IP",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IP",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IP",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IP",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD"])
                a.writerow(data)
                fp.close()

    # Function for print data
    def printData(self):

        p = QtGui.QPixmap.grabWindow(self.widget_2.winId())
        p.save('resultats.png', 'png')

        image = QtGui.QImage()
        image.load(path_script + "resultats.png")

        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)

        printDialog = QtGui.QPrintDialog(printer, self)
        if printDialog.exec_() == QtGui.QDialog.Accepted:
            painter = QtGui.QPainter(printer)
            rect = painter.viewport()
            size = image.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(),
                                size.width(), size.height())
            painter.setWindow(image.rect())
            painter.drawImage(0, 0, image)
            painter.end()

    # Function for save data in file automatically
    def save(self):
        print "save"
        # Marker for knowing when we must write new line in file .csv
        add_new_session = True

        # Update patient data with user inputs
        Patient_Name = self.nom_3.text()
        Patient_First_Name = self.prenom_3.text()
        Sex = self.sexe_3.currentText()
        Report_Number = self.numero_dossier_3.text()
        Birth_Day = self.date_naissance_3.text()
        User = self.usager.text()

        # Create repertory of all files if it does not exist
        if not os.path.exists(path_script + 'Results'):
            os.makedirs(path_script + 'Results')

        # Data to saving
        data = [str(datetime.datetime.fromtimestamp(time.time())).split(' ')[0],
                str(datetime.datetime.fromtimestamp(
                    time.time())).split(' ')[1][:8],
                Results_to_save[Left][Thumb][MP][
                    Max], Results_to_save[Left][Thumb][IPP][Max],
                Results_to_save[Left][Index][MP][Max], Results_to_save[Left][
                    Index][IPP][Max], Results_to_save[Left][Index][IPD][Max],
                Results_to_save[Left][Middle][MP][Max], Results_to_save[Left][
                    Middle][IPP][Max], Results_to_save[Left][Middle][IPD][Max],
                Results_to_save[Left][Ring][MP][Max], Results_to_save[Left][
                    Ring][IPP][Max], Results_to_save[Left][Ring][IPD][Max],
                Results_to_save[Left][Pinky][MP][Max], Results_to_save[Left][
                    Pinky][IPP][Max], Results_to_save[Left][Pinky][IPD][Max],
                Results_to_save[Right][Thumb][MP][
                    Max], Results_to_save[Right][Thumb][IPP][Max],
                Results_to_save[Right][Index][MP][Max], Results_to_save[Right][
                    Index][IPP][Max], Results_to_save[Right][Index][IPD][Max],
                Results_to_save[Right][Middle][MP][Max], Results_to_save[Right][
                    Middle][IPP][Max], Results_to_save[Right][Middle][IPD][Max],
                Results_to_save[Right][Ring][MP][Max], Results_to_save[Right][
                    Ring][IPP][Max], Results_to_save[Right][Ring][IPD][Max],
                Results_to_save[Right][Pinky][MP][Max], Results_to_save[Right][
                    Pinky][IPP][Max], Results_to_save[Right][Pinky][IPD][Max],
                Results_to_save[Left][Thumb][MP][
                    Min], Results_to_save[Left][Thumb][IPP][Min],
                Results_to_save[Left][Index][MP][Min], Results_to_save[Left][
                    Index][IPP][Min], Results_to_save[Left][Index][IPD][Min],
                Results_to_save[Left][Middle][MP][Min], Results_to_save[Left][
                    Middle][IPP][Min], Results_to_save[Left][Middle][IPD][Min],
                Results_to_save[Left][Ring][MP][Min], Results_to_save[Left][
                    Ring][IPP][Min], Results_to_save[Left][Ring][IPD][Min],
                Results_to_save[Left][Pinky][MP][Min], Results_to_save[Left][
                    Pinky][IPP][Min], Results_to_save[Left][Pinky][IPD][Min],
                Results_to_save[Right][Thumb][MP][
                    Min], Results_to_save[Right][Thumb][IPP][Min],
                Results_to_save[Right][Index][MP][Min], Results_to_save[Right][
                    Index][IPP][Min], Results_to_save[Right][Index][IPD][Min],
                Results_to_save[Right][Middle][MP][Min], Results_to_save[Right][
                    Middle][IPP][Min], Results_to_save[Right][Middle][IPD][Min],
                Results_to_save[Right][Ring][MP][Min], Results_to_save[Right][
                    Ring][IPP][Min], Results_to_save[Right][Ring][IPD][Min],
                Results_to_save[Right][Pinky][MP][Min], Results_to_save[Right][Pinky][IPP][Min], Results_to_save[Right][Pinky][IPD][Min]]

        # When the file of patient exists
        if os.path.exists(path_script + 'Results' + '/' + Report_Number + '.csv'):
            replace_row(path_script + 'Results' + '/' + Report_Number + '.csv', 5, [
                        "Date de mise a jour", str(datetime.datetime.fromtimestamp(time.time())).split(' ')[0]])
            replace_row(path_script + 'Results' + '/' + Report_Number + '.csv', 6, [
                        "Heure de mise a jour", str(datetime.datetime.fromtimestamp(time.time())).split(' ')[1][:8]])
            replace_row(path_script + 'Results' + '/' +
                        Report_Number + '.csv', 7, ["Ergotherapeute", User])

            # Read patient file
            bottle_list = []
            with open(path_script + 'Results' + '/' + Report_Number + '.csv', 'rb') as b:
                bottles = csv.reader(b)
                bottle_list.extend(bottles)
                b.close()

            # Extract index of last line
            line = len(bottle_list) - 1

            # Travel each line of angles measured
            while line >= 13:
                # Check if date of today already exists
                if bottle_list[line][0][:10] == str(datetime.datetime.fromtimestamp(time.time())).split(' ')[0]:
                    # Replace old data with actual data
                    replace_row(path_script + 'Results' + '/' +
                                Report_Number + '.csv', line, data)
                    # Interdict addition of new line
                    add_new_session = False
                    # Stop searching
                    break
                # Update line index
                line = line - 1

            # When we must add new line
            if add_new_session:
                with open(path_script + 'Results' + '/' + Report_Number + '.csv', 'ab') as fp:
                    # Define format as excel format
                    a = csv.writer(fp, delimiter=';')
                    # Write all headers in file of raw data
                    a.writerow(data)
                    fp.close()

        # When the file of patient does not exist
        if not os.path.exists(path_script + 'Results' + '/' + Report_Number + '.csv'):
            with open(path_script + 'Results' + '/' + Report_Number + '.csv', 'wb') as fp:
                # Define format as excel format
                a = csv.writer(fp, delimiter=';')
                # Write all headers in file of raw data
                a.writerow(["Prenom", Patient_First_Name])
                a.writerow(["Nom", Patient_Name])
                a.writerow(["Date de naissance", Birth_Day])
                a.writerow(["Sexe", Sex])
                a.writerow(["Numero de dossier", Report_Number])
                a.writerow(["Date de mise a jour", str(
                    datetime.datetime.fromtimestamp(time.time())).split(' ')[0]])
                a.writerow(["Heure de mise a jour", str(
                    datetime.datetime.fromtimestamp(time.time())).split(' ')[1][:8]])
                a.writerow(["Ergotherapeute", User])
                a.writerow(
                    "---------------------------------------------------------")
                a.writerow([" ", " ",
                            "Flexion", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            "Extension", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " "])
                a.writerow([" ", " ",
                            "Main Gauche", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            "Main Droite", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            "Main Gauche", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            "Main Droite", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " ",
                            " ", " ", " "])
                a.writerow([" ", " ",
                            "D1", " ",
                            "D2", " ", " ",
                            "D3", " ", " ",
                            "D4", " ", " ",
                            "D5", " ", " ",
                            "D1", " ",
                            "D2", " ", " ",
                            "D3", " ", " ",
                            "D4", " ", " ",
                            "D5", " ", " ",
                            "D1", " ",
                            "D2", " ", " ",
                            "D3", " ", " ",
                            "D4", " ", " ",
                            "D5", " ", " ",
                            "D1", " ",
                            "D2", " ", " ",
                            "D3", " ", " ",
                            "D4", " ", " ",
                            "D5", " ", " "])
                a.writerow(["Date de la seance", "Heure de fin",
                            "MP", "IP",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IP",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IP",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IP",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD",
                            "MP", "IPP", "IPD"])
                a.writerow(data)
                fp.close()

    # Function for start thread of acquisition
    def setupUpdateThread(self):

        # Connect thread for get angles calculated
        self.updateThread.progress.connect(self.updateText, QtCore.Qt.BlockingQueuedConnection)
        # Start thread if it is not running
        if not self.updateThread.isRunning():
            self.updateThread.start()

    # Function for display angles
    def updateText(self, text):

        # Connect function for delete and zoom an angle
        self.updateThread.progress.connect(
            self.zoomDelete, QtCore.Qt.BlockingQueuedConnection)
        self.i += 1
        # For each angle

        global signalWarning
        global warningMessage

        if not Acquisition:
            mainPage.statusbar.showMessage(QtGui.QApplication.translate(
                "TabWidget", "", None, QtGui.QApplication.UnicodeUTF8))

        if Acquisition:

            if not signalWarning:
                mainPage.statusbar.showMessage(QtGui.QApplication.translate(
                    "TabWidget", "", None, QtGui.QApplication.UnicodeUTF8))
                # Create icon
                newIcon = QtGui.QIcon()
                newIcon.addPixmap(QtGui.QPixmap(
                    path_script + "filesUi/imagesUi/green_circle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

                # Modify icon
                self.circle_signal.setIcon(newIcon)

            if signalWarning:
                mainPage.statusbar.showMessage(QtGui.QApplication.translate(
                    "TabWidget", warningMessage, None, QtGui.QApplication.UnicodeUTF8))
                # Create icon
                newIcon = QtGui.QIcon()
                newIcon.addPixmap(QtGui.QPixmap(
                    path_script + "filesUi/imagesUi/mauve_circle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

                # Modify icon
                self.circle_signal.setIcon(newIcon)

        for Hand_select in User_Choices[0]:
            for Finger_select in User_Choices[1]:
                for Joint_select in Finger_select[1]:
                    for Data_select in [Min, Value, Max]:

                        if self.i == 2:
                            self.animated = not self.animated
                            self.i = 0

                        self.circle_signal.setEnabled(self.animated)

                        # Get the display button corresponding
                        label = getattr(self, self.labels[Hand_select][
                                        Finger_select[0]][Joint_select][Data_select])

                        # Get the select button corresponding
                        button = getattr(self, self.buttons[Hand_select][
                                         Finger_select[0]][Joint_select][Data_select])

                        # Check if user select this angle
                        if button.isChecked():

                            # Not display minimum if user select flexion
                            # movement
                            if self.flexion_2.isChecked() and Data_select == Min:
                                label.setVisible(False)
                                text[Hand_select][Finger_select[0]][
                                    Joint_select][Data_select] = ""

                            # Display and save maximum if user select flexion
                            # movement
                            if self.flexion_2.isChecked() and Data_select == Max:
                                label.setVisible(True)
                                Results_to_save[Hand_select][Finger_select[0]][Joint_select][
                                    Data_select] = text[Hand_select][Finger_select[0]][Joint_select][Data_select]

                            # Not display maximum if user select extension
                            # movement
                            if self.extension_2.isChecked() and Data_select == Max:
                                label.setVisible(False)
                                text[Hand_select][Finger_select[0]][
                                    Joint_select][Data_select] = ""

                            # Display and save minimum if user select extension
                            # movement
                            if self.extension_2.isChecked() and Data_select == Min:
                                label.setVisible(True)
                                Results_to_save[Hand_select][Finger_select[0]][Joint_select][
                                    Data_select] = text[Hand_select][Finger_select[0]][Joint_select][Data_select]

                            # Display and save minimum if user select flexion
                            # movement
                            if self.combine_2.isChecked() and (Data_select == Min or Data_select == Max):
                                label.setVisible(True)
                                Results_to_save[Hand_select][Finger_select[0]][Joint_select][
                                    Data_select] = text[Hand_select][Finger_select[0]][Joint_select][Data_select]

                            # If it is angle selected by user for zoom
                            if Hand_select == self.handZoom and Finger_select[0] == self.fingerZoom and Joint_select == self.jointZoom and Data_select == self.dataZoom:
                                # Surround angle selected by user for zoom
                                label.setStyleSheet("font: 14pt \"Book Antiqua\";\n"
                                                    "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.977, y2:0.943182, stop:0 rgba(0, 0, 0, 0), stop:1 rgba(255, 255, 255, 255));\n")
                                label.setFlat(False)

                            # For others angles
                            else:

                                # Set flat for button aspect
                                label.setFlat(True)

                                # Display minimum in green
                                if Data_select == Min:
                                    label.setStyleSheet("font: 14pt \"Book Antiqua\";\n"
                                                        "color: rgb(0, 85, 0);")

                                # Display value in black
                                if Data_select == Value:
                                    label.setStyleSheet("font: 14pt \"Book Antiqua\";\n"
                                                        "color: rgb(0, 0, 0);")

                                # Display maximum in red
                                if Data_select == Max:
                                    label.setStyleSheet("font: 14pt \"Book Antiqua\";\n"
                                                        "color: rgb(255, 0, 0);")

                                if Data_select == Min or Data_select == Max:
                                    item = QtGui.QTableWidgetItem(text[Hand_select][Finger_select[0]][
                                                                  Joint_select][Data_select])
                                    item.setTextAlignment(
                                        QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                                    item.setBackground(
                                        QtGui.QColor(245, 245, 255))
                                    self.tableWidget.setItem(self.cellV[Hand_select][Finger_select[0]][Joint_select][
                                                             Data_select], self.cellH[Hand_select][Finger_select[0]][Joint_select][Data_select], item)

                            # Display angle
                            label.setText(text[Hand_select][Finger_select[0]][
                                          Joint_select][Data_select])

    # Function for zoom and delete angle value
    def zoomDelete(self, text):

        # Check if user click an angle for zoom
        if (self.handDelete == Left or self.handDelete == Right):

            # Reset value of angle
            if self.dataDelete == Min:
                Hands_Angle[self.handDelete][self.fingerDelete][
                    self.jointDelete][self.dataDelete] = 180
            if self.dataDelete == Max:
                Hands_Angle[self.handDelete][self.fingerDelete][
                    self.jointDelete][self.dataDelete] = -180
            if self.dataDelete == Value:
                Hands_Angle[self.handDelete][self.fingerDelete][
                    self.jointDelete][self.dataDelete] = 0
            Results[self.handDelete][self.fingerDelete][
                self.jointDelete][self.dataDelete] = "***"

        # Check if user click an left angle for delete
        if self.handZoom == Left:
            # Reset value of left zoom
            self.zoom_gauche.setText(text[self.handZoom][self.fingerZoom][
                                     self.jointZoom][self.dataZoom])
            # Clear right zoom
            self.zoom_droite.setText("")

        # Check if user click an right angle for delete
        if self.handZoom == Right:
            # Reset value of left zoom
            self.zoom_droite.setText(text[self.handZoom][self.fingerZoom][
                                     self.jointZoom][self.dataZoom])
            # Clear left zoom
            self.zoom_gauche.setText("")

    # Functions corresponding to each display button of angle
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

#=========================================================================

#== CLASS: mainPage; MainWidget for GUI ==================================


class mainPage(QtGui.QMainWindow, mainPageUi.Ui_MainWindow):

    # Function for initialisation MainWindow
    def __init__(self, parent=None):

        # Initialisation of class
        super(mainPage, self).__init__(parent)
        self.setupUi(self)

        # Create tab widget for GUI
        self.widget = page()

        # Set central widget of main window
        self.setCentralWidget(self.widget)

        # Status bar font
        self.statusbar.setStyleSheet(
            "font: italic 100 14pt \"Book Antiqua\";\n""color: rgb(255, 0, 0);\n")

if __name__ == '__main__':

    #-------------------------------------------------------------------------
    # Global variables
    #-------------------------------------------------------------------------

    # Index of data, joints, fingers and hands
    # Define type of data
    Min, Value, Max = 0, 1, 2
    # Define type of each joint
    MP, IPP, IPD = 0, 1, 2
    # Define type of each finger
    Thumb, Index, Middle, Ring, Pinky = 0, 1, 2, 3, 4
    # Define type of each hand
    Left, Right = 0, 1

    # List of finger extrema, joints, fingers and hands
    Hands_Angle = [[[[180, 0, -180], [180, 0, -180]],                       # [Min, Value, Max]--> [MP][IPP] --> [Thumb]
                    # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Index]
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                    # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Middle]
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                    # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Ring]
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]]],      # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Pinky]
                   [[[180, 0, -180], [180, 0, -180]],                       # Same for right hand
                    # Same for right hand
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                    # Same for right hand
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                    # Same for right hand
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]]]]      # Same for right hand

    # Results for display
    Results = [[[[' ', ' ', ' '], [' ', ' ', ' ']],
                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]],
               [[[' ', ' ', ' '], [' ', ' ', ' ']],
                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]]]

    # Results for save
    Results_to_save = [[[[' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]],
                       [[[' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
                        [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]]]

    # List of choices
    User_Choices = [[Left, Right],                             # List of hand selected by user
                    [[Thumb, [MP, IPP]],                        # Finger joints : [finger 1,[list of joints selected]]
                     # Finger joints : [finger 2,[list of joints selected]]
                     [Index, [MP, IPP, IPD]],
                     # Finger joints : [finger 3,[list of joints selected]]
                     [Middle, [MP, IPP, IPD]],
                     # Finger joints : [finger 4,[list of joints selected]]
                     [Ring, [MP, IPP, IPD]],
                     [Pinky, [MP, IPP, IPD]]]]                   # Finger joints : [finger 5,[list of joints selected]]

    # Patient data
    Patient_First_Name, Patient_Name, Report_Number, Birth_Day, Last_session, Sex, User = str, str, str, str, str, str, str

    # Start time
    start = time.time()

    # Create application GUI
    app = QtGui.QApplication(sys.argv)

    # Create contents GUI
    mainPage = mainPage()

    # Show GUI
    mainPage.showMaximized()

    # Execute application GUI
    r = app.exec_()

    # Exit application GUI
    sys.exit(r)

