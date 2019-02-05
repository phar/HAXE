import mmap
import os
from math import *
import time
import string
from cursor import *
from selection import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui 

COLOR_PALETTE = [
        "#FFFF00", "#1CE6FF", "#FF34FF", "#FF4A46", "#008941", "#006FA6", "#A30059",
        "#FFDBE5", "#7A4900", "#0000A6", "#63FFAC", "#B79762", "#004D43", "#8FB0FF", "#997D87",
        "#5A0007", "#809693", "#FEFFE6", "#1B4400", "#4FC601", "#3B5DFF", "#4A3B53", "#FF2F80",
        "#61615A", "#BA0900", "#6B7900", "#00C2A0", "#FFAA92", "#FF90C9", "#B903AA", "#D16100",
        "#DDEFFF", "#000035", "#7B4F4B", "#A1C299", "#300018", "#0AA6D8", "#013349", "#00846F",
        "#372101", "#FFB500", "#C2FFED", "#A079BF", "#CC0744", "#C0B9B2", "#C2FF99", "#001E09",
        "#00489C", "#6F0062", "#0CBD66", "#EEC3FF", "#456D75", "#B77B68", "#7A87A1", "#788D66",
        "#885578", "#FAD09F", "#FF8A9A", "#D157A0", "#BEC459", "#456648", "#0086ED", "#886F4C",
        
        "#34362D", "#B4A8BD", "#00A6AA", "#452C2C", "#636375", "#A3C8C9", "#FF913F", "#938A81",
        "#575329", "#00FECF", "#B05B6F", "#8CD0FF", "#3B9700", "#04F757", "#C8A1A1", "#1E6E00",
        "#7900D7", "#A77500", "#6367A9", "#A05837", "#6B002C", "#772600", "#D790FF", "#9B9700",
        "#549E79", "#FFF69F", "#201625", "#72418F", "#BC23FF", "#99ADC0", "#3A2465", "#922329",
        "#5B4534", "#FDE8DC", "#404E55", "#0089A3", "#CB7E98", "#A4E804", "#324E72", "#6A3A4C",
        "#83AB58", "#001C1E", "#D1F7CE", "#004B28", "#C8D0F6", "#A3A489", "#806C66", "#222800",
        "#BF5650", "#E83000", "#66796D", "#DA007C", "#FF1A59", "#8ADBB4", "#1E0200", "#5B4E51",
        "#C895C5", "#320033", "#FF6832", "#66E1D3", "#CFCDAC", "#D0AC94", "#7ED379", "#012C58",
        
        "#7A7BFF", "#D68E01", "#353339", "#78AFA1", "#FEB2C6", "#75797C", "#837393", "#943A4D",
        "#B5F4FF", "#D2DCD5", "#9556BD", "#6A714A", "#001325", "#02525F", "#0AA3F7", "#E98176",
        "#DBD5DD", "#5EBCD1", "#3D4F44", "#7E6405", "#02684E", "#962B75", "#8D8546", "#9695C5",
        "#E773CE", "#D86A78", "#3E89BE", "#CA834E", "#518A87", "#5B113C", "#55813B", "#E704C4",
        "#00005F", "#A97399", "#4B8160", "#59738A", "#FF5DA7", "#F7C9BF", "#643127", "#513A01",
        "#6B94AA", "#51A058", "#A45B02", "#1D1702", "#E20027", "#E7AB63", "#4C6001", "#9C6966",
        "#64547B", "#97979E", "#006A66", "#391406", "#F4D749", "#0045D2", "#006C31", "#DDB6D0",
        "#7C6571", "#9FB2A4", "#00D891", "#15A08A", "#BC65E9", "#FFFFFE", "#C6DC99", "#203B3C",

        "#671190", "#6B3A64", "#F5E1FF", "#FFA0F2", "#CCAA35", "#374527", "#8BB400", "#797868",
        "#C6005A", "#3B000A", "#C86240", "#29607C", "#402334", "#7D5A44", "#CCB87C", "#B88183",
        "#AA5199", "#B5D6C3", "#A38469", "#9F94F0", "#A74571", "#B894A6", "#71BB8C", "#00B433",
        "#789EC9", "#6D80BA", "#953F00", "#5EFF03", "#E4FFFC", "#1BE177", "#BCB1E5", "#76912F",
        "#003109", "#0060CD", "#D20096", "#895563", "#29201D", "#5B3213", "#A76F42", "#89412E",
        "#1A3A2A", "#494B5A", "#A88C85", "#F4ABAA", "#A3F3AB", "#00C6C8", "#EA8B66", "#958A9F",
        "#BDC9D2", "#9FA064", "#BE4700", "#658188", "#83A485", "#453C23", "#47675D", "#3A3F00",
        "#061203", "#DFFB71", "#868E7E", "#98D058", "#6C8F7D", "#D7BFC2", "#3C3E6E", "#D83D66",
        
        "#2F5D9B", "#6C5E46", "#D25B88", "#5B656C", "#00B57F", "#545C46", "#866097", "#365D25",
        "#252F99", "#00CCFF", "#674E60", "#FC009C", "#92896B"
    ]


class HexWidget(QAbstractScrollArea):
	selectionChanged = QtCore.pyqtSignal()
	def __init__(self, parent=None, filename=None, size=1024, font="Courier", fontsize=12):
		super(HexWidget, self).__init__(parent)
		if filename != None:
			self.filename = filename
			self.data = mmap.mmap(-1, os.stat(self.filename).st_size)
			self.data[:] = open(self.filename, 'rb').read()
		else:
			self.data = mmap.mmap(-1, size)
			self.filename = "<buffer>"

		self.debug = False		
		self.Modified = False
		self.font = font
		self.fontsize = fontsize
		self.setFont(QFont(self.font, self.fontsize))
		self.charWidth = self.fontMetrics().width("2")
		self.charHeight = self.fontMetrics().height()
		self.magic_font_offset = 4

		
		self.viewport().setCursor(Qt.IBeamCursor)

		self.addressformat = "{:08x}"
		self.hexcharformat = "{:02x} "
		# constants... NOT IF I HAVE ANYTHING TO SAY ABOUT IT

		self.bpl = 16
		
		self.gap2 = 2
		self.gap3 = 1
		self.gap4 = 3

		self.pos = 0
		self.blink = False

		
		self.ActiveView = 'hex'
		self.selection = Selection(active=False, color=self.palette().color(QPalette.Highlight))
		self.highlights = []
		self._cursor = Cursor(32,1)

		
		self.cursor.changed.connect(self.cursorMove)
		
		# cursor blinking timer
		self.cursorTimer = QTimer()
		self.cursorTimer.timeout.connect(self.updateCursor)
		self.cursorTimer.setInterval(500)
		self.cursorTimer.start()
		self.adjust()
	
	def contextMenuEvent(self, event):
		menu = QMenu(self)
		quitAction = menu.addAction("Testing")
		action = menu.exec_(self.mapToGlobal(event.pos()))
		if action == quitAction:
			qApp.quit()


	def addr_start(self):
		return 1

	def data_start(self):
		return self.addr_start() + self.getAddressFormatLen() + self.gap2
	
	def code_start(self):
		return self.data_start() + self.getDataLength() + self.gap3

	@property
	def cursor(self):
		return self._cursor

	@cursor.setter
	def cursor(self, value):
		self._cursor.update(value)

	def getLine(self, pos=0):
		return (pos, self.bpl, self.data[pos:pos+self.bpl])

	def toAscii(self, strin):
		return  "".join([chr(x) if chr(x) in string.printable else "." for x in strin])

	def getLines(self, pos=0):
		while pos < len(self.data)-self.bpl:
			yield (pos, self.bpl, self.toAscii(self.data[pos:pos+self.bpl]))
			pos += self.bpl
		yield (pos, len(self.data)-pos, self.toAscii(self.data[pos:]))

	def getBytes(self, count=1):
		return self.data[self.cursor.address:self.cursor.address+count]

	def numLines(self):
		return ceil(float(len(self.data))/ self.bpl)

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
		return  self.getAddressFormatLen()  + self.gap2 + self.getDataLength() + self.gap3 + self.getCodeLength() + self.gap4

	def adjust(self):
		self.horizontalScrollBar().setRange(0, self.totalCharsPerLine() - self.visibleColumns() + 1)
		self.horizontalScrollBar().setPageStep(self.visibleColumns())
		self.verticalScrollBar().setRange(0, self.numLines() - self.visibleLines() + 1)
		self.verticalScrollBar().setPageStep(self.visibleLines())

	def sizeHint(self):
		return QtCore.QSize(self.totalCharsPerLine() * self.charWidth, 25 * self.charHeight)

#		self.resize(QSize(self.totalCharsPerLine() * self.charWidth,  self.visibleLines() * self.charHeight))
	
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
		if column >= self.data_start() and column < self.code_start():
			rel_column = column-self.data_start()
			line_index = rel_column - (rel_column / 3)
			addr = self.pos + line_index/2 + row * self.bpl
			return Cursor(addr, 1 if rel_column % 3 == 1 else 0)

	def indexToHexCharCoords(self, index):
		rel_index = index - self.pos
		cy = floor(rel_index / self.bpl)
		line_index = rel_index % self.bpl
		rel_column = line_index * self.getHexCharFormatLen()
		cx = rel_column + self.data_start()
		return (cx, cy)

	def indexToAsciiCharCoords(self, index):
		rel_index = index - self.pos
		cy = floor(rel_index / self.bpl)
		line_index = rel_index % self.bpl
		cx = line_index + self.code_start()
		return (cx, cy)

	def cursorToHexRect(self, cur):
		hex_cx, hex_cy = self.indexToHexCharCoords(cur.address)
		hex_cx += cur.nibble
		hex_point = self.charToPxCoords(hex_cx, hex_cy)
		hex_rect = QRect(hex_point, QSize( 2, self.charHeight))
		return hex_rect


	def cursorToAsciiRect(self, cur):
		ascii_cx, ascii_cy = self.indexToAsciiCharCoords(cur.address)
		ascii_point = self.charToPxCoords(ascii_cx-1, ascii_cy)
		ascii_rect = QRect(ascii_point, QSize(2, self.charHeight))
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
		
		if((event.pos().x()/self.charWidth) < (self.getAddressFormatLen() + self.gap2)):
		   self.ActiveView = 'addr'
		elif ((self.getAddressFormatLen() + self.gap2 + self.getDataLength())  > (event.pos().x()/self.charWidth) > (self.getAddressFormatLen() + self.gap2)):
		   self.ActiveView = 'hex'
		else:
		   self.ActiveView = 'ascii'
	
		cur = self.pxCoordToCursor(event.pos())
		if cur is not None:
			if self.selection.active:
				self.selection.active = False
				self.selection.start = self.selection.end = cur.address
				self.viewport().update()
			self.blink = False
			self.viewport().update(self.cursorRect())
			self.cursor = cur
			self.selectionChanged.emit()

# 		print(self.ActiveView,event.pos().x())


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



	def widthToBPL(self, width):
#		if(self.totalCharsPerLine() / self.charWidth)
#		if ((width/self.charWidth)/self.totalCharsPerLine()):
#			self.bpl =
# 		print((width / self.charWidth) - self.totalCharsPerLine())#(self.getAddressFormatLen() + self.getDataLength(self.bpl) + self.gap2 + self.gap3  + self.gap4 + self.getDataLength(self.bpl)))
		pass
	
	def resizeEvent(self, event):
		self.widthToBPL(event.size().width())
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
					bottomright_hex = QPoint(self.charToPxCoords(self.code_start() - self.gap2, line))
					bottomright_ascii = QPoint(self.charToPxCoords(self.code_start() + self.bpl, line))
				bottomright_hex += QPoint(0, self.charHeight)
				bottomright_ascii += QPoint(0, self.charHeight)
				painter.fillRect(QRect(topleft_hex, bottomright_hex), selection.color)
				painter.fillRect(QRect(topleft_ascii, bottomright_ascii), selection.color)
			elif line > cy_start_hex and line <= cy_end_hex:
				topleft_hex = QPoint(self.charToPxCoords(self.data_start(), line))
				topleft_ascii = QPoint(self.charToPxCoords(self.code_start(), line))
				if line == cy_end_hex:
					bottomright_hex = QPoint(self.charToPxCoords(cx_end_hex, line))
					bottomright_ascii = QPoint(self.charToPxCoords(cx_end_ascii, line))
				else:
					bottomright_hex = QPoint(self.charToPxCoords(self.code_start() - self.gap2, line))
					bottomright_ascii = QPoint(self.charToPxCoords(self.code_start() + self.bpl, line))
				bottomright_hex += QPoint(0, self.charHeight)
				bottomright_ascii += QPoint(0, self.charHeight)
				painter.fillRect(QRect(topleft_hex, bottomright_hex), selection.color)
				painter.fillRect(QRect(topleft_ascii, bottomright_ascii), selection.color)

	def getHexCharFormat(self):
		return self.hexcharformat
	
	def getHexCharFormatLen(self):
		return len(self.getHexCharFormat().format(0))

	
	def clearHilights(self):
		self.highlights = []
		
	def addHilight(self,start,end=1):
		self.highlights.append(Selection(start,end,True, QColor(COLOR_PALETTE[len(self.highlights)])))

	
	def paintHex(self, painter, row, column):
		addr = self.pos + row * self.bpl + column
		topleft = self.charToPxCoords(column*self.getHexCharFormatLen() + self.data_start(), row)
		bottomleft = topleft + QPoint(0, self.charHeight-self.magic_font_offset)
		byte = self.getHexCharFormat().format(self.data[addr])
		size = QSize(self.charWidth*self.getHexCharFormatLen(), self.charHeight)
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
		topleft = self.charToPxCoords(column + self.code_start(), row)
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
		data_width = self.getDataLength()
		addr_width = self.getAddressFormatLen()
		addr_start = self.addr_start()
		gap2 = self.gap2
		gap3 = self.gap3

		data_start = addr_start + addr_width + gap2
		code_start = data_start + data_width + gap3

		hs = self.horizontalScrollBar().value()
		addr_start -= hs
		code_start -= hs
		data_start -= hs

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
			painter.drawText(addr_start, (i+1)*charh, self.getAddressFormat().format(address))

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
		if duration > 0.02 and self.debug == 1:
			print ("painting took: ", duration, 's')

	def getAddressFormat(self):
		return self.addressformat

	def getAddressWidth(self):
		return self.getAddressFormatLen() * self.charWidth
	
	def getDataLength(self, bpl=None):
		return (self.getCodeLength(bpl) * 3.0)
	
	def getCodeLength(self,bpl=None):
		if bpl == None:
			return self.bpl
		else:
			return bpl
	
	def getAddressFormatLen(self):
		return len(self.getAddressFormat().format(0))

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

		if event.matches(QKeySequence.Copy):
			print('Ctrl + C')
		elif event.matches(QKeySequence.Paste):
			print('Ctrl + V')

		self.viewport().update()
