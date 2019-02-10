from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
import math
from selection import *

class Cursor(QObject):
	changed = QtCore.pyqtSignal()
	selectionChanged  = QtCore.pyqtSignal(object)

	def __init__(self, parent, address=0, nibble=0):
		super(Cursor, self).__init__()
		self.parent = parent
		self._selection = Selection(0,None,active=False, color=self.parent.palette().color(QPalette.HighlightedText))
		self._address = int(address)
		self._nibble = nibble
		self.blink = False
		

# 		self.bpl = bpl

	def updateCursor(self):
		self.blink = not self.blink
		self.parent.viewport().update(self.parent.cursorRectHex())
		
	def startCursor(self,interval=500):
		# cursor blinking timer
		self.cursorTimer = QTimer()
		self.cursorBlinkInterval = interval
		self.cursorTimer.timeout.connect(self.updateCursor)
		self.cursorTimer.setInterval(interval)
		self.cursorTimer.start()
						
	def getSelection(self):
		self._selection.color =self.parent.palette().color(QPalette.Highlight)
		return self._selection
		
	def setSelection(self,selection):
		self._selection = selection
		self._selection.active = True
		self.selectionChanged.emit(selection)		

	def clearSelect(self):
		self.setSelection(Selection(self._address))		
		
# 	@property
	def getAddress(self, address=None):
		if address != None:
			self._address = int(address)
		return self._address

# 	@address.setter
	def setAddress(self, value):
		self._address = int(value)
		self._nibble = 0
		self.changed.emit()

# 	@property
	def getNibble(self):
		return self._nibble

# 	@nibble.setter
	def setNibble(self, value):
		self._nibble = value
		self.changed.emit()

	def update(self, other_cursor):
		changed = False
		if not self._address == other_cursor.getAddress():
			self._address = other_cursor.getAddress()
			changed = True
		if not self._nibble == other_cursor.getNibble():
			self._nibble = other_cursor.getNibble()
			changed = True
		if changed:
			self.changed.emit()

	def right(self):
		self._nibble += 1
		if (self._nibble) > 1:
			self._address += 1				
			self._nibble = 0
		self.changed.emit()	
			
	def left(self):
		self._nibble -= 1
		if (self._nibble) < 0:
				if self._address > 0:
					self._address -= 1				
					self._nibble = 1
				else:
					self._nibble = 0
		self.changed.emit()
	
	def rewind(self, amount):
		self._address -= amount
		if self._address < 0:
			self._address = 0
		self.changed.emit()	


	def forward(self, amount):
		if amount:
			self._address +=  int(amount)
		self.changed.emit()
