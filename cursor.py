from PySide.QtCore import *

class Cursor(QObject):
    changed = Signal()

    def __init__(self, address=0, nibble=0):
        super(Cursor, self).__init__()
        self._address = address
        self._nibble = nibble

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value
        self.changed.emit()


    @property
    def nibble(self):
        return self._nibble

    @nibble.setter
    def nibble(self, value):
        self._nibble = value
        self.changed.emit()

    def update(self, other_cursor):
        changed = False
        if not self.address == other_cursor.address:
            self._address = other_cursor.address
            changed = True
        if not self.nibble == other_cursor.nibble:
            self._nibble = other_cursor.nibble
            changed = True
        if changed:
            self.changed.emit()

    def right(self):
        if self.nibble == 0:
            self.nibble = 1
        else:
            self.address +=1
            self.nibble = 0

    def left(self):
        if self.nibble == 1:
            self.nibble = 0
        else:
            self.address -=1
            self.nibble = 1

    def rewind(self, amount):
        self.address -= amount
        if self.address < 0:
            self.address = 0


    def forward(self, amount):
        self.address += amount
