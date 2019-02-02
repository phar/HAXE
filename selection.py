#from PySide.QtCore import *
#from PyQt5 import QtGui,QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Selection(QObject):
    def __init__(self, start=0, end=0, active=True, color=Qt.green):
        self._start = min(start, end)
        self._end = max(start, end)
        self.active = active
        self.color = color

    def __len__(self):
        return self._end - self._start

    def contains(self, address):
        return address >= self._start and address <= self._end

    # enforce that start <= end
    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        if not self.active:
            self._start = self._end = value
            return
        self._start = min(value, self.end)
        self._end = max(value, self.end)

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        if not self.active:
            self._start = self._end = value
            return
        self._end = max(value, self.start)
        self._start = min(value, self.start)
