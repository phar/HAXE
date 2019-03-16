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


def hilo2(r,g,b):
	b = ((r * 299.0) + (g * 587.0) + (b * 114.0)) / 1000.0
	if b < 128:
		return  0
	else:
		return 1
	
def hexColorComplement2(cstr):
	r = (cstr & 0xff0000) >> 16
	g = (cstr & 0x00ff00) >> 8
	b = (cstr & 0x0000ff)
	return hilo2(r,g,b)



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
		
	def setWidgetFont(self,font="Courier",size=10):
		self.font = font
		self.fontsize = size
		self.fontpixmap = {}
			
		font = QFont(self.font, self.fontsize)
		font.setStyleStrategy(QFont.NoAntialias | QFont.Light)
		self.fm = QFontMetrics(font)
		self.charWidth = self.fm.maxWidth() * self.charWidthMultiplier
		self.charHeight = self.fm.height() * self.charHeightMultiplier
		print(self.font)
		self.setFont(font)
		self.fontpixmap = {'light':{},'dark':{}}
		for i in string.printable:
			self.fontpixmap['dark'][i] = QPixmap(self.charWidth, self.charHeight)
			self.fontpixmap['light'][i] = QPixmap(self.charWidth, self.charHeight)
			self.fontpixmap['dark'][i].fill(Qt.transparent)
			self.fontpixmap['light'][i].fill(Qt.transparent)
			
    
			painter = QPainter(self.fontpixmap['dark'][i])
# 			painter.setRenderHint(painter.RenderHint(QPainter.TextAntialiasing), True)
			painter.setFont(font)
			painter.setPen(QtGui.QColor(0, 0, 0,255))
			painter.drawText(QRect(QPoint(0,0),QPoint(self.charWidth,self.charHeight)),Qt.AlignCenter,i)

			painter = QPainter(self.fontpixmap['light'][i])
# 			painter.setRenderHint(painter.RenderHint(QPainter.TextAntialiasing), True)

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
		if self.pos < 0:
			self.pos = 0
		while pos < len(self.filebuff)-self.bpl:
			bytes = self.filebuff[pos:pos+self.bpl]
			yield (pos, self.bpl,bytes, self.toAscii(bytes))
			pos += self.bpl
		bytes = self.filebuff[pos:]
		yield (pos, len(self.filebuff)-pos,bytes, self.toAscii(bytes))

	def numLines(self):
		return ceil(len(self.filebuff) / self.bpl)

	def cursorRectHex(self):
		return self.cursorToHexRect(self.cursor)

	def cursorRectAscii(self):
		return self.cursorToAsciiRect(self.cursor)

	def visibleColumns(self):
		ret = int(ceil(float(self.viewport().width())/self.charWidth))
		return ret

	def visibleLines(self):
		return ceil(self.viewport().height() / self.charHeight)

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
					tooltip += "[%s]" %  s.obj.labelAction(self.parent, s) #fixme
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
		
# 	def getNextColor(self):
# 		return COLOR_PALETTE[len(self.highlights)]
		
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
		sel = None
		
		if len(ph):
			size = QSize(ceil(self.charWidth*self.getHexCharFormatLen()), ceil(self.charHeight/len(ph)))
			for i,sel in enumerate(ph):
				rect = QRect(topleft + QPoint(0,(self.charHeight/len(ph)) * i), size)
				painter.fillRect(rect,QColor( sel.color))
				
# 			painter.setPen(QColor(hexColorComplement(sel.color)))
# 		else:
# 			painter.setPen(self.palette().color(QPalette.WindowText))
		
		for i,b in enumerate(list(self.getHexCharFormat().format(byte))):
			top = topleft + QPoint(i*self.charWidth,0)
			if sel is not None:
				if hexColorComplement2(sel.color):
					painter.drawPixmap(QRect(top,top + QPoint(self.charWidth,self.charHeight)),self.fontpixmap['dark'][b])
				else:
					painter.drawPixmap(QRect(top,top + QPoint(self.charWidth,self.charHeight)),self.fontpixmap['light'][b])
			else:
				painter.drawPixmap(QRect(top,top + QPoint(self.charWidth,self.charHeight)),self.fontpixmap['dark'][b])

	def paintAsciiByte(self, painter, addr, byte, ph):
		topleft = self.addrToAsciiPxCoords(addr)
		sel = None
		if len(ph):
			size = QSize(ceil(self.charWidth), ceil(self.charHeight/len(ph)))
			for i,sel in enumerate(ph):
				rect = QRect(topleft + QPoint(0,(self.charHeight/len(ph)) * i), size)
				painter.fillRect(rect,QColor( sel.color))
			painter.setPen(QColor(hexColorComplement(sel.color)))
# 		else:
# 			painter.setPen(self.palette().color(QPalette.WindowText))
		if sel is not None:
			if hexColorComplement2(sel.color):
				painter.drawPixmap(QRect(topleft,topleft + QPoint(self.charWidth,self.charHeight)),self.fontpixmap['dark'][byte])
			else:
				painter.drawPixmap(QRect(topleft,topleft + QPoint(self.charWidth,self.charHeight)),self.fontpixmap['light'][byte])
		else:
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
		p = self.pos - (disty * self.bpl)
		if p < 0:
			p = 0
		self.setPosition(p)		
		self.adjust()
	
			
	def setPosition(self,pos):
		self.pos  = pos
		self.repaintWidget()
				
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
		# print(time.time()-s)


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
			s.obj.editAction(self.parent, s) #fixme 

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
				s.obj.selectAction(self.parent,s) #fixme
			
			if (mod & Qt.AltModifier):
				self.dragactive = True
				self.selectactive = False	
				self.dragstart = cur
			
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

	def mouseMoveEvent(self, event):	
		(nib,cur) = self.pxCoordToAddr(event.pos())
		if cur is not None:
			if self.dragstart != cur:		
				if self.selectactive == True:
					self.cursor.updateSelection(Selection(self.dragstart, cur))	
				elif self.dragactive == True:
					t = cur-self.dragstart
					if t != 0:
						for p in self.pxToSelectionList(event.pos()):					
							p.obj.dragAction(self.parent, p,t)
						self.repaintWidget()
						self.dragstart = cur				
			self.hover(event.pos())

	def mouseReleaseEvent(self, event):
		self.selectactive = False
		self.dragactive = False
		self.dragselection = []
	
	def focusInEvent(self, event):
		self.focusEvent.emit(self.cursor.getSelection())

	def adjust(self):
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


		
# 		p = (self.verticalScrollBar().value() * self.bpl)
# 		print(p)
		
	# 	self.verticalScrollBar().setRange(0, self.numLines() - self.visibleLines() + 1)
# 		self.verticalScrollBar().setPageStep(self.visibleLines())

		

# 		print("mnoo", nbpl)
		if self.bpl != nbpl: 
			self.bpl = nbpl
			repaint = True
			self.pos = 0 #fixme, this is a compromise for now
			self.adjust()
# # 			
# 		vl = self.visibleLines()
# 		if self.knownvisiblelines != vl:
# 			self.knownvisiblelines = vl
# 			repaint = True
# 
# 		self.adjust()
# 
		if repaint:
			self.repaintWidget()		
# 			

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
			
					

							
