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
from filebuffer import FileBuffer

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




class HexDialog(QMainWindow):
	undoEvent = QtCore.pyqtSignal(object)
	redoEvent = QtCore.pyqtSignal(object)
	saveEvent = QtCore.pyqtSignal(object)

	def __init__(self, api, parent=None,fileobj=None):
		super(HexDialog, self).__init__(parent)
		self.filebuff = fileobj
		self.api = api
		self.parent = parent
		self.clipboardata = []
	
		self.isActiveWindow = False
		self.hexWidget =  HexWidget(api,self,self.filebuff)
		self.setCentralWidget(self.hexWidget);
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
	
		self.api.activeWindowChanged.connect(self.active_notify)
		self.hexWidget.selectionChanged.connect(self.select_changed)
		self.hexWidget.copyEvent.connect(self.copy)
		self.hexWidget.pasteEvent.connect(self.paste)
		self.hexWidget.editEvent.connect(self.edit)
		self.hexWidget.focusEvent.connect(self.setFocus)
	
		self.selectstatus = QLabel("")
		self.statusBar.addWidget(self.selectstatus)
		self.statusBar.show()
	
# 		self.selection = self.hexWidget.getSelection()
      	
	def getSelection(self):
		return self.hexWidget.getSelection()
      	
	def select_changed(self,selection):
		# self.selection = sel
		print(selection)
		if len(selection):
			self.selectstatus.setText("%d bytes selected at offset 0x%x out of %d bytes" % (selection.end-selection.start, selection.start, len(self.filebuff)))
		else:
			self.selectstatus.setText("offset 0x%x (%d) of %d bytes" % (selection.start,selection.start, len(self.filebuff)))
		self.selectstatus.repaint()

      	
	def setFocus(self):
# 		print ("sdfas",sel)
		self.api.setActiveFocus(self.filebuff.filename)

	def active_notify(self, fn):
		if fn == self.filebuff.filename:
			self.isActiveWindow = True
		else:
			self.isActiveWindow = False
			
		
	def edit(self,tup):
		(selection,edit) = tup
		print (tup)
		self.filebuff.addEdit(selection,edit)
		
	def paste(self,selection):
		print("paste!")
		cb = QApplication.clipboard()
		if cb.ownsClipboard():
			t = self.clipboardata	
		else:
			t = bytearray(cb.text(),'utf-8')
		self.filebuff.addEdit(selection, t)
		self.hexWidget.goto(self.hexWidget.cursor.getAddress())
		self.hexWidget.setSelection(Selection(selection.start, selection.start + len(t)))
	
	def copy(self,slection):
		print("copy!")
		t = self.filebuff[self.hexWidget.selection.start: self.hexWidget.selection.end]			
		self.clipboardata = t
		cb = QApplication.clipboard()
		t = self.api.getCopyModeFn()(t)
		print(t)
		cb.setText(t.decode('ASCII'), mode=cb.Clipboard)

	def keyPressEvent(self, event):
		key = event.key()
		mod = event.modifiers()
		text = event.text()
		print(key)
		if event.matches(QKeySequence.Undo):
			self.undoEvent.emit(self.hexWidget.selection)

		elif event.matches(QKeySequence.Redo):
			self.redoEvent.emit(self.hexWidget.selection)
			
		elif event.matches(QKeySequence.Save):
			self.saveEvent.emit(self.hexWidget.selection)

		else:
			pass

		self.hexWidget.viewport().update()






class HexWidget(QAbstractScrollArea):
	selectionChanged = QtCore.pyqtSignal(object)
	focusEvent = QtCore.pyqtSignal(object)
	copyEvent = QtCore.pyqtSignal(object)
	pasteEvent = QtCore.pyqtSignal(object)
	editEvent = QtCore.pyqtSignal(object)
	
	def __init__(self,api, parent=None, fileobj=None, font="Courier", fontsize=12):
		super(HexWidget, self).__init__(parent)
			
		self.api = api
		self.debug = False		
		self.filebuff = fileobj	
		self.parent = parent
		self.fontsize = fontsize
		self.font = font
		self.fontsize = fontsize
		self.cursor = Cursor(32,1)

		
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

		self.cursor.changed.connect(self.cursorMove)

		self.ActiveView = 'hex'
		self.selection = Selection(0,None,active=False, color=self.palette().color(QPalette.Highlight))
		self.highlights = []
		
		self.adjust()
		
		# cursor blinking timer
		self.cursorTimer = QTimer()
		self.cursorTimer.timeout.connect(self.updateCursor)
		self.cursorTimer.setInterval(500)
		self.cursorTimer.start()
		
	def getSelection(self):
		return self.selection

	def contextMenuEvent(self, event):
		menu = QMenu(self)
		
		mnu = {}
		for n in self.api.getStructList():
			mnu[n] = menu.addAction("Struct %s here" % n, lambda n = n: self.structAtAddress(n,self.cursor.getAddress()))
			
		action = menu.exec_(self.mapToGlobal(event.pos()))
# 		print(action)
# 		print(mnu[action] == action)
# 		if action == quitAction:
# 			qApp.quit()


	def structAtAddress(self,struct,address):
		print("define struct %s @ %08x" % (struct,address))

# 		try:		
# 			parsed = cons.parse(self.filebuffer[self.cursor.address:])
# 		except:
# 			parsed = "<parse error>"
# 					
# 		print(parsed)
# 			print(structs)
					
# 				if isinstance(parsed, construct.Container):
# 					self.items.append(QTreeWidgetItem(self.qtparent.structexplorer, [cons.name,'Container',"none"]))
# 					parent = self.items[-1]
# 					parent.setExpanded(True)
# 					offt =  self.openFiles[self.getActiveFocus()].cursor.address
# 					for i in cons.subcons:
# 						self.openFiles[self.getActiveFocus()].addHilight(offt,offt+i.sizeof()-1)
# 						offt+=i.sizeof()			
		
		pass
	
	def addr_start(self):
		return 1

	def data_start(self):
		return self.addr_start() + self.getAddressFormatLen() + self.gap2
	
	def code_start(self):
		return self.data_start() + self.getDataLength() + self.gap3

	def getLine(self, pos=0):
		return (pos, self.bpl, self.filebuff[pos:pos+self.bpl])

	def toAscii(self, strin):
		return  "".join([chr(x) if chr(x) in string.printable else "." for x in strin])

	def getLines(self, pos=0):
		while pos < len(self.filebuff)-self.bpl:
			yield (pos, self.bpl, self.toAscii(self.filebuff[pos:pos+self.bpl]))
			pos += self.bpl
		yield (pos, len(self.filebuff)-pos, self.toAscii(self.filebuff[pos:]))

# 	def getBytes(self, count=1):
# 		return self.filebuff[self.cursor._address:self.cursor._address+count]

	def numLines(self):
		return ceil(float(len(self.filebuff))/ self.bpl)

	def cursorRectHex(self):
		return self.cursorToHexRect(self.cursor)

	def cursorRectAscii(self):
		return self.cursorToAsciiRect(self.cursor)

	def updateCursor(self):
		self.blink = not self.blink
		self.viewport().update(self.cursorRectHex())

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


	def goto(self, address):
		self.cursor.setAddress(address)
	# =====================  Coordinate Juggling  ============================


	def pxToCharCoords(self, px, py):
		cx = int(px / self.charWidth)
		cy = int((py-self.magic_font_offset) / self.charHeight)
		return (cx, cy)

	def charToPxCoords(self, cx, cy):
		"return upper left corder of the rectangle containing the char at position cx, cy"
		px = cx * self.charWidth
		py = cy * self.charHeight + (self.magic_font_offset)
		return QPoint(px, py)

	def pxCoordToCursor(self, coord):
		column, row = self.pxToCharCoords(coord.x()+self.charWidth/2, coord.y())
		if column >= self.data_start() and column < self.code_start():
			rel_column = column-self.data_start()
			line_index = rel_column - (rel_column / 3)
			addr = self.pos + line_index/2 + row * self.bpl
			return Cursor(addr, 1 if (rel_column % self.getHexCharFormatLen()) == 1 else 0)
		else:
			column, row = self.pxToCharCoords(coord.x()+self.charWidth/2, coord.y()) #fixme
			rel_column = column-(self.code_start() + self.data_start())
			line_index = rel_column - rel_column
			addr = self.pos + line_index/2 + row * self.bpl		
			print(column, row,addr)


	def indexToHexCharCoords(self, index):
		rel_index = index - self.pos
		cy = int(rel_index / self.bpl) 
		line_index = rel_index % self.bpl
		rel_column = line_index * self.getHexCharFormatLen()
		cx = rel_column + self.data_start()
		return (cx, cy)

	def indexToAsciiCharCoords(self, index):
		rel_index = index - self.pos
		cy = int(rel_index / self.bpl)
		line_index = rel_index % self.bpl
		cx = line_index + self.code_start()
		return (cx, cy)

	def cursorToHexRect(self, cur):
		hex_cx, hex_cy = self.indexToHexCharCoords(cur.getAddress())
		hex_cx += cur.getNibble()
		hex_point = self.charToPxCoords(hex_cx, hex_cy)
		hex_rect = QRect(hex_point, QSize( 2, self.charHeight))
		return hex_rect


	def cursorToAsciiRect(self, cur):
		ascii_cx, ascii_cy = self.indexToAsciiCharCoords(cur.getAddress())
		ascii_point = self.charToPxCoords(ascii_cx, ascii_cy)
		ascii_rect = QRect(ascii_point, QSize(2, self.charHeight))
		return ascii_rect

	def charAtCursor(self, cursor):
		code_char = self.filebuff[cursor.getAddress()]
		hexcode = "{:02x}".format(ord(code_char))
		hex_char = hexcode[cursor.getNibble()]
		return (hex_char, code_char)

	# ====================  Event Handling  ==============================


	def mousePressEvent(self, event):
		if((event.pos().x()/self.charWidth) < (self.getAddressFormatLen() + self.gap2)):
		   self.ActiveView = 'addr'
		elif ((self.getAddressFormatLen() + self.gap2 + self.getDataLength())  > (event.pos().x()/self.charWidth) > (self.getAddressFormatLen() + self.gap2)):
		   self.ActiveView = 'hex'
		else:
		   self.ActiveView = 'ascii'
	
		cur = self.pxCoordToCursor(event.pos())
		self.selection.start = self.cursor.getAddress()
		if cur is not None:
			if self.selection.active:
				self.selection.active = False
				self.selection.start = self.selection.end = cur.getAddress()
				self.viewport().update()
			self.blink = False
			self.selectionChanged.emit(Selection(cur.getAddress()))
# 			self.setSelection(Selection(cur.getAddress()))
			self.cursor = cur 			
		self.viewport().update()
			
	def setSelection(self,selection):
		self.selection = selection
		self.selection.active = True
		self.selection.color = self.palette().color(QPalette.Highlight)
		self.selectionChanged.emit(selection)		

	def mouseMoveEvent(self, event):
		self.selection.start = self.cursor.getAddress()
		new_cursor = self.pxCoordToCursor(event.pos())
		if new_cursor is None:
			return
		self.selection.end = new_cursor.getAddress()
		self.selection.active = True
		self.selectionChanged.emit(self.selection)
		self.viewport().update()

	def mouseReleaseEvent(self, event):
		cur = self.pxCoordToCursor(event.pos())
		if cur is not None:
			self.cursor = cur
			self.viewport().update(self.cursorRectHex())

	def focusInEvent(self, event):
		self.focusEvent.emit(self.selection)
	
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
		byte = self.getHexCharFormat().format(self.filebuff[addr])
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
				if (row % 2):
					painter.fillRect(rect, self.palette().color(QPalette.AlternateBase))
				
			painter.setPen(self.palette().color(QPalette.WindowText))
			painter.drawText(bottomleft, byte)
			

	def paintAscii(self, painter, row, column):
		addr = self.pos + row * self.bpl + column
		topleft = self.charToPxCoords(column + self.code_start(), row)
		bottomleft = topleft + QPoint(0, self.charHeight-self.magic_font_offset)
		byte = self.toAscii(bytearray([self.filebuff[addr]]))
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
			if (row % 2):
				painter.fillRect(rect, self.palette().color(QPalette.AlternateBase))
			painter.setPen(self.palette().color(QPalette.WindowText))
			painter.drawText(bottomleft, byte )

	def paintEvent(self, event):
		start = time.time()
		painter = QPainter(self.viewport())
		palette = self.viewport().palette()

		rect = self.cursorRectHex()
		rect.setRight(self.cursorRectAscii().right())

		#painter.fillRect(event.rect(), Qt.green)
		if event.rect() == self.cursorRectHex(): 
			if self.blink and self.parent.isActiveWindow:
				if self.ActiveView == "hex":
					painter.fillRect(self.cursorRectHex(), Qt.black)
				else:
					painter.fillRect(self.cursorRectHex(), Qt.gray)
			self.viewport().update(self.cursorRectAscii())
			return
		elif event.rect() == self.cursorRectAscii():
			if self.blink and self.parent.isActiveWindow :
				if self.ActiveView == "ascii":
					painter.fillRect(self.cursorRectAscii(), Qt.black)
				else:
					painter.fillRect(self.cursorRectAscii(), Qt.gray)
			return

		data_width = self.getDataLength()
		addr_width = self.getAddressFormatLen()
		addr_start = self.addr_start()

		data_start = addr_start + addr_width + self.gap2
		code_start = data_start + data_width + self.gap3

		hs = self.horizontalScrollBar().value()
		addr_start -= hs
		code_start -= hs
		data_start -= hs

		addr_start *= self.charWidth
		data_start *= self.charWidth
		code_start *= self.charWidth

		self.pos = self.verticalScrollBar().value() * self.bpl

		for i, line in enumerate(self.getLines(self.pos)):
			if i > self.visibleLines():
				break

			if (i % 2):
				painter.fillRect(0, (i)* self.charHeight+self.magic_font_offset, self.viewport().width(),  self.charHeight, self.palette().color(QPalette.AlternateBase))
			(address, length, ascii) = line

			data = self.filebuff[address:address+length]

			# selection highlight
			self.paintHighlight(painter, i, self.selection)
			for h in self.highlights:
				self.paintHighlight(painter, i, h)

			# address
			painter.drawText(addr_start, ((i+1)* self.charHeight), self.getAddressFormat().format(address))

			# data
			for j, byte in enumerate(data):
				self.paintHex(painter, i, j)
				self.paintAscii(painter, i, j)

		painter.setPen(Qt.gray)
		painter.drawLine(data_start-self.charWidth, 0, data_start-self.charWidth, self.height())
		painter.drawLine(code_start-self.charWidth, 0, code_start-self.charWidth, self.height())

		if self.blink and self.cursorRectHex().top() < self.height() and self.cursorRectHex().bottom() > 0:
			painter.fillRect(self.cursorRectHex(), Qt.black)
			painter.fillRect(self.cursorRectAscii(), Qt.black)
			
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
	

	def cursorMove(self):
		print(self.cursor.getAddress())
		x, y = self.indexToAsciiCharCoords(self.cursor.getAddress())
		if y > self.visibleLines() - 4:
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() + y - self.visibleLines() + 4)
		if y < 4:
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() + y - 4)
		
	def keyPressEvent(self, event):
		key = event.key()
		mod = event.modifiers()
		text = event.text()
		
		if event.matches(QKeySequence.Copy):
			self.copyEvent.emit(self.selection)
			
		elif event.matches(QKeySequence.Paste):
			self.pasteEvent.emit(self.selection)
			
		elif event.matches(QKeySequence.Copy):
			self.copyEvent.emit(self.selection)
			
		elif event.matches(QKeySequence.Paste):
			self.pasteEvent.emit(self.selection)
		else:				
		
			if key == Qt.Key_Right:
				if mod & Qt.ShiftModifier:
					if not self.selection.active:
						self.selection.start = self.cursor.getAddress()
						self.selection.active = True
					self.selection.end = self.cursor.getAddress()
				self.cursor.right()
			elif key == Qt.Key_Left:
				self.cursor.left()
				print("kjjkllkj")
			elif key == Qt.Key_Up:
				self.cursor.rewind(self.bpl)
			elif key == Qt.Key_Down:
				self.cursor.forward(self.bpl)
			elif key in [Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt]:
				pass

			elif key == Qt.Key_Down:
				self.cursor.forward(self.hexWidget.bpl)
			elif key in [Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt]:
				pass
			elif text != '':
				oldbyte = self.filebuff[self.cursor.getAddress()]
				hexalpha = "0123456789abcdefABCDEF"


				if   text in hexalpha and self.ActiveView == 'hex':
					if self.cursor.getNibble() == 0:
						byte = (oldbyte & 0x0f) | (int(text,16) << 4)
					else:
						byte = (oldbyte & 0xf0) | int(text,16)
					if byte != oldbyte:		
						self.editEvent.emit((Selection(self.cursor.getAddress()),byte))
					self.cursor.right()
				
				elif   self.ActiveView == 'ascii':
					byte = ord(text)
					if byte != oldbyte:		
						self.editEvent.emit((Selection(self.cursor.getAddress()),byte))
					self.cursor.right()
					self.cursor.right()
		self.viewport().update()
