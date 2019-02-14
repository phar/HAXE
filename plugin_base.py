from binascii import *
from math import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import string
import importlib
import construct


class HexPlugin():
	def __init__(self,api,name):
		self.api = api
		self.name = name

	def name(self):
		raise "must implement"	

	def start(self):
		raise "must implement"	
		
	def stop(self):
		raise "must implement"	

	def pluginMenuPlacement(self, selection=None):
		return []
		
	def pluginSelectionPlacement(self, selection=None):
		return []
		
	def pluginImporterExporterPlacement(self, selection=None):
		return []
