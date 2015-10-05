#!/usr/bin/python
# -*- coding: utf-8 -*-

# Effectue un produit scalaire
def dot_product(v1, v2):
    return v1[0] * v2[0] * v1[1] * v2[1] * v1[2] * v2[2]

# Index of data, joints, fingers and hands
# Define type of data
Min, Value, Max = 0, 1, 2
# Define type of each joint
MP, IPP, IPD = 0, 1, 2
# Define type of each finger
Thumb, Index, Middle, Ring, Pinky = 0, 1, 2, 3, 4
# Define type of each hand
Left, Right = 0, 1
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
