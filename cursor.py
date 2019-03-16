from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
# import math
from selection import *

class Cursor(QObject):
	changed = QtCore.pyqtSignal(object)
	selectionChanged  = QtCore.pyqtSignal(object)

	def __init__(self, parent, address=0, nibble=0):
		super(Cursor, self).__init__()
		self.parent = parent
		self._selection = Selection(0,None,active=False)
		self._selection.selectionChanged.connect(self.selectionChanged.emit)
		self._nibble = nibble
		
	def selectNone(self):
		self._selection.start = self._selection.end
		
	def getPosition(self):
		return  self._selection.end # this is the one place i think this is ok becaus eof the ways ranges work

	def getRange(self):
		return self._selection.getRange()

	def __len__(self):
		return len(self._selection)
		
	def getSelection(self):
		(r,g,b,a) = self.parent.palette().color(QPalette.Highlight).getRgb()
		self._selection.color = (r << 16) | (g << 8) | b
		return self._selection
		
	def setCursorPosition(self, pos):
		self._selection.start =  pos
		self._selection.end =  pos
		self.changed.emit(self)		
			
	def startActiveSelection(self,selection):
		self._selection.start = int(selection.start)
		self._selection.end = self._selection.start
		self.changed.emit(self)		
	
	def endSelection(self,selection):
		if selection.start is not None:
			self._selection.start = selection.start
		self._selection.end = int(selection.end)
		self.changed.emit(self)		

	def updateSelection(self,selection):
		if selection.start:
			self._selection.start = selection.start
		self._selection.end = selection.end
		self.changed.emit(self)		
		
	def setSelection(self,selection):
		self._selection = selection
		self._selection.active = True
		self.changed.emit(self)		

# 	@property
# 	def getAddress(self):
# 		return self._selection.start
# 
# 	@address.setter
# 	def setAddress(self, value):
# 		self.updateSelection(Selection(int(value),None))
# 		self._nibble = 0
# 		self.changed.emit(self)

# 	@property
	def getNibble(self):
		return self._nibble

# 	@nibble.setter
	def setNibble(self, value):
		self._nibble = value
		self.changed.emit(self)

	def update(self, other_cursor):
		self.changed.emit(self)


	def right(self, shift=False, update=True):
		self._nibble += 1
		if (self._nibble) > 1:
			self._selection.end += 1
			self._nibble = 0
		if not shift:
			self._selection.start = self._selection.end
			
		if update:
			self.changed.emit(self)	

			
	def left(self, shift=False, update=True):
		self._nibble -= 1
		
		if (self._nibble) < 0:
			self._selection.end -= 1
			if self._selection.start < 0:
				 self._selection.start = 0
			if self._selection.end < 0:
				 self._selection.start = 0
			self._nibble = 1
			
		if not shift:
			self._selection.start = self._selection.end
		if update:
			self.changed.emit(self)	
	
	def rewind(self, amount, shift=False):
		for i in range(int(amount)):
			self.left(shift,False)						
			self.left(shift,False)						
		self.changed.emit(self)
		
	def forward(self, amount,shift = False):
		for i in range(int(amount)):
			self.right(shift,False)						
			self.right(shift,False)						
		self.changed.emit(self)
