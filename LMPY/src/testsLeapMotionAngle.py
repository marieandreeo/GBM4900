#!/usr/bin/env python

## @package testsLeapMotionAngle
#
# - program of tests : save data for results analyse and validation of software
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

# == IMPORTS ===========================================================================================================

import sys                  # For using system parameters
import os                   # For using system parameters
import math                 # Calculate angle
import csv                  # Save in format .csv
import time                 # Check the time
import signal               # Exit program at any time when user press enter
import threading            # Make multi-threading
import Queue                # Make queue data
import datetime             # Determinate date

sys.path.insert(0, "../lib") # CHANGEMENT ICI

# Check if the correct LeapMotion library is installed
try:
    import Leap
except ImportError:
    print '\n---------------------------- Leap Motion Library not installed --------------------------\n'
    print 'Install library at   : <https://developer.leapmotion.com/downloads/skeletal-beta> '
    print 'For more information : <https://www.youtube.com/watch?v=T9k7rdY625M> \n'
    print '---------------------------------------Exit program. ------------------------------------\n'
    sys.exit(2)

# Check if the correct python version in installed----not sys.version_info[:3] == (2, 7, 6):
if sys.version_info[:3] >=  (2, 7, 6):
    print '\n--------------------- The correct version of python is not installed --------------------\n'
    print 'You need to install Python 2.7.6 '
    print '1. Delete your version of python '
    print '2. Install Canopy: <https://store.enthought.com/> '
    print '3. Configure new Canopy python 2.7.6 in PyCharm \n'
    print '---------------------------------------Exit program. ------------------------------------\n'
    sys.exit(2)

# Check if colorama library is installed
try:
    import colorama
except ImportError:
    print '\n------------------------------ Coloram Library not installed ----------------------------\n'
    print 'Install library at : <https://pypi.python.org/pypi/colorama> \n'
    print '---------------------------------------Exit program. ------------------------------------\n'
    sys.exit(2)

#=======================================================================================================================

#== FUNCTION:  Display background of hands =============================================================================

def display_template():

    # Clear console before display
    os.system('cls' if os.name == 'nt' else 'clear')

    # For color and cursor movement
    colorama.init()

    # Define print format
    print  '\033[0;0H' + ('TEST PROCEDURE-GBM4900-04                                                                                                                                                                                        ')
    print  '\033[1;0H' + ('                                                TFEL                                                     '[::-1] + '                                               RIGHT                                                     ')
    print  '\033[2;0H' + ('                                                ----                                                     '[::-1] + '                                               -----                                                    ')
    print  '\033[3;0H' + ('                                                                                                         '[::-1] + '                                                                                                         ')
    print  '\033[4;0H' + ('                                               ELDDIM                                                    '[::-1] + '                                               MIDDLE                                                    ')
    print  '\033[5;0H' + ('                                          ...............                                                '[::-1] + '                                          ...............                                                ')
    print  '\033[6;0H' + ('                                          .             .                                                '[::-1] + '                                          .             .                                                ')
    print  '\033[7;0H' + ('                                          .             .                                                '[::-1] + '                                          .             .                                                ')
    print  '\033[8;0H' + ('                                          .             .                                                '[::-1] + '                                          .             .                                                ')
    print  '\033[9;0H' + ('                                          .             .                                                '[::-1] + '                                          .             .                                                ')
    print  '\033[10;0H' + ('                                XEDNI     .             .     GNIR                                       '[::-1] + '                                INDEX     .             .     RING                                       ')
    print  '\033[11;0H' + ('                            ...............             ...............                                  '[::-1] + '                            ...............             ...............                                  ')
    print  '\033[12;0H' + ('                            .             .     ' + results[Left][Middle][IPD][Max][::-1] + '     .             .                                  ')[::-1] + ('                            .             .     ' + results[Right][Middle][IPD][Max] + '     .             .                                  ')
    print  '\033[13;0H' + ('                            .             . ~ ~ ' + results[Left][Middle][IPD][Value][::-1] + ' ~ ~ .             .                                  ')[::-1] + ('                            .             . ~ ~ ' + results[Right][Middle][IPD][Value] + ' ~ ~ .             .                                  ')
    print  '\033[14;0H' + ('                            .             .     ' + results[Left][Middle][IPD][Min][::-1] + '     .             .                                  ')[::-1] + ('                            .             .     ' + results[Right][Middle][IPD][Min] + '     .             .                                  ')
    print  '\033[15;0H' + ('                            .             .             .             .                                  '[::-1] + '                            .             .             .             .                                  ')
    print  '\033[16;0H' + ('                            .     ' + results[Left][Index][IPD][Max][::-1] + '     .             .     ' + results[Left][Ring][IPD][Max][::-1] + '     .                                  ')[::-1] + ('                            .     ' + results[Right][Index][IPD][Max] + '     .             .     ' + results[Right][Ring][IPD][Max] + '     .                                  ')
    print  '\033[17;0H' + ('                            . ~ ~ ' + results[Left][Index][IPD][Value][::-1] + ' ~ ~ .             . ~ ~ ' + results[Left][Ring][IPD][Value][::-1] + ' ~ ~ .                                  ')[::-1] + ('                            . ~ ~ ' + results[Right][Index][IPD][Value] + ' ~ ~ .             . ~ ~ ' + results[Right][Ring][IPD][Value] + ' ~ ~ .                                  ')
    print  '\033[18;0H' + ('                            .     ' + results[Left][Index][IPD][Min][::-1] + '     .             .     ' + results[Left][Ring][IPD][Min][::-1] + '     .                                  ')[::-1] + ('                            .     ' + results[Right][Index][IPD][Min] + '     .             .     ' + results[Right][Ring][IPD][Max] + '     .                                  ')
    print  '\033[19;0H' + ('                            .             .             .             .                                  '[::-1] + '                            .             .             .             .                                  ')
    print  '\033[20;0H' + ('                            .             .             .             .                                  '[::-1] + '                            .             .             .             .                                  ')
    print  '\033[21;0H' + ('                            .             .             .             .                                  '[::-1] + '                            .             .             .             .                                  ')
    print  '\033[22;0H' + ('                            .             .             .             .    YKNIP                         '[::-1] + '                            .             .             .             .    PINKY                         ')
    print  '\033[23;0H' + ('                            .             .     ' + results[Left][Middle][IPP][Max][::-1] + '     .             ...............                    ')[::-1] + ('                            .             .     ' + results[Right][Middle][IPP][Max] + '     .             ...............                       ')
    print  '\033[24;0H' + ('                            .             . ~ ~ ' + results[Left][Middle][IPP][Value][::-1] + ' ~ ~ .             .             .                    ')[::-1] + ('                            .             . ~ ~ ' + results[Right][Middle][IPP][Value] + ' ~ ~ .             .             .                                  ')
    print  '\033[25;0H' + ('                            .             .     ' + results[Left][Middle][IPP][Min][::-1] + '     .             .             .                    ')[::-1] + ('                            .             .     ' + results[Right][Middle][IPP][Min] + '     .             .             .                                  ')
    print  '\033[26;0H' + ('                            .     ' + results[Left][Index][IPP][Max][::-1] + '     .             .     ' + results[Left][Ring][IPP][Max][::-1] + '     .     ' + results[Left][Pinky][IPD][Max][::-1] + '     .                    ')[::-1] + ('                            .     ' + results[Right][Index][IPP][Max] + '     .             .     ' + results[Right][Ring][IPP][Max] + '     .     ' + results[Right][Pinky][IPD][Max] + '     .                    ')
    print  '\033[27;0H' + ('                            . ~ ~ ' + results[Left][Index][IPP][Value][::-1] + ' ~ ~ .             . ~ ~ ' + results[Left][Ring][IPP][Value][::-1] + ' ~ ~ . ~ ~ ' + results[Left][Pinky][IPD][Value][::-1] + ' ~ ~ .                    ')[::-1] + ('                            . ~ ~ ' + results[Right][Index][IPP][Value] + ' ~ ~ .             . ~ ~ ' + results[Right][Ring][IPP][Value] + ' ~ ~ . ~ ~ ' + results[Right][Pinky][IPD][Value] + ' ~ ~ .                    ')
    print  '\033[28;0H' + ('                            .     ' + results[Left][Index][IPP][Min][::-1] + '     .             .     ' + results[Left][Ring][IPP][Min][::-1] + '     .     ' + results[Left][Pinky][IPD][Min][::-1] + '     .                    ')[::-1] + ('                            .     ' + results[Right][Index][IPP][Min] + '     .             .     ' + results[Right][Ring][IPP][Min] + '     .     ' + results[Right][Pinky][IPD][Min] + '     .                    ')
    print  '\033[29;0H' + ('                            .             .             .             .             .                    '[::-1] + '                            .             .             .             .             .                    ')
    print  '\033[30;0H' + ('                            .             .             .             .             .                    '[::-1] + '                            .             .             .             .             .                    ')
    print  '\033[31;0H' + ('                            .             .             .             .             .                    '[::-1] + '                            .             .             .             .             .                    ')
    print  '\033[32;0H' + ('                            .             .             .             .     ' + results[Left][Pinky][IPP][Max][::-1] + '     .                    ')[::-1] + ('                            .             .             .             .     ' + results[Right][Pinky][IPP][Max] + '     .                    ')
    print  '\033[33;0H' + ('                            .             .             .             . ~ ~ ' + results[Left][Pinky][IPP][Value][::-1] + ' ~ ~ .                    ')[::-1] + ('                            .             .             .             . ~ ~ ' + results[Right][Pinky][IPP][Value] + ' ~ ~ .                    ')
    print  '\033[34;0H' + ('                            .             .             .             .     ' + results[Left][Pinky][IPP][Min][::-1] + '     .                    ')[::-1] + ('                            .             .             .             .     ' + results[Right][Pinky][IPP][Min] + '     .                    ')
    print  '\033[35;0H' + ('                  BMUHT     .             .             .             .             .                    '[::-1] + '                  THUMB     .             .             .             .             .                    ')
    print  '\033[36;0H' + ('             ................             .             .             .             .                    '[::-1] + '             ................             .             .             .             .                    ')
    print  '\033[37;0H' + ('             .              .     ' + results[Left][Index][MP][Max][::-1] + '     .     ' + results[Left][Middle][MP][Max][::-1] + '     .     ' + results[Left][Ring][MP][Max][::-1] + '     .     ' + results[Left][Pinky][MP][Max][::-1] + '     .                    ')[::-1] + ('             .              .     ' + results[Right][Index][MP][Max] + '     .     ' + results[Right][Middle][MP][Max] + '     .     ' + results[Right][Ring][MP][Max] + '     .     ' + results[Right][Pinky][MP][Max] + '     .                    ')
    print  '\033[38;0H' + ('             .              . ~ ~ ' + results[Left][Index][MP][Value][::-1] + ' ~ ~ . ~ ~ ' + results[Left][Middle][MP][Value][::-1] + ' ~ ~ . ~ ~ ' + results[Left][Ring][MP][Value][::-1] + ' ~ ~ . ~ ~ ' + results[Left][Pinky][MP][Value][::-1] + ' ~ ~ .                    ')[::-1] + ('             .              . ~ ~ ' + results[Right][Index][MP][Value] + ' ~ ~ . ~ ~ ' + results[Right][Middle][MP][Value] + ' ~ ~ . ~ ~ ' + results[Right][Ring][MP][Value] + ' ~ ~ . ~ ~ ' + results[Right][Pinky][MP][Value] + ' ~ ~ .                    ')
    print  '\033[39;0H' + ('             .              .     ' + results[Left][Index][MP][Min][::-1] + '     .     ' + results[Left][Middle][MP][Min][::-1] + '     .     ' + results[Left][Ring][MP][Min][::-1] + '     .     ' + results[Left][Pinky][MP][Min][::-1] + '     .                    ')[::-1] + ('             .              .     ' + results[Right][Index][MP][Min] + '     .     ' + results[Right][Middle][MP][Min] + '     .     ' + results[Right][Ring][MP][Min] + '     .     ' + results[Right][Pinky][MP][Min] + '     .                    ')
    print  '\033[40;0H' + ('             .              .             |             |             |             .                    '[::-1] + '             .              .             |             |             |             .                    ')
    print  '\033[41;0H' + ('             .              .                                                       .                    '[::-1] + '             .              .                                                       .                    ')
    print  '\033[42;0H' + ('             .     ' + results[Left][Thumb][IPP][Max][::-1] + '      .             |             |             |             .                    ')[::-1] + ('             .     ' + results[Right][Thumb][IPP][Max] + '      .             |             |             |             .                    ')
    print  '\033[43;0H' + ('             . ~ ~ ' + results[Left][Thumb][IPP][Value][::-1] + ' ~ ~  .                                                       .                    ')[::-1] + ('             . ~ ~ ' + results[Right][Thumb][IPP][Value] + ' ~ ~  .                                                       .                    ')
    print  '\033[44;0H' + ('             .     ' + results[Left][Thumb][IPP][Min][::-1] + '      .             |             |             |             .                    ')[::-1] + ('             .     ' + results[Right][Thumb][IPP][Min] + '      .             |             |             |             .                    ')
    print  '\033[45;0H' + ('             .              .                                                       .                    '[::-1] + '             .              .                                                       .                    ')
    print  '\033[46;0H' + ('             .              .             |             |             |             .                    '[::-1] + '             .              .             |             |             |             .                    ')
    print  '\033[47;0H' + ('             .              .                                                       .                    '[::-1] + '             .              .                                                       .                    ')
    print  '\033[48;0H' + ('             .              .             |             |             |             .                    '[::-1] + '             .              .             |             |             |             .                    ')
    print  '\033[49;0H' + ('             .              .                                                       .                    '[::-1] + '             .              .                                                       .                    ')
    print  '\033[50;0H' + ('              .    ' + results[Left][Thumb][MP][Max][::-1] + '                    |             |             |             .                    ')[::-1] + ('              .    ' + results[Right][Thumb][MP][Max] + '                    |             |             |             .                    ')
    print  '\033[51;0H' + ('               .    ' + results[Left][Thumb][MP][Value][::-1] + '                                                             .                    ')[::-1] + ('               .    ' + results[Right][Thumb][MP][Value] + '                                                             .                    ')
    print  '\033[52;0H' + ('                .    ' + results[Left][Thumb][MP][Min][::-1] + '                                                            .                    ')[::-1] + ('                .    ' + results[Right][Thumb][MP][Min] + '                                                            .                    ')
    print  '\033[53;0H' + ('                 .                                                                  .                    '[::-1] + '                 .                                                                  .                    ')
    print  '\033[54;0H' + ('                  .                                                                 .                    '[::-1] + '                  .                                                                 .                    ')
    print  '\033[55;0H' + ('                   .                                                                .                    '[::-1] + '                   .                                                                .                    ')
    print  '\033[56;0H' + ('                    .                                                               .                    '[::-1] + '                    .                                                               .                    ')
    print  '\033[57;0H' + ('                     .                                                              .                    '[::-1] + '                     .                                                              .                    ')
    print  '\033[58;0H' + (' ')
    print  '\033[59;0H' + (' ')
    print  '\033[60;0H' + ('Press Enter to quit')

#=======================================================================================================================

#== FUNCTION:  Display results =========================================================================================

def display(Hands_Angle):

    # Red color detection of hyper-extension initialized
    color_in_red = False

    # Actualize results printing with user choices selected
    for Hand_select in User_Choices[0]:                                             # Each hand chosen
        for Finger_select in User_Choices[1]:                                       # Each finger chosen for each hand
            for Joint_select in Finger_select[1]:                                   # Each joint chosen for each finger

                # Check if Leap Motion acquire frame
                if Hands_Angle[Hand_select][Finger_select[0]][Joint_select][Value] !=0:

                    # Store temporarily the results
                    temp = Hands_Angle[Hand_select][Finger_select[0]][Joint_select][Value]

                    # Store results for saving in file
                    results_to_save[Hand_select][Finger_select[0]][Joint_select][Value] = str(temp).replace('.',',')

                    # Round angle amplitude
                    temp = round(temp)

                    # Convert angle amplitude float to integer
                    temp = int(temp)

                    # Check if it is hyper-extension
                    if temp < 0:
                        color_in_red = True
                        temp = -temp

                    # Stock results in display format
                    temp = str(temp).zfill(3)
                    results[Hand_select][Finger_select[0]][Joint_select][Value] = temp

                    # Color in red in console if it is hyper-extension
                    if color_in_red:
                        # Initialize color parameter
                        colorama.init()
                        # Apply color ASCII code
                        results[Hand_select][Finger_select[0]][Joint_select][Value] = \
                            colorama.Fore.RED + temp + colorama.Fore.RESET
                        # Initialize hyper-extension marker
                        color_in_red = False

        # Define print format without clear background
        print'\033[14;55H' + results[Left][Middle][IPD][Value]
        print'\033[14;154H' + results[Right][Middle][IPD][Value]

        print'\033[25;55H' + results[Left][Middle][IPP][Value]
        print'\033[25;154H' + results[Right][Middle][IPP][Value]

        print'\033[39;55H' + results[Left][Middle][MP][Value]
        print'\033[39;154H' + results[Right][Middle][MP][Value]

        print'\033[18;41H' + results[Left][Ring][IPD][Value]
        print'\033[18;168H' + results[Right][Ring][IPD][Value]

        print'\033[28;41H' + results[Left][Ring][IPP][Value]
        print'\033[28;168H' + results[Right][Ring][IPP][Value]

        print'\033[39;41H' + results[Left][Ring][MP][Value]
        print'\033[39;168H' + results[Right][Ring][MP][Value]

        print'\033[18;69H' + results[Left][Index][IPD][Value]
        print'\033[18;140H' + results[Right][Index][IPD][Value]

        print'\033[28;69H' + results[Left][Index][IPP][Value]
        print'\033[28;140H' + results[Right][Index][IPP][Value]

        print'\033[39;69H' + results[Left][Index][MP][Value]
        print'\033[39;140H' + results[Right][Index][MP][Value]

        print'\033[28;27H' + results[Left][Pinky][IPD][Value]
        print'\033[28;182H' + results[Right][Pinky][IPD][Value]

        print'\033[34;27H' + results[Left][Pinky][IPP][Value]
        print'\033[34;182H' + results[Right][Pinky][IPP][Value]

        print'\033[39;27H' + results[Left][Pinky][MP][Value]
        print'\033[39;182H' + results[Right][Pinky][MP][Value]

        print'\033[44;84H' + results[Left][Thumb][IPP][Value]
        print'\033[44;125H' + results[Right][Thumb][IPP][Value]

        print'\033[52;83H' + results[Left][Thumb][MP][Value]
        print'\033[52;126H' + results[Right][Thumb][MP][Value]

#=======================================================================================================================

#== FUNCTION: Do dot product: returns dot product of 2 3D unit vectors =================================================

def dot_product(v1, v2):
    a = v1[0]                   # x for vector 1
    b = v2[0]                   # x for vector 2
    c = v1[1]                   # y for vector 1
    d = v2[1]                   # y for vector 2
    e = v1[2]                   # z for vector 1
    f = v2[2]                   # z for vector 2
    g = a * b + c * d + e * f   # do dot product of v1 and v2
    return g

#=======================================================================================================================

#== FUNCTION: save ; Write angles calculated in files  =================================================================

def save(Hands_Angle):

    # Define global variable for save only if it's necessary
    global data_ok

    # Check if Leap Motion acquire data
    if set(sum(sum(sum(results_to_save, []), []), [])) != {'-'}:

        # Permit to save data
        data_ok = True

        # Create files if this is not done and write headers
        save_headers()

        # Search start time in file of raw data
        bottle_list = []
        with open(path_script+'Results'+'/'+Patient_First_Name+'_'+Patient_Name+'/'+Report_Number
                  +'_'+'raw.csv', 'rb') as b:
            bottles = csv.reader(b)
            bottle_list.extend(bottles)
            b.close()

        # Extract date parameters
        Year, Month, Day = str(bottle_list[5][0][-8:]).split('-')
        Year = int('20'+Year)
        Month = int(Month)
        Day = int(Day)

        # Extract time parameters
        Hour, Minute, Second = str (bottle_list[6][0][-8:]).split (':')
        Hour = int (Hour)
        Minute = int (Minute)
        Second = int (Second)

        # Convert start time in seconds
        start = datetime.datetime(Year, Month, Day, Hour, Minute, Second)

        # Determinate the between start and now
        t = str(round((time.time()-time.mktime(start.timetuple())), 1000)).replace('.',',')

        # Data to saving in file
        data = [str(t),
                results_to_save[Left][Thumb][MP][Value],results_to_save[Left][Thumb][IPP][Value],
                results_to_save[Left][Index][MP][Value],results_to_save[Left][Index][IPP][Value],results_to_save[Left][Index][IPD][Value],
                results_to_save[Left][Middle][MP][Value],results_to_save[Left][Middle][IPP][Value],results_to_save[Left][Middle][IPD][Value],
                results_to_save[Left][Ring][MP][Value],results_to_save[Left][Ring][IPP][Value],results_to_save[Left][Ring][IPD][Value],
                results_to_save[Left][Pinky][MP][Value],results_to_save[Left][Pinky][IPP][Value],results_to_save[Left][Pinky][IPD][Value],
                results_to_save[Right][Thumb][MP][Value],results_to_save[Right][Thumb][IPP][Value],
                results_to_save[Right][Index][MP][Value],results_to_save[Right][Index][IPP][Value],results_to_save[Right][Index][IPD][Value],
                results_to_save[Right][Middle][MP][Value],results_to_save[Right][Middle][IPP][Value],results_to_save[Right][Middle][IPD][Value],
                results_to_save[Right][Ring][MP][Value],results_to_save[Right][Ring][IPP][Value],results_to_save[Right][Ring][IPD][Value],
                results_to_save[Right][Pinky][MP][Value],results_to_save[Right][Pinky][IPP][Value],results_to_save[Right][Pinky][IPD][Value]]

    #-------------------------------------------------------------------------------------------------------------------
    # FILE OF RAW DATA
    #-------------------------------------------------------------------------------------------------------------------

    # Write data in file each time if Leap Motion acquire data
    if data_ok:
        with open(path_script+'results'+'/'+Patient_First_Name+'_'+Patient_Name+'/'+Report_Number+'_' + 'raw.csv', 'ab') as fp:
            # Define format as excel format
            a = csv.writer(fp, delimiter=';')
            # Write all data in file
            a.writerow(data)
            # Close file
            fp.close()

#=======================================================================================================================

#== FUNCTION: save_headers ; Create and write headers in files  ========================================================

def save_headers():

    # Define global variable for session number
    global Session_Number

    # Define path of script repertory as global variable
    global path_script

    # Extract path of script repertory
    path_script = os.getcwd() + '/'

    # Create repertory of all files if it does not exist
    if not os.path.exists(path_script+'Results'):
        os.makedirs(path_script+'Results')

    # Create repertory of patients files if it does not exist
    if not os.path.exists(path_script+'Results'+'/'+Patient_First_Name+'_'+Patient_Name):
        os.makedirs(path_script+'Results'+'/'+Patient_First_Name+'_'+Patient_Name)

    # Determinate number of session and create folder of new session
    while True:
        # Check if old session exist
        if os.path.exists(path_script+'Results'+'/'+Patient_First_Name+'_'+Patient_Name
                          + '/' + Report_Number + '_' + 'raw.csv'):
            # Extract data of file for checking if this acquisition is done the same day
            bottle_list = []
            with open(path_script+'Results'+'/'+Patient_First_Name+'_'+Patient_Name+'/'+Report_Number
                      +'_'+'raw.csv', 'rb') as b:
                bottles = csv.reader(b)
                bottle_list.extend(bottles)
                b.close()
            # Check if this acquisition is done the same day
            if str(["Date", str(datetime.datetime.fromtimestamp(time.time())).split(' ')[0]])[-10:-2] == bottle_list[5][0][-8:]:
                # Stop searching and overwrite data in the session files
                break
            else:
                # Search the following session file
                Session_Number += 1
        # Create the new session file with new session number
        else:
            with open(path_script+'Results'+'/'+Patient_First_Name+'_'+Patient_Name+'/'+Report_Number
                      +'_'+'raw.csv', 'ab') as fp:
                # Define format as excel format
                a = csv.writer(fp, delimiter=';')
                # Write all headers in file of raw data
                a.writerow(["First Name", Patient_First_Name])
                a.writerow(["Name", Patient_Name])
                a.writerow(["Age", Patient_Age])
                a.writerow(["Report", Report_Number])
                a.writerow(["Session", Session_Number])
                a.writerow(["Date", str(datetime.datetime.fromtimestamp(time.time())).split(' ')[0]])
                a.writerow(["Hour", str(datetime.datetime.fromtimestamp(time.time())).split(' ')[1][:8]])
                a.writerow("---------------------------------------------------------")
                a.writerow(["Time",
                            "THUMB MP LEFT", "THUMB IP LEFT",
                            "INDEX MP LEFT", "INDEX IPP LEFT", "INDEX IPD LEFT",
                            "MIDDLE MP LEFT", "MIDDLE IPP LEFT", "MIDDLE IPD LEFT",
                            "RING MP LEFT", "RING IPP LEFT", "RING IPD LEFT",
                            "PINKY MP LEFT", "PINKY IPP LEFT", "PINKY IPD LEFT",
                            "THUMB MP RIGHT", "THUMB IP RIGHT",
                            "INDEX MP RIGHT", "INDEX IPP RIGHT", "INDEX IPD RIGHT",
                            "MIDDLE MP RIGHT", "MIDDLE IPP RIGHT", "MIDDLE IPD RIGHT",
                            "RING MP RIGHT", "RING IPP RIGHT", "RING IPD RIGHT",
                            "PINKY MP RIGHT", "PINKY IPP RIGHT", "PINKY IPD RIGHT"])

                # Close file
                fp.close()

#=======================================================================================================================

#== CLASS: SampleListener; receives events from controller and executes accordingly ====================================

class SampleListener(Leap.Listener):

    # Function executed for each frame:
    def on_frame(self, controller):

        # Get the most recent frame and report some basic information
        frame = controller.frame()

        #----------------------------------------------------
        # Get hands (for each hand in the current frame...):
        #----------------------------------------------------
        for hand in frame.hands:

            # Find out which hand is in the frame (h = 0 for left and 1 for right)
            h = 0 if hand.is_left else 1

            # Filter data : permit only data for a minimum confidence equal to 0.5
            if hand.confidence >= 0.5:

                #---------------------------------------------------------------------
                # Get fingers (for each finger of each hand in the current frame...):
                #---------------------------------------------------------------------
                for finger in hand.fingers:

                    #--------------------------------------------------------------------------------
                    # Get bones (for each bone of each finger of each hand in the current frame...):
                    #--------------------------------------------------------------------------------
                    # If its a thumb...
                    if finger.type() == 0:

                        # Iterate through Proximal, Intermediate and Distal (no Metacarpal).
                        for b in range(2, 4):

                            # Determinate joint type
                            j = b - 2

                            # Identification of the previous bone
                            bone1 = finger.bone(b - 1)

                            # Identification of the actual bone
                            bone2 = finger.bone(b)

                            # For MP
                            if b == 2:

                               # Store direction unit vector of previous bone in v0
                                v0 = bone1.basis.y_basis
                                # Store direction unit vector of actual bone
                                v1 = bone2.basis.y_basis
                                # Calculate scalar product
                                sp = dot_product(v0, v1)

                                # Verify if scalar product is valid, i.e. it between -1 and 1
                                if (sp <= 1) and (sp >= -1) and (v0 != v1):

                                    # Get angle (in radians) between the 2 unit vectors
                                    angle_in_radians = math.acos(sp)
                                    # Get angle in degrees
                                    angle_in_degrees = math.degrees(angle_in_radians)

                                    # Detect hyper-extension with direction bone1 and normal bone2
                                    if dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                                        angle_in_degrees = -angle_in_degrees

                                    # Store actual value of angle
                                    Hands_Angle[h][finger.type()][j][Value] = angle_in_degrees

                            # For others joints
                            else:

                                # Determinate each length in triangle
                                length_a = bone1.length
                                length_b = bone2.length
                                length_c = bone2.next_joint.distance_to(bone1.prev_joint)

                                # Apply cos law
                                sp = (length_c*length_c-length_b*length_b-length_a*length_a)/(2*length_a*length_b)

                                # Verify if scalar product is valid, i.e. it between -1 and 1
                                if (sp <= 1) and (sp >= -1):

                                    # Get angle (in radians) between the 2 unit vectors
                                    angle_in_radians = math.acos(sp)
                                    # Get angle in degrees
                                    angle_in_degrees = math.degrees(angle_in_radians)

                                    # Detect hyper-extension with direction bone1 and normal bone2
                                    if dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                                        angle_in_degrees = 0.00001

                                    # Store actual value of angle
                                    Hands_Angle[h][finger.type()][j][Value] = angle_in_degrees

                    # ... otherwise (i.e., if its NOT a thumb)...
                    else:

                        # Iterate through Proximal, Intermediate and Distal (no Metacarpal).
                        for b in range(1, 4):

                            # Determinate joint type
                            j = b - 1

                            # Identification of the previous bone
                            bone1 = finger.bone(b - 1)

                            # Identification of the actual bone
                            bone2 = finger.bone(b)

                            # For MP
                            if b == 1:

                                # Store direction unit vector of previous bone in v0
                                v0 = bone1.basis.y_basis
                                # Store direction unit vector of actual bone
                                v1 = bone2.basis.y_basis
                                # Calculate scalar product
                                sp = dot_product(v0, v1)

                                # Verify if scalar product is valid, i.e. it between -1 and 1
                                if (sp <= 1) and (sp >= -1) and (v0 != v1):

                                    # Get angle (in radians) between the 2 unit vectors
                                    angle_in_radians = math.acos(sp)
                                    # Get angle in degrees
                                    angle_in_degrees = math.degrees(angle_in_radians)

                                    # Detect hyper-extension with direction bone1 and normal bone2
                                    if dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                                        angle_in_degrees = -angle_in_degrees

                                    # Store actual value of angle
                                    Hands_Angle[h][finger.type()][j][Value] = angle_in_degrees

                            # For others joints
                            else:

                                # Determinate each length in triangle
                                length_a = bone1.length
                                length_b = bone2.length
                                length_c = bone2.next_joint.distance_to(bone1.prev_joint)

                                # Apply cos law
                                sp = (length_c*length_c-length_b*length_b-length_a*length_a)/(2*length_a*length_b)

                                # Verify if scalar product is valid, i.e. it between -1 and 1
                                if (sp <= 1) and (sp >= -1):

                                    # Get angle (in radians) between the 2 unit vectors
                                    angle_in_radians = math.acos(sp)
                                    # Get angle in degrees
                                    angle_in_degrees = math.degrees(angle_in_radians)

                                    # Detect hyper-extension with direction bone1 and normal bone2
                                    if dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                                        angle_in_degrees = 0.00001

                                    # Store actual value of angle
                                    Hands_Angle[h][finger.type()][j][Value] = angle_in_degrees

#=======================================================================================================================

#== FUNCTION: acquisition_angle; calculate angle each time =============================================================

def acquisition_angle():

    # Create controller
    controller = Leap.Controller()

    # Create a sample listener
    listener = SampleListener()

    # Have the sample listener receive events from the controller
    controller = Leap.Controller(listener)

#=======================================================================================================================

#== FUNCTION THREAD #1 : kill_handler ; exit program at any time when user press enter =================================

def kill_handler():

    # Read input (key on the keyboard)
    sys.stdin.read(1)

    # Exit the program if the user press
    os.system('cls' if os.name == 'nt' else 'clear')
    os.kill(os.getpid(), signal.SIGINT)

#=======================================================================================================================

#== FUNCTION THREAD #2 : consumer_display ; implement display as a consumer in multi-threading==========================

def consumer_display():

    # Infinite loop
    while True:

        # Take angles calculated which is in queue
        Angles = data_queue.get()

        # Apply priority of multi-threading
        with lock:

            # Display angles calculated
            display(Angles)

#=======================================================================================================================

#== FUNCTION THREAD #3 : producer_acquisition_angle ; implement acquisition_angle as a producer in multi-threading =====

def producer_acquisition_angle():

    # Infinite loop
    while True:

        # Apply priority of multi-threading
        with lock:

            # Acquire angles calculated
            acquisition_angle()

            # Put angles calculated in a queue
            data_queue.put(Hands_Angle)

#=======================================================================================================================

#== FUNCTION THREAD #4 : consumer_save ; implement save as a consumer in multi-threading================================

def consumer_save():

    # Infinite loop
    while True:

        # Take angles calculated which is in queue
        Angles = data_queue.get()

        # Apply priority of multi-threading
        with lock:

            # Save angles calculated
            save(Angles)

#=======================================================================================================================

#== FUNCTION MULTI THREADING : multi_threading ; implement multi-threading as producer-consumer pattern ================

# Define data queue for angles calculated each time
data_queue = Queue.Queue()

# Define priority of each thread of multi-threading
lock = threading.Lock()

def multi_threading():

    #--------------------------------------------------------
    # THREAD #1 : Check if user press enter for quit program
    #--------------------------------------------------------
    kill_thread = threading.Thread(target=kill_handler)         # Define thread for kill_handler
    kill_thread.daemon = True                                   # Daemon mode (kill thread automatically at program end)
    kill_thread.start()                                         # Start this thread  in first position

    #--------------------------------------------------------
    # THREAD #3 : Acquire angles calculated with Leap Motion
    #--------------------------------------------------------
    p = threading.Thread(target=producer_acquisition_angle)     # Define thread for producer_acquisition_angle
    p.daemon = True                                             # Daemon mode (kill thread automatically at program end)
    p.start()                                                   # Start this thread in third position

    #--------------------------------------------------------
    # THREAD #4 : Save angles calculated in file .csv
    #--------------------------------------------------------
    cc = threading.Thread(target=consumer_save)                 # Define thread for consumer_save
    cc.daemon = True                                            # Daemon mode (kill thread automatically at program end)
    cc.start()                                                  # Start this thread in fourth position

    #--------------------------------------------------------
    # THREAD #2 : Display angles calculated with acquisition
    #--------------------------------------------------------
    c = threading.Thread(target=consumer_display)               # Define thread for consumer_display
    c.daemon = True                                             # Daemon mode (kill thread automatically at program end)
    c.start()                                                   # Start this thread in second position

    #--------------------------------------------------------
    # Wait for the producers threads to finish
    #--------------------------------------------------------
    p.join()

    #--------------------------------------------------------
    # wait till all the jobs are done in the queue
    #--------------------------------------------------------
    data_queue.join()

#=======================================================================================================================

#== FUNCTION: main; executes program ===================================================================================

def main():

    # Display only template of hands without angles
    display_template()

    # Apply multi-threading for acquisition, display angles calculated and save results
    multi_threading()

#== START PROGRAM ======================================================================================================

if __name__ == "__main__":

    #-------------------------------------------------------------------------------------------------------------------
    # Global variables
    #-------------------------------------------------------------------------------------------------------------------

    # Index of data, joints, fingers and hands
    Min, Value, Max = 0, 1, 2                                   # Define type of data
    MP, IPP, IPD = 0, 1, 2                                      # Define type of each joint
    Thumb, Index, Middle, Ring, Pinky = 0, 1, 2, 3, 4           # Define type of each finger
    Left, Right = 0, 1                                          # Define type of each hand

    # List of finger extrema, joints, fingers and hands
    Hands_Angle = [[[[180, 0, -180], [180, 0, -180]],                 # [Min, Value, Max]--> [MP][IPP] --> [Thumb]
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],    # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Index]
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],    # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Middle]
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],    # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Ring]
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]]],   # [Min, Value, Max]--> [[MP][IPP][IPD]] --> [Pinky]
                   [[[180, 0, -180], [180, 0, -180]],                 # Same for right hand
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],    # Same for right hand
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],    # Same for right hand
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]],    # Same for right hand
                    [[180, 0, -180], [180, 0, -180], [180, 0, -180]]]]   # Same for right hand


    # Initialisation of results printing as global variable
    results = [[[['   ', '~|~', '   '], ['   ', '~|~', '   ']],
               [['   ', '~|~', '   '], ['   ', '~|~', '   '], ['   ', '~|~', '   ']],
               [['   ', '~|~', '   '], ['   ', '~|~', '   '], ['   ', '~|~', '   ']],
               [['   ', '~|~', '   '], ['   ', '~|~', '   '], ['   ', '~|~', '   ']],
               [['   ', '~|~', '   '], ['   ', '~|~', '   '], ['   ', '~|~', '   ']]],
              [[['   ', '~|~', '   '], ['   ', '~|~', '   ']],
               [['   ', '~|~', '   '], ['   ', '~|~', '   '], ['   ', '~|~', '   ']],
               [['   ', '~|~', '   '], ['   ', '~|~', '   '], ['   ', '~|~', '   ']],
               [['   ', '~|~', '   '], ['   ', '~|~', '   '], ['   ', '~|~', '   ']],
               [['   ', '~|~', '   '], ['   ', '~|~', '   '], ['   ', '~|~', '   ']]]]

    # Initialisation of results saving as global variable
    results_to_save = [[[['-', '-', '-'], ['-', '-', '-']],
                       [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']],
                       [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']],
                       [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']],
                       [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]],
                      [[['-', '-', '-'], ['-', '-', '-']],
                       [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']],
                       [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']],
                       [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']],
                       [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]]]

    # Define patient data
    Patient_First_Name = "Model 3D"
    Patient_Name = "Hand"
    Patient_Age = "2 ans"
    Session_Number = 1
    Report_Number = str(datetime.datetime.fromtimestamp(time.time())).split(' ')[0].replace('-','') +'_'+ (str(datetime.datetime.fromtimestamp(time.time())).split(' ')[1][:8]).replace(':','')

    # Initialize markers
    data_ok = False

    #-------------------------------------------------------------------------------------------------------------------
    # Stocking user choices
    #-------------------------------------------------------------------------------------------------------------------

    User_Choices =  [[Left, Right],                         # List of hand selected by user
                    [[Thumb, [MP, IPP]],                    # Finger joints : [finger 1,[list of joints selected]]
                    [Index, [MP, IPP, IPD]],                # Finger joints : [finger 2,[list of joints selected]]
                    [Middle, [MP, IPP, IPD]],               # Finger joints : [finger 3,[list of joints selected]]
                    [Ring, [MP, IPP, IPD]],                 # Finger joints : [finger 4,[list of joints selected]]
                    [Pinky, [MP, IPP, IPD]]]]               # Finger joints : [finger 5,[list of joints selected]]

    # Call main function
    main()

#=======================================================================================================================