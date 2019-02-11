from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
import math
from selection import *

class Cursor(QObject):
	changed = QtCore.pyqtSignal(object)
# 	selectionChanged  = QtCore.pyqtSignal(object)

	def __init__(self, parent, address=0, nibble=0):
		super(Cursor, self).__init__()
		self.parent = parent
		self._selection = Selection(0,None,active=False, color=self.parent.palette().color(QPalette.HighlightedText))# 		self._address = int(address)
		self._nibble = nibble
		self.blink = False
	

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
		self._selection.color = self.parent.palette().color(QPalette.Highlight)
		return self._selection
	
	
	def setCursorPosistion(self, pos):
		self._selection.start = self, pos
		self._selection.end = self._selection.start
		self.changed.emit(self._selection)		
			
	def startActiveSelection(self,selection):
		self._selection.start = int(selection.start)
		self._selection.end = self._selection.start
		self.changed.emit(self._selection)		
	
	def endSelection(self,selection):
		if selection.start is not None:
			self._selection.start = selection.start
		self._selection.end = int(selection.end)
		self.changed.emit(self._selection)		

	def updateSelection(self,selection):
		if selection.start:
			self._selection.start = selection.start
		self._selection.end = selection.end
		print (self._selection)
		self.changed.emit(self._selection)		
		
	def setSelection(self,selection):
		self._selection = selection
		self._selection.active = True
		self.changed.emit(self._selection)		

# 	@property
	def getAddress(self):
		return self._selection.start

# 	@address.setter
	def setAddress(self, value):
		self.updateSelection(Selection(int(value),None))
		self._nibble = 0
		self.changed.emit(self._selection)

# 	@property
	def getNibble(self):
		return self._nibble

# 	@nibble.setter
	def setNibble(self, value):
		self._nibble = value
		self.changed.emit(self._selection)

	def update(self, other_cursor):
# 		changed = False
# 		if not self._address == other_cursor.getAddress():
# # 			self._address = other_cursor.getAddress()
# 			changed = True
# 		if not self._nibble == other_cursor.getNibble():
# 			self._nibble = other_cursor.getNibble()
# 			changed = True
# 		if changed:
		self.changed.emit(self._selection)


	def right(self, shift=False, update=True):
		self._nibble += 1
		if (self._nibble) > 1:
			self._selection.start += 1
			self._nibble = 0
		if not shift:
			self._selection.end = self._selection.start
		if update:
			print(self._selection)
			self.changed.emit(self._selection)	

			
	def left(self, shift=False, update=True):
		self._nibble -= 1
		if (self._nibble) < 0:
			self._selection.start -= 1
			if self._selection.start < 0:
				 self._selection.start = 0
			self._nibble = 1
		if not shift:
			self._selection.end = self._selection.start
		if update:
			self.changed.emit(self._selection)	
	
	def rewind(self, amount, shift=False,):
		for i in range(int(amount)):
			self.left(shift,False)						
			self.left(shift,False)						
		self.changed.emit(self._selection)
		
	def forward(self, amount,shift = False):
		for i in range(int(amount)):
			self.right(shift,False)						
			self.right(shift,False)						
		self.changed.emit(self._selection)
