#!/usr/local/bin/python
# -*- coding: utf-8 -*- 

class Finger: 

	def _init_(self):
		self.max = 0
		self.value = 0
		self.min = 0

# Classe représentant une main. Elle permet de stocker des valeurs d'angles pour chaque doigt
class Hand:

	def _init_(self):
		# Formaté selon [Min, Value, Max]
		self.thumb = Finger()
		self.index = Finger()
		self.middle = Finger()
		self.ring = Finger()
		self.pinky = Finger()