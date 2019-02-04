import mmap
import os
import collections
from math import *
import time

from cursor import *
from selection import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore


class HexWidget(QAbstractScrollArea):
	selectionChanged = QtCore.pyqtSignal()
	def __init__(self, parent=None, filename="besthex.py", size=1024):
		super(HexWidget, self).__init__(parent)
		if filename:
			self.filename = filename
			self.data = mmap.mmap(-1, os.stat(self.filename).st_size)
			self.data[:] = open(self.filename, 'rb').read()
		else:
			self.data = mmap.mmap(-1, size)
			self.filename = "<buffer>"
		self.setFont(QFont("Courier", 10))
		self.charWidth = self.fontMetrics().width("2")
		self.charHeight = self.fontMetrics().height()
		self.magic_font_offset = 4

		self.viewport().setCursor(Qt.IBeamCursor)
		# constants
		self.addr_width = 8
		self.bpl = 8
		self.addr_start = 1
		self.gap2 = 2
		self.gap3 = 2
		self.data_width = self.maxWidth()
		self.data_start = self.addr_start + self.addr_width + self.gap2
		self.code_start = self.data_start + self.data_width + self.gap3

		self.pos = 0
		self.blink = False

		self.selection = Selection(active=False, color=self.palette().color(QPalette.Highlight))

		self.highlights = []
		self._cursor = Cursor(32,1)

		self.cursor.changed.connect(self.cursorMove)
		# cursor blinking timer
		self.cursorTimer = QTimer()
		self.cursorTimer.timeout.connect(self.updateCursor)
		self.cursorTimer.setInterval(500)
		self.cursorTimer.start()
		#self.setMinimumWidth((self.code_start + self.bpl + 5) * self.charWidth)
		#self.setMaximumWidth((self.code_start + self.bpl + 5) * self.charWidth)
		self.adjust()

	@property
	def cursor(self):
		return self._cursor

	@cursor.setter
	def cursor(self, value):
		self._cursor.update(value)

	def getLine(self, pos=0):
		return (pos, self.bpl, self.data[pos:pos+self.bpl])

	def toAscii(self, string):
		return  "".join([chr(x) if x >= 33 and x <= 126 else "." for x in string])

	def getLines(self, pos=0):
		while pos < len(self.data)-self.bpl:
			yield (pos, self.bpl, self.toAscii(self.data[pos:pos+self.bpl]))
			pos += self.bpl
		yield (pos, len(self.data)-pos, self.toAscii([self.data[pos:]]))
	#		yield (pos, len(self.data)-pos, "")

	def getBytes(self, count=1):
		return self.data[self.cursor.address:self.cursor.address+count]

	def maxWidth(self):
		return self.bpl * 3 - 1

	def numLines(self):
		return int(ceil(float(len(self.data))/ self.bpl))


	def cursorRect(self):
		return self.cursorToHexRect(self.cursor)

	def cursorRect2(self):
		return self.cursorToAsciiRect(self.cursor)

	def updateCursor(self):
		self.blink = not self.blink
		self.viewport().update(self.cursorRect())


	def visibleColumns(self):
		ret = int(ceil(float(self.viewport().width())/self.charWidth))
		return ret

	def visibleLines(self):
		return int(ceil(float(self.viewport().height())/self.charHeight))

	def totalCharsPerLine(self):
		ret = self.bpl * 4 + self.addr_width + self.addr_start + self.gap2 + self.gap3
		return ret

	def adjust(self):
		self.horizontalScrollBar().setRange(0, self.totalCharsPerLine() - self.visibleColumns() + 1)
		self.horizontalScrollBar().setPageStep(self.visibleColumns())
		self.verticalScrollBar().setRange(0, self.numLines() - self.visibleLines() + 1)
		self.verticalScrollBar().setPageStep(self.visibleLines())

	def goto(self, address):
		self.cursor.nibble = 0
		self.cursor.address = address

	# =====================  Coordinate Juggling  ============================

	def pxToCharCoords(self, px, py):
		cx = int(px / self.charWidth)
		cy = int((py-self.magic_font_offset) / self.charHeight)
		return (cx, cy)

	def charToPxCoords(self, cx, cy):
		"return upper left corder of the rectangle containing the char at position cx, cy"
		px = cx * self.charWidth
		py = cy * self.charHeight + self.magic_font_offset
		return QPoint(px, py)

	def pxCoordToCursor(self, coord):
		column, row = self.pxToCharCoords(coord.x()+self.charWidth/2, coord.y())
		if column >= self.data_start and column < self.code_start:
			rel_column = column-self.data_start
			line_index = rel_column - (rel_column / 3)
			addr = self.pos + line_index/2 + row * self.bpl
			return Cursor(addr, 1 if rel_column % 3 == 1 else 0)

	def indexToHexCharCoords(self, index):
		rel_index = index - self.pos
		cy = rel_index / self.bpl
		line_index = rel_index % self.bpl
		rel_column = line_index * 3
		cx = rel_column + self.data_start
		return (cx, cy)

	def indexToAsciiCharCoords(self, index):
		rel_index = index - self.pos
		cy = rel_index / self.bpl
		line_index = rel_index % self.bpl
		cx = line_index + self.code_start
		return (cx, cy)

	def cursorToHexRect(self, cur):
		hex_cx, hex_cy = self.indexToHexCharCoords(cur.address)
		hex_cx += cur.nibble
		hex_point = self.charToPxCoords(hex_cx, hex_cy)
		hex_rect = QRect(hex_point, QSize(
						   2, self.charHeight))
		return hex_rect


	def cursorToAsciiRect(self, cur):
		ascii_cx, ascii_cy = self.indexToAsciiCharCoords(cur.address)
		ascii_point = self.charToPxCoords(ascii_cx-1, ascii_cy)
		ascii_rect = QRect(ascii_point, QSize(
						   2, self.charHeight))
		return ascii_rect

	def charAtCursor(self, cursor):
		code_char = self.data[cursor.address]
		hexcode = "{:02x}".format(ord(code_char))
		hex_char = hexcode[cursor.nibble]
		return (hex_char, code_char)

	# ====================  Event Handling  ==============================
	def cursorMove(self):
		x, y = self.indexToAsciiCharCoords(self.cursor.address)
		if y > self.visibleLines() - 4:
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() + y - self.visibleLines() + 4)
		if y < 4:
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() + y - 4)


	def mousePressEvent(self, event):
		cur = self.pxCoordToCursor(event.pos())
		if cur is not None:
			if self.selection.active:
				self.selection.active = False
				self.selection.start = self.selection.end = cur.address
				self.viewport().update()
			self.blink = False
			self.viewport().update(self.cursorRect())
			self.cursor = cur


	def mouseMoveEvent(self, event):
		self.selection.start = self.cursor.address
		new_cursor = self.pxCoordToCursor(event.pos())
		if new_cursor is None:
			return
		self.selection.end = new_cursor.address
		self.selection.active = True
		self.viewport().update()
		self.selectionChanged.emit()

	def mouseReleaseEvent(self, event):
		cur = self.pxCoordToCursor(event.pos())
		if cur is not None:
			self.cursor = cur
			self.viewport().update(self.cursorRect())



	def resizeEvent(self, event):
		self.adjust()


	def paintHighlight(self, painter, line, selection):
		if self.selection.active:
			cx_start_hex, cy_start_hex = self.indexToHexCharCoords(self.selection.start)
			cx_end_hex, cy_end_hex = self.indexToHexCharCoords(self.selection.end)
			cx_start_ascii, cy_start_ascii = self.indexToAsciiCharCoords(self.selection.start)
			cx_end_ascii, cy_end_ascii = self.indexToAsciiCharCoords(self.selection.end)
			if line == cy_start_hex:
				topleft_hex = QPoint(self.charToPxCoords(cx_start_hex, line))
				topleft_ascii = QPoint(self.charToPxCoords(cx_start_ascii, line))
				if line == cy_end_hex: # single line selection
					bottomright_hex = QPoint(self.charToPxCoords(cx_end_hex, line))
					bottomright_ascii = QPoint(self.charToPxCoords(cx_end_ascii, line))
				else:
					bottomright_hex = QPoint(self.charToPxCoords(self.code_start - self.gap2, line))
					bottomright_ascii = QPoint(self.charToPxCoords(self.code_start + self.bpl, line))
				bottomright_hex += QPoint(0, self.charHeight)
				bottomright_ascii += QPoint(0, self.charHeight)
				painter.fillRect(QRect(topleft_hex, bottomright_hex), selection.color)
				painter.fillRect(QRect(topleft_ascii, bottomright_ascii), selection.color)
			elif line > cy_start_hex and line <= cy_end_hex:
				topleft_hex = QPoint(self.charToPxCoords(self.data_start, line))
				topleft_ascii = QPoint(self.charToPxCoords(self.code_start, line))
				if line == cy_end_hex:
					bottomright_hex = QPoint(self.charToPxCoords(cx_end_hex, line))
					bottomright_ascii = QPoint(self.charToPxCoords(cx_end_ascii, line))
				else:
					bottomright_hex = QPoint(self.charToPxCoords(self.code_start - self.gap2, line))
					bottomright_ascii = QPoint(self.charToPxCoords(self.code_start + self.bpl, line))
				bottomright_hex += QPoint(0, self.charHeight)
				bottomright_ascii += QPoint(0, self.charHeight)
				painter.fillRect(QRect(topleft_hex, bottomright_hex), selection.color)
				painter.fillRect(QRect(topleft_ascii, bottomright_ascii), selection.color)


	def paintHex(self, painter, row, column):
		addr = self.pos + row * self.bpl + column
		topleft = self.charToPxCoords(column*3 + self.data_start, row)
		bottomleft = topleft + QPoint(0, self.charHeight-self.magic_font_offset)
		byte = "{:02x}".format(ord(chr(self.data[addr])))
		size = QSize(self.charWidth*3, self.charHeight)
		rect = QRect(topleft, size)

		for sel in [self.selection] + self.highlights:
			if sel.active and sel.contains(addr):
				painter.fillRect(rect, sel.color)
				painter.setPen(self.palette().color(QPalette.HighlightedText))
				painter.drawText(bottomleft, byte)
				painter.setPen(self.palette().color(QPalette.WindowText))
				break
		else:
			if row % 2 == 0:
				painter.fillRect(rect, self.palette().color(QPalette.AlternateBase))
			painter.setPen(self.palette().color(QPalette.WindowText))
			painter.drawText(bottomleft, byte)


	def paintAscii(self, painter, row, column):
		addr = self.pos + row * self.bpl + column
		topleft = self.charToPxCoords(column + self.code_start, row)
		bottomleft = topleft + QPoint(0, self.charHeight-self.magic_font_offset)
		byte = self.toAscii(bytearray([self.data[addr]]))
		size = QSize(self.charWidth, self.charHeight)
		rect = QRect(topleft, size)

		for sel in [self.selection] + self.highlights:
			if sel.active and sel.contains(addr):
				painter.fillRect(rect, sel.color)
				painter.setPen(self.palette().color(QPalette.HighlightedText))
				painter.drawText(bottomleft, byte )
				painter.setPen(self.palette().color(QPalette.WindowText))
				break
		else:
			if row % 2 == 0:
				painter.fillRect(rect, self.palette().color(QPalette.AlternateBase))
			painter.setPen(self.palette().color(QPalette.WindowText))
			painter.drawText(bottomleft, byte )



	def paintEvent(self, event):
		start = time.time()
		painter = QPainter(self.viewport())
		palette = self.viewport().palette()

		rect = self.cursorRect()
		rect.setRight(self.cursorRect2().right())

		#painter.fillRect(event.rect(), Qt.green)
		if event.rect() == self.cursorRect():
			if self.blink:
				painter.fillRect(self.cursorRect(), Qt.black)
			self.viewport().update(self.cursorRect2())

			return

		if event.rect() == self.cursorRect2():
			if self.blink:
				painter.fillRect(self.cursorRect2(), Qt.black)
			return



		charh = self.charHeight
		charw = self.charWidth
		charw3 = 3*charw
		data_width = self.data_width
		addr_width = self.addr_width
		addr_start = self.addr_start
		gap2 = self.gap2
		gap3 = self.gap3

		data_start = addr_start + addr_width + gap2
		code_start = data_start + data_width + gap3

		hs = self.horizontalScrollBar().value()
		addr_start -= hs
		code_start -= hs
		data_start -= hs

		# self.addr_start = addr_start
		# self.code_start = code_start
		# self.data_start = data_start

		addr_start *= charw
		data_start *= charw
		code_start *= charw

		self.pos = self.verticalScrollBar().value() * self.bpl

		for i, line in enumerate(self.getLines(self.pos)):
			if i > self.visibleLines():
				break

			if i % 2 == 0:
				painter.fillRect(0, (i)*charh+self.magic_font_offset,
								 self.viewport().width(), charh,
								 self.palette().color(QPalette.AlternateBase))
			(address, length, ascii) = line

			data = self.data[address:address+length]


			# selection highlight
			self.paintHighlight(painter, i, self.selection)
			for h in self.highlights:
				self.paintHighlight(painter, i, h)

			# address
			painter.drawText(addr_start, (i+1)*charh, "{:08x}".format(address))

			# hex data
			for j, byte in enumerate(data):
				self.paintHex(painter, i, j)
				self.paintAscii(painter, i, j)
				#painter.drawText(data_start + j*charw3, (i+1)*charh, "{:02x}".format(ord(byte)))

			# ascii data
			#for j, char in enumerate(data):
			#painter.drawText(code_start, (i+1)*charh, ascii)
		painter.setPen(Qt.gray)
		painter.drawLine(data_start-charw, 0, data_start-charw, self.height())
		painter.drawLine(code_start-charw, 0, code_start-charw, self.height())

		if self.blink and self.cursorRect().top() < self.height() and self.cursorRect().bottom() > 0:
			painter.fillRect(self.cursorRect(), Qt.black)
			painter.fillRect(self.cursorRect2(), Qt.black)
		duration = time.time()-start
		if duration > 0.02:
			print ("painting took: ", duration, 's')

	def keyPressEvent(self, event):
		key = event.key()
		mod = event.modifiers()
		text = event.text()
		hexalpha = "0123456789abcdef"
		if key == Qt.Key_Right:
			if mod & Qt.ShiftModifier:
				if not self.selection.active:
					self.selection.start = self.cursor.address
					self.selection.active = True
				self.selection.end = self.cursor.address
			self.cursor.right()
		elif key == Qt.Key_Left:
			self.cursor.left()
		elif key == Qt.Key_Up:
			self.cursor.rewind(self.bpl)
		elif key == Qt.Key_Down:
			self.cursor.forward(self.bpl)
		elif key in [Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt]:
			pass
		elif text in hexalpha:
			oldbyte = self.data[self.cursor.address]
			if self.cursor.nibble == 1:
				byte = (oldbyte & 0xf0) | hexalpha.index(text)
			else:
				byte = (oldbyte & 0x0f) | (hexalpha.index(text) << 4)
			self.data[int(self.cursor.address)] = byte
			self.cursor.right()

		self.viewport().update()
