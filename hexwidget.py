import os
import time
from math import *
import string
from cursor import *
from selection import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui 
from filebuffer import FileBuffer
import traceback



COLOR_PALETTE = [ #high contrast color mapping
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


def hilo(r,g,b):
	b = ((r * 299.0) + (g * 587.0) + (b * 114.0)) / 1000.0
	if b < 128:
		return  (255,255,255)
	else:
		return tuple(int(QColor(QPalette.WindowText).name()[i:i+2], 16) for i in (1, 3 ,5))

def hexColorComplement(cstr):
        (r,g,b) = tuple(int(cstr[i:i+2], 16) for i in (1, 3 ,5))
        return "#" + "".join(["%02x" % x for x in hilo(r,g,b)])




class HexWidget(QAbstractScrollArea):
	selectionChanged = QtCore.pyqtSignal(object)
	focusEvent = QtCore.pyqtSignal(object)
	copyEvent = QtCore.pyqtSignal(object)
	cutEvent = QtCore.pyqtSignal(object)
	pasteEvent = QtCore.pyqtSignal(object)
	findEvent = QtCore.pyqtSignal(object)
	editEvent = QtCore.pyqtSignal(object)	
	deleteEvent = QtCore.pyqtSignal(object)
	undoEvent = QtCore.pyqtSignal(object)	
	redoEvent = QtCore.pyqtSignal(object)
	selectAllEvent = QtCore.pyqtSignal(object)
	updateSelectionListEvent =  QtCore.pyqtSignal(object)
	ctxtMenuEvent =  QtCore.pyqtSignal(object)
	jumpToEvent =  QtCore.pyqtSignal(object)
		
	def __init__(self,api, parent=None, fileobj=None, font="Courier", fontsize=12):
		super(HexWidget, self).__init__(parent)
		self.api = api
		self.debug = False		
		self.filebuff = fileobj	
		self.parent = parent
		self.cursorBlinkInterval = None
		self.cursorTimer = None
		self.fontsize = None
		self.font = None
		self.charWidth = 0
		self.charHeight = 0
		self.fontsize = fontsize
		self.addressformat = "{:08x}"
		self.hexcharformat = "{:02x} "
		self.activeview = 'hex'
		self.charset = "ascii"
		self.highlights = []
		self.dragactive = 0
		# constants... NOT IF I HAVE ANYTHING TO SAY ABOUT IT
		self.bpl = 16
		self.gap2 = 2
		self.gap3 = 1
		self.gap4 = 3
		self.pos = 0
		self.magic_font_offset = 2
		self.colorBars = True
		
		self.setWidgetFont(font,fontsize)
		self.cursor = Cursor(self, 0,0)
		
		self.cursor.changed.connect(self.selectionChanged.emit)
		self.cursor.changed.connect(self.cursorMove)		
		self.horizontalScrollBar().setEnabled(False);
		self.setMouseTracking(True)  
		self.adjust()


	def getCursor(self):
		return self.cursor
		
	def getSelection(self):
		return self.cursor.getSelection()
		
	def setWidgetFont(self,font="Courier",size=12):
		self.font = font
		self.fontsize = size
		self.setFont(QFont(self.font, self.fontsize))
		
		self.charWidth = self.fontMetrics().width("2")
		self.charHeight = self.fontMetrics().height()

	def toggleAddressFormat(self):
		if 	self.addressformat == "{:08d}":
			self.addressformat = "{:08x}"
		else:
			self.addressformat = "{:08d}"		

	def toggleActiveView(self):
		if 	self.activeview == "hex":
			self.activeview = "ascii"
		else:
			self.activeview = "hex"		
			
	def getSelection(self):
		return self.cursor.getSelection()

	def contextMenuEvent(self, event):
		self.ctxtMenuEvent.emit(event)
		

	def addr_start(self):
		return 1

	def hex_start(self):
		return self.addr_start() + self.getAddressFormatLen() + self.gap2
	
	def ascii_start(self):
		return self.hex_start() + self.getHexLength() + self.gap3

	def getLine(self, pos=0):
		return (pos, self.bpl, self.filebuff[pos:pos+self.bpl])

	def toAscii(self, strin):
# 		return  "".join([chr(x) if chr(x) in string.printable else "." for x in strin])
		return  "".join([chr(x) if chr(x) in string.printable else "." for x in strin])
# 		return strin.decode("")
	
	
	def getLines(self, pos=0):
# 		while pos <  self.visibleLines():#len(self.filebuff)-self.bpl:
		while pos < len(self.filebuff)-self.bpl:
			yield (pos, self.bpl, self.toAscii(self.filebuff[pos:pos+self.bpl]))
			pos += self.bpl
		yield (pos, len(self.filebuff)-pos, self.toAscii(self.filebuff[pos:]))

	def numLines(self):
		return ceil(float(len(self.filebuff))/ self.bpl)

	def cursorRectHex(self):
		return self.cursorToHexRect(self.cursor)

	def cursorRectAscii(self):
		return self.cursorToAsciiRect(self.cursor)

	def visibleColumns(self):
		ret = int(ceil(float(self.viewport().width())/self.charWidth))
		return ret

	def visibleLines(self):
		return int(ceil(float(self.viewport().height())/self.charHeight))

	def totalCharsPerLine(self):
		return  self.getAddressFormatLen()  + self.gap2 + self.getHexLength() + self.gap3 + self.bpl + self.gap4

	def adjust(self):
		self.horizontalScrollBar().setRange(0, self.totalCharsPerLine() - self.visibleColumns() + 1)
		self.horizontalScrollBar().setPageStep(self.visibleColumns())
		self.verticalScrollBar().setRange(0, self.numLines() - self.visibleLines() + 1)
		self.verticalScrollBar().setPageStep(self.visibleLines())

	def sizeHint(self):
		return QtCore.QSize((self.totalCharsPerLine() * self.charWidth), (25 * self.charHeight))


	def goto(self, address):
		self.cursor.setAddress(address)
	# =====================  Coordinate Juggling  ============================


	def pxToCharCoords(self, px, py):
		cx = px / self.charWidth
		cy = (py-self.magic_font_offset) / self.charHeight
		return (cx, cy)


	def charToPxCoords(self, cx, cy):
		"return upper left corder of the rectangle containing the char at position cx, cy"
		px = cx * self.charWidth
		py = cy * self.charHeight + (self.magic_font_offset)
		return QPoint(px, py)

	def pxCoordToAddr(self, coord):
		column, row = self.pxToCharCoords(coord.x(), coord.y())
		nib = (column - int(column)) > .6
		column,row = floor(column), floor(row)
		if column >= self.hex_start() and column < self.ascii_start():
			rel_column = (column-self.hex_start() / 2.0)
			line_index = rel_column - (rel_column / self.getHexCharFormatLen())
			addr = self.pos + (line_index / 2.0) + (row * self.bpl) - 1
			
			return  (nib,addr)
		elif column >=  self.ascii_start():
			rel_column = column-self.ascii_start() 
			addr = self.pos + rel_column + row * self.bpl
			return (0,addr)
		else:
			return (None,None)
	def indexToHexCharCoords(self, index):
		rel_index = index - self.pos
		cy = int(rel_index / self.bpl) 
		line_index = rel_index % self.bpl
		rel_column = line_index * self.getHexCharFormatLen()
		cx = rel_column + self.hex_start()
		return (cx, cy)

	def indexToAsciiCharCoords(self, index):
		rel_index = index - self.pos
		cy = int(rel_index / self.bpl)
		line_index = rel_index % self.bpl
		cx = line_index + self.ascii_start()
		return (cx, cy)

	def cursorToHexRect(self, cur):
		hex_cx, hex_cy = self.indexToHexCharCoords(cur._selection.end)
		hex_cx += cur.getNibble()
		hex_point = self.charToPxCoords(hex_cx, hex_cy)
		coffset = QPoint(0, self.charHeight-2)
		hex_rect = QRect(hex_point+coffset, QSize(self.charWidth, 2))
		return hex_rect


	def cursorToAsciiRect(self, cur):
		ascii_cx, ascii_cy = self.indexToAsciiCharCoords(cur._selection.end)
		ascii_point = self.charToPxCoords(ascii_cx, ascii_cy)
		coffset = QPoint(0, self.charHeight-2)
		ascii_rect = QRect(ascii_point+coffset, QSize(self.charWidth,2))
		return ascii_rect

	def charAtCursor(self, cursor):
		ascii_char = self.filebuff[cursor.getAddress()]
		hexcode = self.hexcharformat.strip().format(ord(ascii_char))
		hex_char = hexcode[cursor.getNibble()]
		return (hex_char, ascii_char)

	# ====================  Event Handling  ==============================


	def mousePressEvent(self, event):
		if((event.pos().x()/self.charWidth) < (self.getAddressFormatLen() + self.gap2)):
			self.activeview = 'addr'
			self.toggleAddressFormat()
			self.viewport().update()
		elif ((self.getAddressFormatLen() + self.gap2 + self.getHexLength())  > (event.pos().x()/self.charWidth) > (self.getAddressFormatLen() + self.gap2)):
			self.activeview = 'hex'
		else:
			self.activeview = 'ascii'
	
		(nib, cur) = self.pxCoordToAddr(event.pos())	
		if cur is not None and event.buttons() == Qt.LeftButton:
			self.dragactive  = True
			self.cursor.startActiveSelection(Selection(cur,cur))
			self.cursor.setNibble(nib)	
			self.viewport().update()
			for s in self.pxToSelectionList(event.pos()):
				s.obj.selectAction()
	
	
	def mouseDoubleClickEvent(self,event):
		for s in self.pxToSelectionList(event.pos()):
			s.obj.editAction()

		
	def pxToSelectionList(self, pos):
		"""bytes may be involved in more then one selection, this returns a list of those selections"""
		selections = []
		for sel in self.highlights:
			(nib, cur) = self.pxCoordToAddr(pos)
			if sel.contains(cur):
				selections.append(sel)
		return selections
		
	def hover(self,pos):
		for s in self.pxToSelectionList(pos):
			if s.obj != None:
				QToolTip.hideText()
				QToolTip.showText(self.mapToGlobal(pos),  s.obj.labelAction(), self)
						
	def mouseMoveEvent(self, event):	
		(nib,cur) = self.pxCoordToAddr(event.pos())
		if cur is not None and self.dragactive == True:
			self.cursor.updateSelection(Selection(self.cursor._selection.start, cur))		
			self.viewport().update()
		if cur: 
			self.hover(event.pos())

	def mouseReleaseEvent(self, event):
		self.dragactive = False

	def focusInEvent(self, event):
		self.focusEvent.emit(self.cursor.getSelection())
	
	def resizeEvent(self, event):

		a = self.getAddressFormatLen()  + self.gap2 + self.getHexLength() + self.gap3 + self.bpl + self.gap4
		b = (self.viewport().width() / self.charWidth) -  ( self.getAddressFormatLen()  + self.gap2 +  self.gap3 +  self.gap4)
		c = b - (self.bpl + (self.bpl * self.getHexCharFormatLen()))
		if self.viewport().width() <  (b  - (1 + (1 * self.getHexCharFormatLen()))):
			self.bpl = 1
		else:
			snap = 0
			minlval = 0
			widths = []
			for i in range(1,64):
				l = ( self.viewport().width() /self.charWidth ) - (( self.getAddressFormatLen()  + self.gap2 +  self.gap3 +  self.gap4) + (i + (i * self.getHexCharFormatLen())))
				widths.append(l)				
	
			self.bpl = widths.index(min(widths, key=abs)) + 1
		self.adjust()

	def getHexCharFormat(self):
		return self.hexcharformat
	
	def getHexCharFormatLen(self):
		return len(self.getHexCharFormat().format(0))

	def clearHilights(self):
		self.highlights = []
		
	def getNextColor(self):
		return COLOR_PALETTE[len(self.highlights)]
		
	def addSelection(self,start, end=1, color=None, obj=None):
		if color == None:
			color =  self.getNextColor()
		self.highlights.append(Selection(start,end,True, color,obj))
		self.updateSelectionListEvent.emit(self.highlights)

	def paintByte(self, painter, addr, topleft, byte, selected):
		bottomleft = topleft + QPoint(0, self.charHeight-self.magic_font_offset)
		size = QSize(self.charWidth*self.getHexCharFormatLen(), self.charHeight)
		rect = QRect(topleft, size)

		if selected:
			painter.fillRect(rect,self.palette().color(QPalette.Highlight))
			painter.setPen(self.palette().color(QPalette.HighlightedText))
		else:
			for sel in self.highlights:
				if len(sel) and sel.active and sel.contains(addr):
					painter.fillRect(rect,QColor( sel.color))
					painter.setPen(QColor(hexColorComplement(sel.color)))
					painter.drawText(bottomleft, byte)
					return
					
		painter.setPen(self.palette().color(QPalette.WindowText))
		painter.drawText(bottomleft, byte)
		
		painter.setPen(self.palette().color(QPalette.WindowText))
		painter.drawText(bottomleft, byte )


# 	def paintCursor(self, event,painter, cur, active):
# 		palette = self.viewport().palette()
# 
# 		if event.rect() == cur: 
# 			if self.cursor.blink and self.parent.isActiveWindow:
# 				if active:
# 					painter.fillRect(cur, Qt.black)
# 				else:
# 					painter.fillRect(cur, Qt.gray)
# 			self.viewport().update(cur)
# 			return True
# 		return False
# 
# 		

	def paintEvent(self, event):
		start = time.time()
		painter = QPainter(self.viewport())
		palette = self.viewport().palette()

		rect = self.cursorRectHex()
		rect.setRight(self.cursorRectAscii().right())

		hex_width = self.getHexLength()

		addr_width = self.getAddressFormatLen()
		addr_start = self.addr_start()
		hex_start = addr_start + addr_width + self.gap2
		ascii_start = hex_start + hex_width + self.gap3

		hs = self.horizontalScrollBar().value()
		addr_start -= hs
		ascii_start -= hs
		hex_start -= hs

		addr_start *= self.charWidth
		hex_start *= self.charWidth
		ascii_start *= self.charWidth

		self.pos = self.verticalScrollBar().value() * self.bpl

		for i, line in enumerate(self.getLines(self.pos)):	
			(address, length, ascii) = line
			
			if i > self.visibleLines():
				break

			#background stripes
			if self.colorBars and 1 if (address % (self.bpl * 2)) == self.bpl else 0:
				painter.fillRect(0, (i * self.charHeight)+self.magic_font_offset,(self.totalCharsPerLine() * self.charWidth),  self.charHeight, self.palette().color(QPalette.AlternateBase))
			
			data = self.filebuff[address:address+length]

			# address
			painter.setPen(self.palette().color(QPalette.WindowText))
			painter.drawText(addr_start, (i * self.charHeight)+self.charHeight, self.getAddressFormat().format(address))

			# data
			for j, byte in enumerate(data):
				addr = self.pos + i * self.bpl + j
				dat = self.filebuff[addr]
				selected =   self.cursor.getSelection().contains(addr)
				
				topleft = self.charToPxCoords(j*self.getHexCharFormatLen() + self.hex_start(), i)
				self.paintByte(painter, addr, topleft, self.getHexCharFormat().format(dat),selected)
				
				topleft = self.charToPxCoords(j + self.ascii_start(), i)
				self.paintByte(painter, addr, topleft,  self.toAscii([dat]),selected)
				
			#virt sep bars
			painter.setPen(Qt.gray)
			painter.drawLine(hex_start-self.charWidth, 0, hex_start-self.charWidth, self.height())
			painter.drawLine(ascii_start-self.charWidth, 0, ascii_start-self.charWidth, self.height())								
				
		#cursor
		if (self.parent.blinkstate % 2) == 0:
			if self.activeview == "hex":
				painter.fillRect(self.cursorRectHex(), Qt.black)
				painter.fillRect(self.cursorRectAscii(), Qt.gray)
			else:
				painter.fillRect(self.cursorRectAscii(), Qt.black)
				painter.fillRect(self.cursorRectHex(), Qt.gray)
				
				
		duration = time.time()-start
# 		if duration > 0.02:
# 			print ("painting took: ", duration, 's')

	def getAddressFormat(self):
		return self.addressformat

	def getAddressWidth(self):
		return self.getAddressFormatLen() * self.charWidth
	
	def getHexLength(self, bpl=None):
		return (self.getAsciiLength(bpl) * self.getHexFormatLen())
	
	def getAsciiLength(self,bpl=None):
		if bpl == None:
			return self.bpl
		else:
			return bpl
	
	def getHexFormatLen(self):
		return  len(self.hexcharformat.format(0))
		
	def getAddressFormatLen(self):
		return len(self.getAddressFormat().format(self.cursor.getAddress() + (self.visibleLines() * self.bpl)))

	def cursorMove(self, selection):
		if selection.start > len(self.filebuff):
			self.cursor._selection.start = len(self.filebuff)
			
		if selection.end > len(self.filebuff):
			self.cursor._selection.end = len(self.filebuff)
			
		self.scrollWindowToCursor()

	def scrollWindowToCursor(self):
		x, y = self.indexToAsciiCharCoords(self.cursor.getAddress())
		if y > self.visibleLines() - 2:
			self.verticalScrollBar().setValue(((self.verticalScrollBar().value() + y) - self.visibleLines()) + 2)
		if y < 1:
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() + y)
	
	def event(self, event):
		if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
			self.toggleActiveView()
			self.viewport().update()
			return False
		return super(HexWidget, self).event(event)

        		
	def keyPressEvent(self, event):
		key = event.key()
		mod = event.modifiers()
		text = event.text()

		if event.matches(QKeySequence.Copy):
			self.copyEvent.emit(self.cursor.getSelection())
		elif event.matches(QKeySequence.Cut):
			self.cutEvent.emit(self.cursor.getSelection())
		elif event.matches(QKeySequence.Undo):
			self.undoEvent.emit(self.cursor.getSelection())
		elif event.matches(QKeySequence.Redo):
			self.redoEvent.emit(self.cursor.getSelection())
		elif event.matches(QKeySequence.Delete):
			self.deleteEvent.emit(self.cursor.getSelection())
		elif event.matches(QKeySequence.Paste):
			self.pasteEvent.emit(self.cursor.getSelection())
		elif event.matches(QKeySequence.Delete):
			self.deleteEvent.emit(self.cursor.getSelection())
		elif event.matches(QKeySequence.Find):
			self.findEvent.emit(self.cursor.getSelection())
		elif event.matches(QKeySequence.SelectAll):
			self.cursor.setSelection(Selection(0, len(self.filebuff)))# 
			self.selectAllEvent.emit(self.cursor.getSelection())				
		else:					
			if  ((Qt.ControlModifier | Qt.MetaModifier | Qt.AltModifier	) & mod):
				pass
			else:
				if key == Qt.Key_Right:
					self.cursor.right((mod & Qt.ShiftModifier) )
				elif key == Qt.Key_Left:
					self.cursor.left((mod & Qt.ShiftModifier) )
				elif key == Qt.Key_Up:
					self.cursor.rewind(self.bpl,(mod & Qt.ShiftModifier))
				elif key == Qt.Key_Down:
					self.cursor.forward(self.bpl,(mod & Qt.ShiftModifier))
				elif key in [Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt]:
					pass
				elif key == Qt.Key_Backspace:		
					self.deleteEvent.emit(self.cursor.getSelection())
				elif key == Qt.Key_Down:
					self.cursor.forward(self.hexWidget.bpl)
				elif key == Qt.Key_PageUp:
					self.cursor.rewind((self.visibleLines()-2)*self.bpl,(mod & Qt.ShiftModifier))
				elif key == Qt.Key_PageDown:
					self.cursor.forward((self.visibleLines()-2)*self.bpl,(mod & Qt.ShiftModifier))
				elif key == Qt.Key_Home:
					self.cursor.setCursorPosistion(0)
				elif key == Qt.Key_End:
					self.cursor.setCursorPosistion(len(self.filebuff))
				elif text != '':
					oldbyte = self.filebuff[self.cursor.getAddress()] 
					
					hexalpha = "0123456789abcdefABCDEF"
					if  self.activeview == 'hex':
						if text in hexalpha:
							if self.cursor.getNibble() == 0:
								byte = (oldbyte & 0x0f) | (int(text,16) << 4)
							else:
								byte = (oldbyte & 0xf0) | int(text,16)
								
							if byte != oldbyte:		
								self.editEvent.emit((self.cursor.getSelection(),byte))
							self.cursor.right()
							
						elif ord(text) in b'gG':
							self.jumpToEvent.emit(self.cursor.getSelection())

					elif self.activeview == 'ascii':
						byte = ord(text)
						if byte != oldbyte:		
							self.editEvent.emit((self.cursor.getSelection(),byte))
							
						self.cursor.right()
						self.cursor.right()
						
					elif self.activeview == 'addr':
						if ord(text) in b'gG':
							f  = JumpToDialog(self,self.api)
							f.show()
							
				self.viewport().update()
