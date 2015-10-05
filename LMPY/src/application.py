#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import

import sys                          # For using system parameters
import math                         # For calculating angle
import time                         # For extracting time
import datetime                     # For extracting date
import csv                          # For saving data in file
import os                           # For extracting path
import glob                         # For extracting path
import pageUi                       # Import py of Qt Designer
import mainPageUi
from MainPage import *
from LeapThread import *

def main():

	app = QtGui.QApplication(sys.argv)
	mainPage = MainPage()
	mainPage.showMaximized()
	r = app.exec_()
	sys.exit(r)

	print "Press Enter to quit..."
	try:
		sys.stdin.readline()
	except KeyboardInterrupt:
		pass
	finally:
		# thread1.controller.remove_listener(thread1.listener)
		print 'Ended'

# Exécute le main
if __name__ == "__main__":
    main()
