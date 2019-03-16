from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui 

class SelectionActionClasss(QObject):
	updated =  QtCore.pyqtSignal()

	def __init__(self,pluginparent, name=None):
		super(SelectionActionClasss, self).__init__(None)
		self.name = name
		self.selections = []
		self.pluginparent = pluginparent

	def labelAction(self,hexobj, selection):
		return ".".join([self.name, selection.getLabel()])
	
	def selectAction(self,hexobj,  selection):
		print("click!")
		pass

	def editAction(self,hexobj, selection):
		print("dblckick!")
		pass
		
	def dragAction(self,hexobj, selection,dragdistance):
		print("drag!")
		pass
		
	def addSelection(self, hexobj , selection):
		self.selections.append(selection)
		hexobj.addSelection(selection) #fixme


class Selection(QObject):
	selectionChanged = QtCore.pyqtSignal(object)
	def __init__(self, start=0, end=None, active=True, label=None, color=Qt.green, obj=None):
		super(Selection, self).__init__()
		self._start = int(start)
		if end is not None:
			self._end = int(end)
		else:
			self._end = self._start
		self.active = active
		self.obj = obj
		self.color = color
		self.label = label
		
	def setLabel(self,label):
		self.label = label
		
	def getLabel(self):
		return self.label
		
	def __repr__(self):	
		return ("Selection(%s,%s)" % (self._start, self._end))

	def __len__(self):
		if  (self._end == None) or  (self._start == None):
			return 0		
		else:
			return abs(self._end - self._start)

	def __iter__(self):
		return iter(range(min(self._start, self._end), max(self._start, self._end)))

	def __add__(self,arg):
		if self._start + int(arg) > 0:
			self._start += int(arg)
			self._end += int(arg)
		else:
			self._end = len(self)
			self._start = 0
		
		
		self.selectionChanged.emit(self.getRange())		
		return self
		
	def __sub__(self,arg):
		self._start += int(arg)
		self._end += int(arg)
		self.selectionChanged.emit(self.getRange())
		return self
		
	def getRange(self):
		return (min(self._start, self._end), max(self._start, self._end))
		
	def contains(self, address):
		if self._start != None and self._end != None:			
			(st,ed) = self.getRange()
			return int(address) in range(st,ed)
		else:
			return 0
				
	@property
	def start(self):
		return self._start
				
	@start.setter
	def start(self, value):
# 		if int(value) > 0:
# 			if  self._start != int(value):
		self._start = int(value)
		self.selectionChanged.emit(self.getRange())
# 		else:
# 			self._start = 0;
# 			self.selectionChanged.emit(self.getRange())
# 			
# 		if self._end is None:
# 			self._end = self._start
# 			self.selectionChanged.emit(self.getRange())

	@property
	def end(self):
		return self._end
							
	@end.setter
	def end(self, value):				
# 		if value is not None:
# 			if self._start is  None:
# 				self._start =  int(value) 
		self._end =  int(value) 
		self.selectionChanged.emit(self.getRange())
# 			else:
# 				if int(value) > 0:
# 					if self._end != int(value):					
# 						self._end = int(value)
# 						self.selectionChanged.emit(self.getRange())
# 				else:
# 					self._end = 0;
# 	# 			self._end =  int(value) 
# 		else:
# 			if  self._end != self._start:
# 				self._end = self._start
# 				self.selectionChanged.emit(self.getRange())
# 		
	