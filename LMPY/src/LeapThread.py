#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from threading import Thread
sys.path.insert(0, "../lib")
import Leap
from SampleListener import *

class LeapThread(Thread):

	def __init__(self, subTread):
		Thread.__init__(self)

		self.listener = SampleListener()
		self.controller = Leap.Controller()
		self.listener.sub = subTread

	def run(self):
		self.controller.add_listener(self.listener)

