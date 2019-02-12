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

QPalette.HighlightedText
def hilo(r,g,b):
	b = ((r * 299.0) + (g * 587.0) + (b * 114.0)) / 1000.0
	if b < 128:
		return  (255,255,255)
	else:
		return tuple(int(QColor(QPalette.WindowText).name()[i:i+2], 16) for i in (1, 3 ,5))

def hexColorComplement(cstr):
        (r,g,b) = tuple(int(cstr[i:i+2], 16) for i in (1, 3 ,5))
#         k = hilo(r, g, b)
#         return "#" + "".join(["%02x" % x for x in tuple(k - u for u in (r, g, b))])
        return "#" + "".join(["%02x" % x for x in hilo(r,g,b)])

class JumpToDialog(QDialog):
	def __init__(self, parent , api):
		super(JumpToDialog, self).__init__(parent)

		self.api = api
		layout = QFormLayout()
		self.parent = parent
		l = QLabel("Offset")
		self.le1 = QLineEdit()
		layout.addRow(l, self.le1)		

		self.btn = QRadioButton("Hexidecimal")
		self.le = QLineEdit()
		layout.addRow(None,self.btn)		
		self.btn1 = QRadioButton("Decimal")
		layout.addRow(None,self.btn1)
		self.btn1.setChecked(True)
		self.setLayout(layout)
		self.btn2 = QPushButton("Cancel")
		self.btn3 = QPushButton("OK")
		self.btn3.clicked.connect(self.dook)
		self.btn2.clicked.connect(self.doclose)
		layout.addRow(self.btn2,self.btn3)
		self.setLayout(layout)
		self.setWindowTitle("Jumt to Offset")

	def dook(self):
		addr = 0
		if self.btn.isChecked():
			addr = int(self.le.text().replace("0x",""),16)
		elif self.btn1.isChecked():
			addr = int(self.le.text())
		self.parent.cursor.setAddress(int())
		
	def doclose(self):
		self.close()



class SearchDialog(QWidget):
	def __init__(self, po=None,parent=None):
		super(SearchDialog, self).__init__(parent)
		self.lyt = QGridLayout()
		self.setLayout(self.lyt)
		self.parent = po
# 		self.api = api
		self.filename = self.parent.filebuff.filename
		self.searchline = QLineEdit()
		self.replaceLine = QLineEdit()
		self.searchlinel = QLabel("Search")
		self.pb_searchn = QPushButton("Find Next")
		self.pb_searchp = QPushButton("Find Prev")
		self.pb_replacen = QPushButton("Replace Next")
		self.pb_replacen = QPushButton("Replace All")
		self.pb_replace= QLabel("Replace")

		self.lyt.addWidget(self.searchlinel, 0,0,1,1)
		self.lyt.addWidget(self.searchline, 0, 1,1,2)

		self.lyt.addWidget(self.pb_replace, 1,0,1,1)# 
		self.lyt.addWidget(self.replaceLine, 1, 1,1,2)

		l = QLabel("Mode:")
		self.pm = QComboBox()
		for nf in self.parent.api.getConverters()[0]:
			(n,f) = nf
			self.pm.addItem(n)	
			
		self.lyt.addWidget(l, 2, 1)
		self.lyt.addWidget(self.pm, 2, 2)
		

# 		self.lyt.addWidget(self.pb_replace, 1,0,1,1)# 
# 		self.lyt.addWidget(self.replaceLine, 1, 1,1,2)


		self.search_a = QRadioButton("ASCII")
		self.search_a.setChecked(True)
		self.search_chex = QRadioButton("C Hex")
		self.search_hex = QRadioButton("Hex String")
		self.search_reg = QRadioButton("RegEx")



# 		self.lyt.addWidget(self.search_a, 1, 0)
# 
# 		self.lyt.addWidget(self.searchline, 0, 0,1,3)
# 		self.lyt.addWidget(self.search_a, 2, 0)
# 		self.lyt.addWidget(self.search_hex, 2, 1)
# 		self.lyt.addWidget(self.search_reg, 2, 2)


# 		self.lyt.addWidget(self.pb_replacen, 3, 0)
# 		self.lyt.addWidget(self.pb_replacep, 3, 1)
# 		self.lyt.addWidget(self.pb_searchn, 3, 2)
# 		self.lyt.addWidget(self.pb_searchn, 3, 3)

		self.pb_search.clicked.connect(self.do_search)

	def do_search(self):
		phrase = self.searchline.text()
		if self.search_a.isChecked():
			index = self.parent.filebuff.find(phrase.encode('utf-8'), self.parent.cursor._selection.start)
		elif self.search_chex.isChecked():
			pass
		elif self.search_hex.isChecked():
			phrase = self.searchline.text().decode("hex").encode('utf-8')
			index = self.parent.filebuff.find(phrase.encode('utf-8'), self.parent.cursor._selection.start)
		
		elif self.search_reg.isChecked():
			pass			
# 		
		if index >= 0:
			self.api.openFiles[self.filename].goto(index)
# 			self.statusBar().showMessage("found at offset 0x%08x" % index)
		else:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setText("Search String was not found")
			msg.setInformativeText("Search string not found.")
			msg.setWindowTitle("Not found")
			msg.setStandardButtons(QMessageBox.Ok)
# 			self.statusBar().showMessage("search string not found")
			retval = msg.exec_()		
		
		self.close()


class HexDialog(QMainWindow):
	undoEvent = QtCore.pyqtSignal(object)
	redoEvent = QtCore.pyqtSignal(object)
	saveEvent = QtCore.pyqtSignal(object)
	pasteFailed = QtCore.pyqtSignal()
	def __init__(self, api, parent=None,fileobj=None):
		super(HexDialog, self).__init__(parent)
		self.filebuff = fileobj
		self.api = api
		self.parent = parent
		self.clipboardata = []
# 		self.structs = []
		self.isActiveWindow = False
		self.hexWidget =  HexWidget(api,self,self.filebuff, font="Courier", fontsize=12)
		self.setCentralWidget(self.hexWidget);
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
	
		self.api.activeWindowChanged.connect(self.active_notify)
		self.hexWidget.selectionChanged.connect(self.select_changed)
		self.hexWidget.copyEvent.connect(self.copy)
		self.hexWidget.cutEvent.connect(self.cut)
		self.hexWidget.deleteEvent.connect(self.delete)
		self.hexWidget.pasteEvent.connect(self.paste)
		self.hexWidget.editEvent.connect(self.edit)
		self.hexWidget.focusEvent.connect(self.setFocus)
	
		self.hexWidget.findEvent.connect(self.search)
	
		self.synccheck = QCheckBox("Sync")
		self.statusBar.addWidget(self.synccheck)
		
		self.selectstatus = QLabel("")
		self.statusBar.addWidget(self.selectstatus)
		
		self.statusBar.show()

	def search(self):
		self.dia = SearchDialog(self)
		self.dia.show()
		self.dia.raise_()
		self.dia.activateWindow()
		      	
	def getSelection(self):
		return self.hexWidget.getSelection()
      	
	def select_changed(self,selection):
		(start,end) = selection.getRange()
		if len(selection):
			self.selectstatus.setText(" [%d bytes selected at offset 0x%x out of %d bytes]" % (len(selection), start, len(self.filebuff)))
		else:
			self.selectstatus.setText(" [offset 0x%x (%d) of %d bytes]" % (start,start, len(self.filebuff)))
		self.selectstatus.repaint()

	def setFocus(self):
		self.api.setActiveFocus(self.filebuff.filename)

	def active_notify(self, fn):
		if fn == self.filebuff.filename:
			self.isActiveWindow = True
		else:
			self.isActiveWindow = False

	def cut(self,selection):
		(start,end) = self.hexWidget.cursor._selection.getRange()
		self.copy(selection)	
		self.delete(selection)
				
	def delete(self,selection):
		(start,end) = self.hexWidget.cursor._selection.getRange()
		self.filebuff.addEdit(selection, b'')
		self.hexWidget.cursor.updateSelection(Selection(start, start))
		self.hexWidget.viewport().update()
		
	def edit(self,tup):
		(selection,edit) = tup
		self.filebuff.addEdit(selection,edit)
		self.hexWidget.viewport().update()

	def paste(self,selection):
		cb = QApplication.clipboard()
		if cb.ownsClipboard():
			t = self.clipboardata	
		else:
			t = bytearray(cb.text(),'utf-8')
			
		try:
			t = self.api.getPasteModeFn()(t)
			self.filebuff.addEdit(selection, t)
			(start,end) = self.hexWidget.cursor._selection.getRange()
			self.hexWidget.goto(start)
			self.hexWidget.cursor.updateSelection(Selection(start, start + len(t)))
			self.hexWidget.viewport().update()			
		except:
			self.pasteFailed.emit()		
	
	def copy(self,slection):
		(start,end)  = self.hexWidget.cursor._selection.getRange()
		t = self.filebuff[start:end]			
		self.clipboardata = t
		cb = QApplication.clipboard()
		t = self.api.getCopyModeFn()(t)
		cb.setText(str(t), mode=cb.Clipboard)
		self.hexWidget.viewport().update()

class HexWidget(QAbstractScrollArea):
	selectionChanged = QtCore.pyqtSignal(object)
	focusEvent = QtCore.pyqtSignal(object)
	copyEvent = QtCore.pyqtSignal(object)
	cutEvent = QtCore.pyqtSignal(object)
	pasteEvent = QtCore.pyqtSignal(object)
	findEvent = QtCore.pyqtSignal(object)
	editEvent = QtCore.pyqtSignal(object)	
	deleteEvent = QtCore.pyqtSignal(object)
	
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
		self.ActiveView = 'hex'
		self.highlights = []
		self.structs = []
		self.dragactive = 0
		# constants... NOT IF I HAVE ANYTHING TO SAY ABOUT IT
		self.bpl = 16
		self.gap2 = 2
		self.gap3 = 1
		self.gap4 = 3
		self.pos = 0
		self.magic_font_offset = 4
		self.backgroundStripes = True
		
		self.setWidgetFont(font,fontsize)
		self.cursor = Cursor(self, 0,0)
		
		self.cursor.changed.connect(self.selectionChanged.emit)
		self.cursor.changed.connect(self.cursorMove)		
		self.cursor.startCursor(500)
		self.horizontalScrollBar().setEnabled(False);
		self.setMouseTracking(True)  
		self.adjust()
		

	def setWidgetFont(self,font="Courier",size=12):
		self.font = font
		self.fontsize = size
		self.setFont(QFont(self.font, self.fontsize))
		
		self.charWidth = self.fontMetrics().width("2")
		self.charHeight = self.fontMetrics().height()

	def sliderChange(self,change):
		print("yepyep")
	def toggleAddressFormat(self):
		if 	self.addressformat == "{:08d}":
			self.addressformat = "{:08x}"
		else:
			self.addressformat = "{:08d}"		

	def toggleActiveView(self):
		if 	self.ActiveView == "hex":
			self.ActiveView = "ascii"
		else:
			self.ActiveView = "hex"		
			
	def getSelection(self):
		return self.cursor.getSelection()

	def contextMenuEvent(self, event):
		menu = QMenu(self)		
		mnu = {}
		for n in self.api.getStructList():
			mnu[n] = menu.addAction("Struct %s here" % n, lambda n = n: self.structAtAddress(n,self.cursor._selection.start))			
		action = menu.exec_(self.mapToGlobal(event.pos()))

	def structAtAddress(self,struct,address):
		print("define struct %s @ %08x" % (struct,address))
		self.structs.append((struct,address))
		self.refreshStructs()
				
	def refreshStructs(self):
		for (structn, address) in self.structs:
			s = self.api.getStruct(structn);
			t = s.parse(self.filebuff[self.cursor._selection.start:self.cursor._selection.start+s.sizeof()])
			tally = 0
			for  i in s.subcons:
				self.addSelection(int(address+tally), int(address+tally + i.sizeof()))
				tally += i.sizeof()
		self.viewport().update()

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
			yield (pos, self.bpl, self.toAscii(self.filebuff[pos:pos+self.bpl]))
			pos += self.bpl
		yield (pos, len(self.filebuff)-pos, self.toAscii(self.filebuff[pos:]))

	def numLines(self):
		return ceil(float(len(self.filebuff))/ self.bpl)

	def cursorRectHex(self):
		return self.cursorToHexRect(self.cursor)

	def cursorRectAscii(self):
		return self.cursorToAsciiRect(self.cursor)

# 	def updateCursor(self):
# 		self.blink = not self.blink
# 		self.viewport().update(self.cursorRectHex())

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
		cx = floor(px / self.charWidth)
		cy = floor((py-self.magic_font_offset) / self.charHeight)
		return (cx, cy)


	def charToPxCoords(self, cx, cy):
		"return upper left corder of the rectangle containing the char at position cx, cy"
		px = cx * self.charWidth
		py = cy * self.charHeight + (self.magic_font_offset)
		return QPoint(px, py)

	def pxCoordToAddr(self, coord):
		column, row = self.pxToCharCoords(coord.x(), coord.y())
		if column >= self.hex_start() and column < self.ascii_start():
			rel_column = (column-self.hex_start() / 2.0)
			line_index = rel_column - (rel_column / self.getHexCharFormatLen())
			addr = self.pos + (line_index / 2.0) + (row * self.bpl)
			return  ceil(addr)-2
		elif column >=  self.ascii_start():
			rel_column = column-self.ascii_start() 
			addr = self.pos + rel_column + row * self.bpl
			return  addr

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
		hex_rect = QRect(hex_point, QSize( 2, self.charHeight))

		return hex_rect


	def cursorToAsciiRect(self, cur):
		ascii_cx, ascii_cy = self.indexToAsciiCharCoords(cur._selection.end)
		ascii_point = self.charToPxCoords(ascii_cx, ascii_cy)
		ascii_rect = QRect(ascii_point, QSize(2, self.charHeight))
		return ascii_rect

	def charAtCursor(self, cursor):
		ascii_char = self.filebuff[cursor.getAddress()]
		hexcode = self.hexcharformat.strip().format(ord(ascii_char))
		hex_char = hexcode[cursor.getNibble()]
		return (hex_char, ascii_char)

	# ====================  Event Handling  ==============================


	def mousePressEvent(self, event):
		if((event.pos().x()/self.charWidth) < (self.getAddressFormatLen() + self.gap2)):
			self.ActiveView = 'addr'
			self.toggleAddressFormat()
			self.viewport().update()
		elif ((self.getAddressFormatLen() + self.gap2 + self.getHexLength())  > (event.pos().x()/self.charWidth) > (self.getAddressFormatLen() + self.gap2)):
			self.ActiveView = 'hex'
		else:
			self.ActiveView = 'ascii'
	
		cur = self.pxCoordToAddr(event.pos())	
		if cur is not None and event.buttons() == Qt.LeftButton:
			self.dragactive  = True
			self.cursor.startActiveSelection(Selection(cur,cur))	
			self.viewport().update()
# 			QToolTip.showText(self.mapToGlobal(event.pos()), "foop %d %d" % (),self.parent)
		
	def hover(self,pos):
		QToolTip.hideText()
		x = self.pxCoordToAddr(pos)
		QToolTip.showText(self.mapToGlobal(pos), "foop 0x%02x" % self.filebuff[x],self.parent)
	
	def mouseMoveEvent(self, event):	
		cur = self.pxCoordToAddr(event.pos())
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
		self.adjust()

	def paintSelection(self, painter, line, selection):
	
		(start,end) = self.cursor._selection.getRange()
	
		cx_start_hex, cy_start_hex = self.indexToHexCharCoords(start)
		cx_end_hex, cy_end_hex = self.indexToHexCharCoords(end)
		
		cx_start_ascii, cy_start_ascii = self.indexToAsciiCharCoords(start)
		cx_end_ascii, cy_end_ascii = self.indexToAsciiCharCoords(end)
		
		if line == cy_start_hex:
			topleft_hex = QPoint(self.charToPxCoords(cx_start_hex, line))
			topleft_ascii = QPoint(self.charToPxCoords(cx_start_ascii, line))
			if line == cy_end_hex: # single line selection
				bottomright_hex = QPoint(self.charToPxCoords(cx_end_hex, line))
				bottomright_ascii = QPoint(self.charToPxCoords(cx_end_ascii, line))
				
			else:
				bottomright_hex = QPoint(self.charToPxCoords(self.ascii_start() - self.gap2, line))
				bottomright_ascii = QPoint(self.charToPxCoords(self.ascii_start() + self.bpl, line))

			bottomright_hex += QPoint(0, self.charHeight)				
			bottomright_ascii += QPoint(0, self.charHeight)
			painter.fillRect(QRect(topleft_hex, bottomright_hex), QColor(selection.color))
			painter.fillRect(QRect(topleft_ascii, bottomright_ascii), QColor(selection.color))
			
		elif line > cy_start_hex and line <= cy_end_hex:
			topleft_hex = QPoint(self.charToPxCoords(self.hex_start(), line))
			topleft_ascii = QPoint(self.charToPxCoords(self.ascii_start(), line))
			if line == cy_end_hex:
				bottomright_hex = QPoint(self.charToPxCoords(cx_end_hex, line))
				bottomright_ascii = QPoint(self.charToPxCoords(cx_end_ascii, line))					
			else:
				bottomright_hex = QPoint(self.charToPxCoords(self.ascii_start() - self.gap2, line))
				bottomright_ascii = QPoint(self.charToPxCoords(self.ascii_start() + self.bpl, line))

			bottomright_hex += QPoint(0, self.charHeight)	
			bottomright_ascii += QPoint(0, self.charHeight)
			painter.fillRect(QRect(topleft_hex, bottomright_hex), QColor(selection.color))
			painter.fillRect(QRect(topleft_ascii, bottomright_ascii), QColor(selection.color))

	def getHexCharFormat(self):
		return self.hexcharformat
	
	def getHexCharFormatLen(self):
		return len(self.getHexCharFormat().format(0))

	def clearHilights(self):
		self.highlights = []
		
	def getNextColor(self):
		return COLOR_PALETTE[len(self.highlights)]
		
	def addSelection(self,start,end=1, color=None):
		if color == None:
			color =  self.getNextColor()
		self.highlights.append(Selection(start,end,True, color))

	def paintHex(self, painter, row, column):
		addr = self.pos + row * self.bpl + column
		topleft = self.charToPxCoords(column*self.getHexCharFormatLen() + self.hex_start(), row)
		bottomleft = topleft + QPoint(0, self.charHeight-self.magic_font_offset)
		byte = self.getHexCharFormat().format(self.filebuff[addr])
		size = QSize(self.charWidth*self.getHexCharFormatLen(), self.charHeight)
		rect = QRect(topleft, size)


		if self.dragactive and self.cursor.getSelection().contains(addr):
			painter.fillRect(rect,self.palette().color(QPalette.Highlight))
			painter.setPen(self.palette().color(QPalette.HighlightedText))
			painter.drawText(bottomleft, byte)
			painter.setPen(self.palette().color(QPalette.WindowText))
		else:
			for sel in self.highlights:
				if len(sel) and sel.active and sel.contains(addr):
					painter.fillRect(rect,QColor( sel.color))
					painter.setPen(QColor(hexColorComplement(sel.color)))
					painter.drawText(bottomleft, byte)
					return
			painter.setPen(self.palette().color(QPalette.WindowText))
			painter.drawText(bottomleft, byte)
		
	

	def paintAscii(self, painter, row, column):
		addr = self.pos + row * self.bpl + column
		topleft = self.charToPxCoords(column + self.ascii_start(), row)
		bottomleft = topleft + QPoint(0, self.charHeight-self.magic_font_offset)
		byte = self.toAscii(bytearray([self.filebuff[addr]]))
		size = QSize(self.charWidth, self.charHeight)
		rect = QRect(topleft, size)

		if self.dragactive  and self.cursor.getSelection().contains(addr):
			painter.fillRect(rect,self.palette().color(QPalette.Highlight))
			painter.setPen(self.palette().color(QPalette.HighlightedText))
			painter.drawText(bottomleft, byte )
			painter.setPen(self.palette().color(QPalette.WindowText))
		else: 
			for sel in self.highlights:
				if len(sel) and sel.active and sel.contains(addr):
					painter.fillRect(rect,QColor( sel.color))
					painter.setPen(QColor(hexColorComplement(sel.color)))
					painter.drawText(bottomleft, byte )
					return
			painter.setPen(self.palette().color(QPalette.WindowText))
			painter.drawText(bottomleft, byte )


	def paintEvent(self, event):
		start = time.time()
		painter = QPainter(self.viewport())
		palette = self.viewport().palette()

		rect = self.cursorRectHex()
		rect.setRight(self.cursorRectAscii().right())

		if event.rect() == self.cursorRectHex(): 
			if self.cursor.blink and self.parent.isActiveWindow:
				if self.ActiveView == "hex":
					painter.fillRect(self.cursorRectHex(), Qt.black)
				else:
					painter.fillRect(self.cursorRectHex(), Qt.gray)
			self.viewport().update(self.cursorRectAscii())
			return
		elif event.rect() == self.cursorRectAscii():
			if self.cursor.blink and self.parent.isActiveWindow :
				if self.ActiveView == "ascii":
					painter.fillRect(self.cursorRectAscii(), Qt.black)
				else:
					painter.fillRect(self.cursorRectAscii(), Qt.gray)
			return

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
			if i > self.visibleLines():
				break

			#background stripes
			if self.backgroundStripes:
				if (i % 2):
					painter.fillRect(0, (i * self.charHeight)+self.magic_font_offset, self.viewport().width(),  self.charHeight, self.palette().color(QPalette.AlternateBase))
				else:
					painter.fillRect(0, (i * self.charHeight)+self.magic_font_offset, self.viewport().width(),  self.charHeight, self.palette().color(QPalette.Base))
			
			(address, length, ascii) = line
			
			data = self.filebuff[address:address+length]

			# selection 
			sel = self.cursor.getSelection()
			if len(sel):
				self.paintSelection(painter, i, self.cursor.getSelection())
			else:
				#highlights
				for h in self.highlights:
					self.paintSelection(painter, i, h)

			# address
			painter.setPen(self.palette().color(QPalette.WindowText))
			painter.drawText(addr_start, (i * self.charHeight)+self.charHeight, self.getAddressFormat().format(address))

			# data
			for j, byte in enumerate(data):
				self.paintHex(painter, i, j)
				self.paintAscii(painter, i, j)
				
		duration = time.time()-start
		if duration > 0.02 and self.debug == 1:
			print ("painting took: ", duration, 's')

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
		elif event.matches(QKeySequence.Delete):
			self.deleteEvent.emit(self.cursor.getSelection())
		elif event.matches(QKeySequence.Paste):
			self.pasteEvent.emit(self.cursor.getSelection())
		elif event.matches(QKeySequence.Delete):
			self.deleteEvent.emit(self.cursor.getSelection())
		elif event.matches(QKeySequence.Find):
			self.findEvent.emit(self.cursor.getSelection())
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
				elif text != '':
					oldbyte = self.filebuff[self.cursor.getAddress()]
					hexalpha = "0123456789abcdefABCDEF"
					if  self.ActiveView == 'hex':
						if text in hexalpha:
							if self.cursor.getNibble() == 0:
								byte = (oldbyte & 0x0f) | (int(text,16) << 4)
							else:
								byte = (oldbyte & 0xf0) | int(text,16)
							if byte != oldbyte:		
								self.editEvent.emit((Selection(self.cursor.getAddress()),byte))
							self.cursor.right()
						elif ord(text) in b'gG':
							f  = JumpToDialog(self,self.api)
							f.show()
					elif   self.ActiveView == 'ascii':
						byte = ord(text)
						if byte != oldbyte:		
							self.editEvent.emit((Selection(self.cursor.getAddress()),byte))
						self.cursor.right()
						self.cursor.right()
					elif self.ActiveView == 'addr':
						if ord(text) in b'gG':
							f  = JumpToDialog(self,self.api)
							f.show()
				self.viewport().update()
