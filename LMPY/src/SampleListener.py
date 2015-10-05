#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../lib")
import Leap
import math
import Utilities

[Min, Value, Max] = [0, 1, 2]

class SampleListener(Leap.Listener):

    # Liest des extremas, joints, doigts et mains, Voir guiLeapMotion ligne
    # 1542 pour plus d'infos
    def getHands(self):
        return self.hands_angle

    # Code exécuté pour chaque capture
    def on_frame(self, controller):
        self.hands_angle = [[[[180, 0, -180], [180, 0, -180]], [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                             [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                             [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                             [[180, 0, -180], [180, 0, -180], [180, 0, -180]]],
                            [[[180, 0, -180], [180, 0, -180]],
                             [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                             [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                             [[180, 0, -180], [180, 0, -180], [180, 0, -180]],
                             [[180, 0, -180], [180, 0, -180], [180, 0, -180]]]]
        frame = controller.frame()
        for hand in frame.hands:
            # h=0 main gauche, h=1 main droite
            h = 0 if hand.is_left else 1

            for finger in hand.fingers:

                # Pouce
                if finger.type == 0:
                    # Os
                    for b in range(2, 4):
                        # Jointure
                        j = b - 2

                        bone1 = finger.bone(b - 1)
                        bone2 = finger.bone(b)

                        # MP
                        if b == 2:
                            # Vecteurs unitaires
                            v0 = bone1.basis.y_basis
                            v1 = bone2.basis.y_basis
                            # Produit scalaire
                            sp = Utilities.dot_product(v0, v1)

                            # Vérification si le produit est valide (-1 1)
                            if(sp <= 1) and (sp >= -1) and (v0 != v1):
                                # Calcul de l'angle en radian (avec vecteurs
                                # unitaires)
                                angle_in_radians = math.acos(sp)
                                # Conversion en degrés
                                angle_in_degrees = math.degrees(
                                    angle_in_radians)

                                # HYPER-EXTENSION????
                                if Utilities.dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                                    angle_in_degrees = - angle_in_degrees

                                # Minimum et maximum
                                if self.hands_angle[h][finger.type][j][Max] < angle_in_degrees:
                                    self.hands_angle[h][finger.type][j][
                                        Max] = angle_in_degrees

                                if self.hands_angle[h][finger.type][j][Min] > angle_in_degrees:
                                    self.hands_angle[h][finger.type][j][
                                        Min] = angle_in_degrees

                                self.hands_angle[h][finger.type][j][
                                    Value] = angle_in_degrees

                        # Autres jointure
                        else:
                            # Longueurs dans le triangle
                            length_a = bone1.length
                            length_b = bone2.length
                            length_c = bone2.next_joint.distance_to(
                                bone1.prev_joint)

                            # Loi des cosinus
                            sp = (length_c * length_c - length_b * length_b -
                                  length_a * length_a) / (2 * length_a * length_b)

                            # Vérification si le produit est valide (-1 1)
                            if (sp <= 1) and (sp >= -1):

                                # Calcul de l'angle en radian (avec vecteurs
                                # unitaires)
                                angle_in_radians = math.acos(sp)
                                # Conversion en degrés
                                angle_in_degrees = math.degrees(
                                    angle_in_radians)

                                # HYPER-EXTENSION??
                                if Utilities.dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                                    angle_in_degrees = -angle_in_degrees

                                # Maximum et minimum
                                if self.hands_angle[h][finger.type][j][Max] < angle_in_degrees:
                                    self.hands_angle[h][finger.type][j][
                                        Max] = angle_in_degrees

                                if self.hands_angle[h][finger.type][j][Min] > angle_in_degrees:
                                    self.hands_angle[h][finger.type][j][
                                        Min] = angle_in_degrees

                                self.hands_angle[h][finger.type][j][
                                    Value] = angle_in_degrees

                # PAS un pouce
                else:

                    for b in range(1, 4):
                        j = b - 1
                        bone1 = finger.bone(b - 1)
                        bone2 = finger.bone(b)

                        # MP
                        if b == 1:

                            v0 = bone1.basis.y_basis
                            v1 = bone2.basis.y_basis
                            sp = Utilities.dot_product(v0, v1)

                        if (sp <= 1) and (sp >= -1) and (v0 != v1):
                            angle_in_radians = math.acos(sp)
                            angle_in_degrees = math.degrees(angle_in_radians)

                            if Utilities.dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                                angle_in_degrees = -angle_in_degrees

                            if self.hands_angle[h][finger.type][j][Max] < angle_in_degrees:
                                self.hands_angle[h][finger.type][j][
                                    Max] = angle_in_degrees

                            if self.hands_angle[h][finger.type][j][Min] > angle_in_degrees:
                                self.hands_angle[h][finger.type][j][
                                    Min] = angle_in_degrees

                            self.hands_angle[h][finger.type][j][
                                Value] = angle_in_degrees

                    # Autres jointures
                    else:
                        length_a = bone1.length
                        length_b = bone2.length
                        length_c = bone2.next_joint.distance_to(
                            bone1.prev_joint)
                        sp = (length_c * length_c - length_b * length_b -
                              length_a * length_a) / (2 * length_a * length_b)

                        angle_in_radians = math.acos(sp)
                        angle_in_degrees = math.degrees(angle_in_radians)

                        if Utilities.dot_product(bone1.direction, -bone2.basis.y_basis) < 0:
                            angle_in_degrees = -angle_in_degrees

                        if self.hands_angle[h][finger.type][j][Max] < angle_in_degrees:
                            self.hands_angle[h][finger.type][
                                j][Max] = angle_in_degrees

                        if self.hands_angle[h][finger.type][j][Min] > angle_in_degrees:
                            self.hands_angle[h][finger.type][
                                j][Min] = angle_in_degrees

                        self.hands_angle[h][finger.type][j][
                            Value] = angle_in_degrees
        self.sub.emitData(self.hands_angle)
