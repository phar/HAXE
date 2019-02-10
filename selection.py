from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Selection(QObject):
	def __init__(self, start=None, end=None, active=True, color=Qt.green):
		super(Selection, self).__init__()
		if end == None:
			end = start

		if start <=  end :
			self._start = int(start)
			self._end = int(end)
		else:
			self._start = int(end)
			self._end = int(start)
		
		self.active = active
		self.color = color

	def __repr__(self):	
		return ("Selection(%s,%s)" % (self._start, self._end))

	def __len__(self):
		if  (self._end == None) or  (self._start == None):
			return 0		
		else:
			return self._end - self._start

	def getRange(self):
		return (self._start, self._end)
		
	def contains(self, address):
		return int(address) in range(self._start,  self._end)

	# enforce that start <= end
	@property
	def start(self):
		return self._start

	@start.setter
	def start(self, value):
		if not self.active:
			self._start = self._end = int(value)
			return
		self._start = min(value, self.end)
		self._end = max(value, self.end)

	@property
	def end(self):
		return self._end

	@end.setter
	def end(self, value):
		if not self.active:
			self._start = self._end = int(value)
			return
		self._end = max(value, self.start)
		self._start = min(value, self.start)
