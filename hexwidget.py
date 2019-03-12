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
        0xFFFF00, 0x1CE6FF, 0xFF34FF, 0xFF4A46, 0x008941, 0x006FA6, 0xA30059,
        0xFFDBE5, 0x7A4900, 0x0000A6, 0x63FFAC, 0xB79762, 0x004D43, 0x8FB0FF, 0x997D87,
        0x5A0007, 0x809693, 0xFEFFE6, 0x1B4400, 0x4FC601, 0x3B5DFF, 0x4A3B53, 0xFF2F80,
        0x61615A, 0xBA0900, 0x6B7900, 0x00C2A0, 0xFFAA92, 0xFF90C9, 0xB903AA, 0xD16100,
        0xDDEFFF, 0x000035, 0x7B4F4B, 0xA1C299, 0x300018, 0x0AA6D8, 0x013349, 0x00846F,
        0x372101, 0xFFB500, 0xC2FFED, 0xA079BF, 0xCC0744, 0xC0B9B2, 0xC2FF99, 0x001E09,
        0x00489C, 0x6F0062, 0x0CBD66, 0xEEC3FF, 0x456D75, 0xB77B68, 0x7A87A1, 0x788D66,
        0x885578, 0xFAD09F, 0xFF8A9A, 0xD157A0, 0xBEC459, 0x456648, 0x0086ED, 0x886F4C,
        0x34362D, 0xB4A8BD, 0x00A6AA, 0x452C2C, 0x636375, 0xA3C8C9, 0xFF913F, 0x938A81,
        0x575329, 0x00FECF, 0xB05B6F, 0x8CD0FF, 0x3B9700, 0x04F757, 0xC8A1A1, 0x1E6E00,
        0x7900D7, 0xA77500, 0x6367A9, 0xA05837, 0x6B002C, 0x772600, 0xD790FF, 0x9B9700,
        0x549E79, 0xFFF69F, 0x201625, 0x72418F, 0xBC23FF, 0x99ADC0, 0x3A2465, 0x922329,
        0x5B4534, 0xFDE8DC, 0x404E55, 0x0089A3, 0xCB7E98, 0xA4E804, 0x324E72, 0x6A3A4C,
        0x83AB58, 0x001C1E, 0xD1F7CE, 0x004B28, 0xC8D0F6, 0xA3A489, 0x806C66, 0x222800,
        0xBF5650, 0xE83000, 0x66796D, 0xDA007C, 0xFF1A59, 0x8ADBB4, 0x1E0200, 0x5B4E51,
        0xC895C5, 0x320033, 0xFF6832, 0x66E1D3, 0xCFCDAC, 0xD0AC94, 0x7ED379, 0x012C58,
        0x7A7BFF, 0xD68E01, 0x353339, 0x78AFA1, 0xFEB2C6, 0x75797C, 0x837393, 0x943A4D,
        0xB5F4FF, 0xD2DCD5, 0x9556BD, 0x6A714A, 0x001325, 0x02525F, 0x0AA3F7, 0xE98176,
        0xDBD5DD, 0x5EBCD1, 0x3D4F44, 0x7E6405, 0x02684E, 0x962B75, 0x8D8546, 0x9695C5,
        0xE773CE, 0xD86A78, 0x3E89BE, 0xCA834E, 0x518A87, 0x5B113C, 0x55813B, 0xE704C4,
        0x00005F, 0xA97399, 0x4B8160, 0x59738A, 0xFF5DA7, 0xF7C9BF, 0x643127, 0x513A01,
        0x6B94AA, 0x51A058, 0xA45B02, 0x1D1702, 0xE20027, 0xE7AB63, 0x4C6001, 0x9C6966,
        0x64547B, 0x97979E, 0x006A66, 0x391406, 0xF4D749, 0x0045D2, 0x006C31, 0xDDB6D0,
        0x7C6571, 0x9FB2A4, 0x00D891, 0x15A08A, 0xBC65E9, 0xFFFFFE, 0xC6DC99, 0x203B3C,
        0x671190, 0x6B3A64, 0xF5E1FF, 0xFFA0F2, 0xCCAA35, 0x374527, 0x8BB400, 0x797868,
        0xC6005A, 0x3B000A, 0xC86240, 0x29607C, 0x402334, 0x7D5A44, 0xCCB87C, 0xB88183,
        0xAA5199, 0xB5D6C3, 0xA38469, 0x9F94F0, 0xA74571, 0xB894A6, 0x71BB8C, 0x00B433,
        0x789EC9, 0x6D80BA, 0x953F00, 0x5EFF03, 0xE4FFFC, 0x1BE177, 0xBCB1E5, 0x76912F,
        0x003109, 0x0060CD, 0xD20096, 0x895563, 0x29201D, 0x5B3213, 0xA76F42, 0x89412E,
        0x1A3A2A, 0x494B5A, 0xA88C85, 0xF4ABAA, 0xA3F3AB, 0x00C6C8, 0xEA8B66, 0x958A9F,
        0xBDC9D2, 0x9FA064, 0xBE4700, 0x658188, 0x83A485, 0x453C23, 0x47675D, 0x3A3F00,
        0x061203, 0xDFFB71, 0x868E7E, 0x98D058, 0x6C8F7D, 0xD7BFC2, 0x3C3E6E, 0xD83D66,
        0x2F5D9B, 0x6C5E46, 0xD25B88, 0x5B656C, 0x00B57F, 0x545C46, 0x866097, 0x365D25,
        0x252F99, 0x00CCFF, 0x674E60, 0xFC009C, 0x92896B
    ]


def hilo(r,g,b):
	b = ((r * 299.0) + (g * 587.0) + (b * 114.0)) / 1000.0
	if b < 128:
		return  (255,255,255)
	else:
		return tuple(int(QColor(QPalette.WindowText).name()[i:i+2], 16) for i in (1, 3 ,5))
		
def hexColorComplement(cstr):
	r = (cstr & 0xff0000) >> 16
	g = (cstr & 0x00ff00) >> 8
	b = (cstr & 0x0000ff)
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
	jumpToEvent =  QtCore.pyqtSignal()
		
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
		self.selectactive =  False
		self.dragactive = False
		self.dragstart = None
		self.dragselection = []
		self.widgetpainted = None
		# constants... NOT IF I HAVE ANYTHING TO SAY ABOUT IT
		self.bpl = 16
		self.gap2 = 2
		self.gap3 = 1
		self.gap4 = 3
		self.pos = 0
		self.colorBars = True
		self.charWidthMultiplier = 1.0
		self.charHeightMultiplier = 1.0
		self.paintedevent = 0
		self.lastpanted = 0
		self.knownvisiblelines  = 0
		self.fontpixmap = {'light':{},'dark':{}}
		self.setWidgetFont(font,fontsize)
		self.cursor = Cursor(self, 0,0)
		
		self.cursor.selectionChanged.connect(self.selectionChanged.emit)
		self.cursor.changed.connect(self.cursorMove)		
		self.horizontalScrollBar().setEnabled(False);
		self.setMouseTracking(True)  
		self.adjust()
		self.blinkstate = 0
		self.startCursor(500)
		
		


	def startCursor(self,interval=500):
		# cursor blinking timer
		self.cursorTimer = QTimer()
		self.cursorBlinkInterval = interval
		self.cursorTimer.timeout.connect(self.updateCursor)
		self.cursorTimer.setInterval(interval)
		self.cursorTimer.start()

	def updateCursor(self):
		self.blinkstate += 1
		
		self.repaintWidget()

	def getCursor(self):
		return self.cursor
		
	def getSelection(self):
		return self.cursor.getSelection()
		
	def setWidgetFont(self,font="Courier",size=12):
		self.font = font
		self.fontsize = size
		self.fontpixmap = {}
		
		font = QFont(self.font, self.fontsize)
		
		self.fm = QFontMetrics(font)
		self.charWidth = self.fm.maxWidth() * self.charWidthMultiplier
		self.charHeight = self.fm.height() * self.charHeightMultiplier
		
		self.fontpixmap = {'light':{},'dark':{}}
		for i in string.printable:
			self.fontpixmap['dark'][i] = QPixmap(self.charWidth, self.charHeight)
			self.fontpixmap['light'][i] = QPixmap(self.charWidth, self.charHeight)
			self.fontpixmap['dark'][i].fill(Qt.transparent)
			self.fontpixmap['light'][i].fill(Qt.transparent)
			
			painter = QPainter(self.fontpixmap['dark'][i])
			painter.setRenderHint(QPainter.Antialiasing, True)
			painter.setRenderHint(QPainter.TextAntialiasing, True)
			painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
			painter.setFont(font)
			painter.setPen(QtGui.QColor(0, 0, 0,255))
			painter.drawText(QRect(QPoint(0,0),QPoint(self.charWidth,self.charHeight)),Qt.AlignCenter,i)

			painter = QPainter(self.fontpixmap['light'][i])
			painter.setRenderHint(QPainter.Antialiasing, True)
			painter.setRenderHint(QPainter.TextAntialiasing, True)
			painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
			painter.setFont(font)
			painter.setPen(QtGui.QColor(255, 255, 255,255))
			painter.drawText(QRect(QPoint(0,0),QPoint(self.charWidth,self.charHeight)),Qt.AlignCenter,i)
			
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
		return  "".join([chr(x) if chr(x) in string.printable else "." for x in strin])

	def getLines(self, pos=0):
		while pos < len(self.filebuff)-self.bpl:
			bytes = self.filebuff[pos:pos+self.bpl]
			yield (pos, self.bpl,bytes, self.toAscii(bytes))
			pos += self.bpl
		bytes = self.filebuff[pos:]
		yield (pos, len(self.filebuff)-pos,bytes, self.toAscii(bytes))

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
		return ceil(self.viewport().height()/self.charHeight)

	def totalCharsPerLine(self):
		return  self.getAddressFormatLen()  + self.gap2 + self.getHexLength() + self.gap3 + self.bpl + self.gap4


	# =====================  Coordinate Juggling  ============================
	def pxToCharCoords(self, px, py):
		return ( px / self.charWidth, py / self.charHeight)

	def charToPxCoords(self, cx, cy):
		"return upper left corder of the rectangle containing the char at position cx, cy"
		px = cx * self.charWidth
		py = cy * self.charHeight 
		return QPoint(px, py)

	def pxCoordToAddr(self, coord):
		column, row = self.pxToCharCoords(coord.x(), coord.y())
		column,row = floor(column), floor(row)
		if column >= self.hex_start() and column < self.ascii_start():
			clen =  self.getHexCharFormatLen()
			nib =  (((column -  self.hex_start()) / clen) - int(((column -  self.hex_start()) / clen))) > .3 
			addr = self.pos +  ceil((column-self.hex_start()) / clen)  + (row * self.bpl)
			return  (nib,int(addr))
			
		elif column >=  self.ascii_start():
			rel_column = column-self.ascii_start() 
			addr = self.pos + rel_column + row * self.bpl
			return (0,int(addr))
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
		hex_cx, hex_cy = self.indexToHexCharCoords(cur.getPosition())
		hex_cx += cur.getNibble()
		hex_point = self.charToPxCoords(hex_cx, hex_cy)
		coffset = QPoint(0, self.charHeight-2)
		hex_rect = QRect(hex_point+coffset, QSize(self.charWidth, 2))
		return hex_rect


	def cursorToAsciiRect(self, cur):
		ascii_cx, ascii_cy = self.indexToAsciiCharCoords(cur.getPosition())
		ascii_point = self.charToPxCoords(ascii_cx, ascii_cy)
		coffset = QPoint(0, self.charHeight-2)
		ascii_rect = QRect(ascii_point+coffset, QSize(self.charWidth,2))
		return ascii_rect

	def charAtCursor(self, cursor):
		ascii_char = self.filebuff[cursor.getPosition()]
		hexcode = self.hexcharformat.strip().format(ord(ascii_char))
		hex_char = hexcode[cursor.getNibble()]
		return (hex_char, ascii_char)

	# ====================  Event Handling  ==============================

	def pxToSelectionList(self, pos):
		"""bytes may be involved in more then one selection, this returns a list of those selections"""
		selections = []
		for sel in self.highlights:
			(nib, cur) = self.pxCoordToAddr(pos)
			if sel.contains(cur):
				selections.append(sel)
		return selections
		
	def hover(self,pos):
		tooltip  = ""
		handledobjs = []
		for s in self.pxToSelectionList(pos):
			if s.obj != None:
				if s.obj not in handledobjs:
					if tooltip != "":
						tooltip += "+"
					tooltip += "[%s]" %  s.obj.labelAction(s)
					handledobjs.append(s.obj)
				
		if tooltip != "":
# 			QToolTip.hideText()
			QToolTip.showText(self.mapToGlobal(pos),  tooltip, self)
						
	def getHexCharFormat(self):
		return self.hexcharformat
	
	def getHexCharFormatLen(self):
		return len(self.getHexCharFormat().format(0)) 

	def clearHilights(self):
		self.highlights = []
		
	def getNextColor(self):
		return COLOR_PALETTE[len(self.highlights)]
		
	def addSelection(self,selection):
		self.highlights.append(selection)
		self.updateSelectionListEvent.emit(self.highlights)

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
		return len(self.getAddressFormat().format(self.cursor.getPosition() + (self.visibleLines() * self.bpl)))

	def paintHexByte(self, painter, addr, byte, ph):
		topleft = self.addrToHexPxCoords(addr)
		
		if len(ph):
			size = QSize(ceil(self.charWidth*self.getHexCharFormatLen()), ceil(self.charHeight/len(ph)))
			
			for i,sel in enumerate(ph):
				rect = QRect(topleft + QPoint(0,(self.charHeight/len(ph)) * i), size)
				painter.fillRect(rect,QColor( sel.color))
				
			painter.setPen(QColor(hexColorComplement(sel.color)))
		else:
			painter.setPen(self.palette().color(QPalette.WindowText))
		
		for i,b in enumerate(list(self.getHexCharFormat().format(byte))):
			top = topleft + QPoint(i*self.charWidth,0)
			painter.drawPixmap(QRect(top,top + QPoint(self.charWidth,self.charHeight)),self.fontpixmap['dark'][b])


	def paintAsciiByte(self, painter, addr, byte, ph):
		topleft = self.addrToAsciiPxCoords(addr)
			
		if len(ph):
			size = QSize(ceil(self.charWidth), ceil(self.charHeight/len(ph)))
			for i,sel in enumerate(ph):
				rect = QRect(topleft + QPoint(0,(self.charHeight/len(ph)) * i), size)
				painter.fillRect(rect,QColor( sel.color))
			painter.setPen(QColor(hexColorComplement(sel.color)))
		else:
			painter.setPen(self.palette().color(QPalette.WindowText))
		painter.drawPixmap(QRect(topleft,topleft + QPoint(self.charWidth,self.charHeight)),self.fontpixmap['dark'][byte])


	def cursorMove(self, cursor):
		(start,end) = cursor.getRange()
						
		if end > len(self.filebuff):
			self.cursor.setCursorPosistion(len(self.filebuff))			
				
		self.scrollWindowToCursor()
		self.repaintWidget()

	def paintCursor(self,painter):	
		if self.activeview == "hex":
			painter.fillRect(self.cursorRectHex(), self.palette().color(QPalette.HighlightedText))
			painter.fillRect(self.cursorRectAscii(), self.palette().color(QPalette.Highlight))
		else:
			painter.fillRect(self.cursorRectAscii(),self.palette().color(QPalette.HighlightedText))
			painter.fillRect(self.cursorRectHex(), self.palette().color(QPalette.Highlight))

	def addrToHexPxCoords(self, addr):
		return self.charToPxCoords(self.hex_start() + ((addr % self.bpl) * self.getHexCharFormatLen()), floor(addr / self.bpl) - (self.pos/self.bpl))

	def addrToAsciiPxCoords(self, addr):
		return self.charToPxCoords(self.ascii_start() + ((addr % self.bpl)), floor(addr / self.bpl) - (self.pos/self.bpl))

	def paintEvent(self, event):
		if  self.widgetpainted == None:
			self.repaintWidget()						

		s = time.time()
		painterself = QPainter(self.viewport())
		painterself.drawPixmap(0,0,self.widgetpainted)
		if self.lastpanted < self.paintedevent or (self.blinkstate % 2) == 0: 
			self.lastpanted  = 	self.paintedevent	
			if (self.blinkstate % 2) == 0:
				self.paintCursor(painterself)

					
	def scrollContentsBy(self,distx,disty):
		self.setPosition(self.pos - (disty * self.bpl))			
			
	def setPosition(self,pos):
		self.pos  = pos
		self.repaintWidget()
# 	self.paintedevent += 1
				
	def repaintWidget(self):
		s = time.time()
		self.paintedevent += 1
		self.widgetpainted = QPixmap(self.viewport().width(), self.viewport().height())
		painter = QPainter(self.widgetpainted)
		
		painter.setRenderHint(QPainter.SmoothPixmapTransform)
		painter.setBackgroundMode(Qt.TransparentMode)
		painter.fillRect(0, 0,self.viewport().width(), self.viewport().height(), self.palette().color(QPalette.Base))

		palette = self.viewport().palette()

		rect = self.cursorRectHex()
		rect.setRight(self.cursorRectAscii().right())

		hex_width = self.getHexLength()

		addr_width = self.getAddressFormatLen()
		
		addr_start = (self.addr_start()) 
		hex_start = (addr_start + addr_width + self.gap2)
		ascii_start = (hex_start + hex_width + self.gap3)

		addr_start *= self.charWidth
		hex_start *= self.charWidth
		ascii_start *= self.charWidth

		for i, (address, length, data, ascii) in enumerate(self.getLines(self.pos)):	
			
			if i > self.visibleLines():
				break

			#background stripes
			if self.colorBars and 1 if (address % (self.bpl * 2)) == self.bpl else 0:
				painter.fillRect(0, (i * self.charHeight),(self.totalCharsPerLine() * self.charWidth),  self.charHeight, self.palette().color(QPalette.AlternateBase))
			else:
				painter.fillRect(0, (i * self.charHeight),(self.totalCharsPerLine() * self.charWidth),  self.charHeight, self.palette().color(QPalette.Base))

			# address
			self.printAddress(painter, addr_start,(i * self.charHeight)+self.charHeight, address)

			# data
			for j, byte in enumerate(data):
				addr = address + j
				self.paintByteAtAddr(painter, addr, byte,ascii[j])

			#vert sep bars
			painter.setPen(Qt.gray)
			painter.drawLine(hex_start-(self.charWidth/2), 0, hex_start-(self.charWidth/2), self.height())
			painter.drawLine(ascii_start-(self.charWidth/2), 0, ascii_start-(self.charWidth/2), self.height())								
					
		self.viewport().update()
		print(time.time()-s)


	def printAddress(self, painter, addr_start, point,address):
		painter.setPen(self.palette().color(QPalette.WindowText))
# 		for c in self.getAddressFormat().format(address):
		painter.drawText(addr_start, point, self.getAddressFormat().format(address))
# 			painter.drawText(addr_start, (i * self.charHeight)+self.charHeight, self.getAddressFormat().format(address))
# 			painter.drawText(QRect(QPoint(addr_start,point),QPoint(0,point) + QPoint(self.charWidth,self.charHeight)),Qt.AlignCenter,c)
	
	def paintByteAtAddr(self,painter, addr, data, asciidata):
		ph = []
		
		if  self.cursor.getSelection().contains(addr):
			ph.append(self.cursor.getSelection())
			
		for sel in self.highlights:
			if len(sel) and sel.active and sel.contains(addr):
				ph.append(sel)
		
		self.paintHexByte(painter, addr, data,ph)
		self.paintAsciiByte(painter, addr,  asciidata,ph)
					
	def mouseDoubleClickEvent(self,event):
		for s in self.pxToSelectionList(event.pos()):
			s.obj.editAction(s)

	def mousePressEvent(self, event):
		mod = event.modifiers()
		
		if((event.pos().x()/self.charWidth) < (self.getAddressFormatLen() + self.gap2)):
			self.activeview = 'addr'
			self.toggleAddressFormat()
		elif ((self.getAddressFormatLen() + self.gap2 + self.getHexLength())  > (event.pos().x()/self.charWidth) > (self.getAddressFormatLen() + self.gap2)):
			self.activeview = 'hex'
		else:
			self.activeview = 'ascii'
	
		(nib, cur) = self.pxCoordToAddr(event.pos())	
		if cur is not None and event.buttons() == Qt.LeftButton:
			sl = self.pxToSelectionList(event.pos())
			for s in sl:
				s.obj.selectAction(s)
			
			if (mod & Qt.AltModifier):
				self.dragactive = True
				self.selectactive = False				
			else:
				if (mod & Qt.ShiftModifier):
					if self.dragstart:
						self.cursor.updateSelection(Selection(self.dragstart, cur))
					else:
						self.cursor.updateSelection(Selection(self.cursor.getSelection().getRange()[0], cur))
				else:
					self.cursor.startActiveSelection(Selection(cur,cur))
					self.dragstart = cur

				self.cursor.setNibble(nib)	
				self.selectactive = True
				self.dragactive = False
			
			self.dragselection = sl
# 		self.repaintWidget()			

	def mouseMoveEvent(self, event):	
		(nib,cur) = self.pxCoordToAddr(event.pos())
		if cur is not None:
			if self.cursor.getPosition() != cur:		
				if self.selectactive == True:
					self.cursor.updateSelection(Selection(self.dragstart, cur))	
				elif self.dragactive == True:
					t = cur-self.dragstart
					if t != 0:
						for p in self.pxToSelectionList(event.pos()):					
							p.obj.dragAction(p,t)
						self.dragstart = cur				
			self.hover(event.pos())

	def mouseReleaseEvent(self, event):
		self.selectactive = False
		self.dragactive = False
		self.dragselection = []
	
	def focusInEvent(self, event):
		self.focusEvent.emit(self.cursor.getSelection())

	def adjust(self):
		print(self.numLines() - self.visibleLines() + 1)
		self.verticalScrollBar().setRange(0, self.numLines() - self.visibleLines() + 1)
		self.verticalScrollBar().setPageStep(self.visibleLines())
	
	def resizeEvent(self, event):
		repaint = False

		a = self.getAddressFormatLen()  + self.gap2 + self.getHexLength() + self.gap3 + self.bpl + self.gap4
		b = (self.viewport().width() / self.charWidth) -  ( self.getAddressFormatLen()  + self.gap2 +  self.gap3 +  self.gap4)
		c = b - (self.bpl + (self.bpl * self.getHexCharFormatLen()))
		if self.viewport().width() <  (b  - (1 + (1 * self.getHexCharFormatLen()))):
			nbpl = 1
		else:
			snap = 0
			minlval = 0
			widths = []
			for i in range(1,64):
				l = ( self.viewport().width() /self.charWidth ) - (( self.getAddressFormatLen()  + self.gap2 +  self.gap3 +  self.gap4) + (i + (i * self.getHexCharFormatLen())))
				widths.append(l)				
	
			nbpl =  widths.index(min(widths, key=abs)) + 1

# 		self.adjust()
			
		if self.bpl != nbpl:
			self.bpl = nbpl
			repaint = True
			
		vl = self.visibleLines()
		if self.knownvisiblelines != vl:
			self.knownvisiblelines = vl
			repaint = True

		if repaint:
			self.repaintWidget()		
			

	def scrollWindowToCursor(self):
		x, y = self.indexToAsciiCharCoords(self.cursor.getPosition())
		if y > self.visibleLines() - 2:
			self.verticalScrollBar().setValue(((self.verticalScrollBar().value() + y) - self.visibleLines()) + 2)
		if y < 1:
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() + y)
		#fixme
	
	def event(self, event):
		if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
			self.toggleActiveView()
			return False
		return super(HexWidget, self).event(event)

	def sizeHint(self):
		return QtCore.QSize((self.totalCharsPerLine() * self.charWidth), (25 * self.charHeight))
        		
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
					self.pos = len(self.filebuff)
				elif text != '':
					oldbyte = self.filebuff[self.cursor.getPosition()] 
					
					if  self.activeview == 'hex':
						if text in string.hexdigits:
							if self.cursor.getNibble() == 0:
								byte = (oldbyte & 0x0f) | (int(text,16) << 4)
							else:
								byte = (oldbyte & 0xf0) | int(text,16)
								
							if byte != oldbyte:		
								self.editEvent.emit((self.cursor.getSelection(),byte))
							self.cursor.right()
							
						elif ord(text) in b'gG':
							self.jumpToEvent.emit()

					elif self.activeview == 'ascii':
						byte = ord(text)
						if byte != oldbyte:		
							self.editEvent.emit((self.cursor.getSelection(),byte))
						self.cursor.right()
						self.cursor.right()						
						
					elif self.activeview == 'addr':
						if ord(text) in b'gG':
							self.jumpToEvent.emit()	
		self.cursor.blinkstate = 0
		self.repaintWidget()
			
					

							
