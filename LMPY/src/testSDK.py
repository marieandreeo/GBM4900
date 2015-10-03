#!/usr/bin/python
# -*- coding: utf-8 -*-



# import du package système. Permet d'accéder au système de fichier 
import sys
# Permet de voir ce qu'il y a dans le dossier lib
sys.path.insert(0, "../lib")
# Importe la librairie Leap du dossier lib
import Leap

import os, inspect, thread, time

class SampleListener(Leap.Listener):
	def on_connect(self, controller):
		print "Connected"

	def on_frame(self, controller):
		frame = controller.frame()

		print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
			frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))


def main():
	
	# Create a sample listener and controller
	listener = SampleListener()
	controller = Leap.Controller()

	# Have the sample listener receive events from the controller
	controller.add_listener(listener)

	# Keep this process running until Enter is pressed
	print "Press Enter to quit..."
	try:
		sys.stdin.readline()
	except KeyboardInterrupt:
		pass
	finally:
        # Remove the sample listener when done
       	 controller.remove_listener(listener)

# Exécute le main
if __name__ == "__main__":
    main()




