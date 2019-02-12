from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Selection(QObject):
	def __init__(self, start=0, end=None, active=True, color=Qt.green):
		super(Selection, self).__init__()
		self._start = int(start)
		if end is not None:
			self._end = int(end)
		else:
			self._end = self._start
		self.active = active
		self.color = color

	def __repr__(self):	
		return ("Selection(%s,%s)" % (self._start, self._end))

	def __len__(self):
		if  (self._end == None) or  (self._start == None):
			return 0		
		else:
			return abs(self._end - self._start)

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
		if int(value) > 0:
			self._start = int(value)
		else:
			self._start = 0;
			
		if self._end is None:
			self._end = self._start

	@property
	def end(self):
		return self._end
							
	@end.setter
	def end(self, value):				
		if value is not None:
			if self._start is  None:
				self._start =  int(value) 
				self._end =  int(value) 
			else:
				if int(value) > 0:
					self._end = int(value)
				else:
					self._end = 0;
	# 			self._end =  int(value) 
		else:
			self._end = self._start
		
	