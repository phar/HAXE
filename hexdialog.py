import mmap
import os
# from math import *
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
import traceback

from hexwidget import *

class BookmarkWidget(QTableWidget):
	def __init__(self,parent):
		QWidget.__init__(self,parent)
		self.parent = parent
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.horizontalHeader().setStretchLastSection(True)
		self.setColumnCount(3)

	def contextMenuEvent(self, event):
		menu = QMenu(self)
		mnu = {} #fixme
		mnu["save"] = menu.addAction("Save Bookmarks", self.saveBookmarks)	
		mnu["load"] = menu.addAction("Load Bookmarks", self.loadBookmarks)			
		action = menu.exec_(self.mapToGlobal(event.pos()))

	def maintainBookmarks(self, bookmarks):
		self.setRowCount(len(bookmarks))
		i = 0
		for s in bookmarks:
			(start,end) = s.getRange()
			qtw = QTableWidgetItem("0x%08x" % start)
			self.setItem(i,0, qtw)
			qtw.setBackground(QColor( s.color))
			qtw = QTableWidgetItem("0x%08x" % end)
			self.setItem(i,1, qtw)
			qtw.setBackground(QColor( s.color))

			if s.obj[0] == 'struct':
				(type, structname,parent,child) = s.obj
				qtw =  QTableWidgetItem(".".join([structname,child.name]) + " %s" % "")
				qtw.setBackground(QColor( s.color))
				self.setItem(i,2,qtw)
			elif s.obj[0] == 'note':
				(type, text) = s.obj
				qtw = QTableWidgetItem(text)
				qtw.setBackground(QColor( s.color))
				self.setItem(i,2, qtw)
			i+=1
			
			
	def mouseDoubleClickEvent(self, event):
		self.parent.hexWidget.goto(int(self.item(self.currentIndex().row(),1).text(), 16))
		self.parent.hexWidget.goto(int(self.item(self.currentIndex().row(),0).text(), 16))
		
	def loadBookmarks(self):
		self.filename = QFileDialog.getOpenFileName(self, "Load Bookmarks From...")[0]
		if self.filename:
			pass
			
	def saveBookmarks(self):
		self.filename = QFileDialog.getSaveFileName(self, "Save Bookmarks as...")[0]
		if self.filename:
			self.parent.api.log("Saving...")
			f = open(self.filename,"wb")
			for s in self.parent.hexWidget.highlights:
				(start,end) = s.getRange()
				f.write(b"%d," % start)
				f.write(b"%d," % end)
				f.write(b"%s," % bytearray(s.obj[0],"utf-8"))
				if s.obj[0] == 'struct':
					(type, structname,parent,child) = s.obj
					f.write(b"%s" % bytearray(".".join([structname,child.name]),"utf-8"))
				elif s.obj[0] == 'note':
					(type, text) = s.obj
					f.write(b"%s" % bytearray(text,"utf-8"))
				f.write(b"\r\n")
			f.close()
			self.parent.api.log("done.")
			pass

class HexDialog(QMainWindow):
	saveEvent = QtCore.pyqtSignal(object)
	pasteFailed = QtCore.pyqtSignal()
	def __init__(self, api, parent=None,fileobj=None):
		super(HexDialog, self).__init__(parent)
		self.filebuff = fileobj
		self.api = api
		self.parent = parent
		self.clipboardata = []
		self.structs = []
		self.struct_hints = {}		
		self.clipboarcopy = [] #fixme, replace with hash
		self.isActiveWindow = False
		self.hexWidget =  HexWidget(api,self,self.filebuff, font="Courier", fontsize=12)
		splitter1 = QSplitter(Qt.Horizontal)	
		self.setCentralWidget(splitter1)
		splitter1.addWidget(self.hexWidget)
			
		self.bookmarks  = BookmarkWidget(self)
		self.hexWidget.updateSelectionListEvent.connect(self.bookmarks.maintainBookmarks)

# 		self.bookmarksbuildWindow
		
		splitter1.addWidget(self.hexWidget)
		splitter1.addWidget(self.bookmarks)
		splitter1.setOrientation( Qt.Vertical)
		splitter1.setSizes((999999,0))
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
		self.hexWidget.undoEvent.connect(self.undo)
		self.hexWidget.undoEvent.connect(self.redo)
		self.hexWidget.ctxtMenuEvent.connect(self.contextEvent)
	
		self.hexWidget.findEvent.connect(self.search)
	
		self.synccheck = QCheckBox("Sync")
		self.statusBar.addWidget(self.synccheck)
		
		self.selectstatus = QLabel("")
		self.statusBar.addWidget(self.selectstatus)
		
		self.statusBar.show()

	def structAtAddress(self,struct,address):
		print("define struct %s @ %08x" % (struct,address))
		self.structs.append((struct,address))
		self.refreshStructs()
		self.hexWidget.viewport().update()
				
	def refreshStructs(self):
		for (structn, address) in self.structs:
			s = self.api.structeditor.getStruct(structn);
			if s is not None:
				t = s.parse(self.filebuff[self.hexWidget.cursor._selection.start:self.hexWidget.cursor._selection.start+s.sizeof()])
				tally = 0
				for  i in s.subcons:
					self.hexWidget.addSelection(int(address+tally), int(address+tally + i.sizeof()),color=None,obj=("struct",structn,t,i))
					tally += i.sizeof()

	def contextEvent(self,event):
		menu = QMenu(self)		
		mnu = {} #fixme
		structmenu = QMenu("Structs")#this whole area uses variables slopily.. fixme	
		mnu["structs"] = menu.addMenu(structmenu)
	
		for n in self.api.structeditor.getStructList():
			mnu[n] = structmenu.addAction("Struct %s here" % n, lambda n = n: self.structAtAddress(n,self.hexWidget.cursor._selection.start))	
		
# 		for structs in self.pxToSelectionList(event.pos()):
# 			mnu[n] = menu.addAction("Delete struct %s" % structs.obj[2].name, lambda n = n: self.structAtAddress(n,self.cursor._selection.start))	
		
		menu.addSeparator()
		if len(self.hexWidget.cursor._selection):
			mnu['annotate'] = menu.addAction("Annotate Selection")

		pluginmenu = QMenu("Plugins")#this whole area uses variables slopily.. fixme	
		mnu["pluginmenu"] = menu.addMenu(pluginmenu)
	
		pluginmenus = {}
		for (n,fn) in self.api.listSelectionPlugins():
			pluginmenus['plugin_%s' % n] = pluginmenu.addAction("%s from selection" % n, lambda n = n, fn = fn: self.api.runPluginOnHexobj(n,fn, self))
		
		action = menu.exec_(self.mapToGlobal(event.pos()))
		if 'annotate' in mnu and action == mnu['annotate']:
			text, ok = QInputDialog.getText(self, 'Annotate', 'Note:')	
			if ok:
				self.hexWidget.addSelection(self.hexWidget.cursor._selection.start,self.hexWidget.cursor._selection.end, obj=("note",text), color=self.hexWidget.getNextColor())
		
	def maintainBookmarks(self, bookmarks):
# 		self.bookmarks.setRowCount(0)
		self.bookmarks.setRowCount(len(bookmarks))
		i = 0
		for s in bookmarks:
			(start,end) = s.getRange()
			qtw = QTableWidgetItem("0x%08x" % start)
			self.bookmarks.setItem(i,0, qtw)
			qtw.setBackground(QColor( s.color))
			qtw = QTableWidgetItem("0x%08x" % end)
			self.bookmarks.setItem(i,1, qtw)
			qtw.setBackground(QColor( s.color))

			if s.obj[0] == 'struct':
				(type, structname,parent,child) = s.obj
				qtw =  QTableWidgetItem(".".join([structname,child.name]) + " %s" % "")
				qtw.setBackground(QColor( s.color))
				self.bookmarks.setItem(i,2,qtw)
			elif s.obj[0] == 'note':
				(type, text) = s.obj
				qtw = QTableWidgetItem(text)
				qtw.setBackground(QColor( s.color))
# 				qtw.setStyleSheet("background-color: %s;" % s.color)
				self.bookmarks.setItem(i,2, qtw)
			i+=1
			
	def undo(self,selection):
		(start,end) = selection.getRange()
		self.filebuff.undo()		
		self.hexWidget.cursor.updateSelection(Selection(start, start))
		self.hexWidget.viewport().update()

	def redo(self,selection):
		self.filebuff.redo()		
		self.hexWidget.viewport().update()

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
		if self.clipboarcopy == hash(cb.text()):
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
		self.clipboarcopy  = hash(t)
		cb.setText(t, mode=cb.Clipboard)
		self.hexWidget.viewport().update()
		
		
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
# 		self.le = QLineEdit()
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
			addr = int(self.le1.text().replace("0x",""),16)
		elif self.btn1.isChecked():
			
			addr = int(self.le1.text())
		self.parent.goto(addr)
						
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
		if index >= 0:
			self.api.openFiles[self.filename].goto(index)
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

