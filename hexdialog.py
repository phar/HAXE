import mmap
import os
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
		mnu["remove"] = menu.addAction("Remove Bookmarks", self.delBookmarks)			
		mnu["clear"] = menu.addAction("Clear Bookmarks", self.clarBookmarks)			
		action = menu.exec_(self.mapToGlobal(event.pos()))

	def delBookmarks(self):
		pass

	def clarBookmarks(self):
		pass

	def maintainBookmarks(self, bookmarks):
		self.setRowCount(len(bookmarks))
		i = 0
		for s in bookmarks:
			(start,end) = s.getRange()
			qtw = QTableWidgetItem("0x%08x" % start)
			qtw.setForeground(QColor(hexColorComplement( s.color)))
			self.setItem(i,0, qtw)
			qtw.setBackground(QColor( s.color))
			qtw = QTableWidgetItem("0x%08x" % end)
			qtw.setForeground(QColor(hexColorComplement(s.color)))
			self.setItem(i,1, qtw)
			qtw.setBackground(QColor( s.color))
			qtw.setForeground(QColor(hexColorComplement( s.color)))

# 			if s.obj[0] == 'struct':
# 				(type, structname,parent,child) = s.obj
# 				qtw =  QTableWidgetItem(".".join([structname,child.name]) + " %s" % "")
# 				qtw.setBackground(QColor( s.color))
# 				qtw.setForeground(QColor(hexColorComplement( s.color)))
# 				self.setItem(i,2,qtw)
# 			elif s.obj[0] == 'note':
# 				(type, text) = s.obj
			qtw = QTableWidgetItem(s.obj.labelAction())
			qtw.setBackground(QColor(s.color))
			qtw.setForeground(QColor(hexColorComplement(s.color)))
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
		self.clipboarcopy = [] #fixme, replace with hash
		self.isActiveWindow = False
		self.hexWidget =  HexWidget(api,self,self.filebuff, font="Courier", fontsize=12)
		splitter1 = QSplitter(Qt.Horizontal)	
		self.setCentralWidget(splitter1)
		splitter1.addWidget(self.hexWidget)
			
		self.bookmarks  = BookmarkWidget(self)
		self.hexWidget.updateSelectionListEvent.connect(self.bookmarks.maintainBookmarks)
		
		splitter1.addWidget(self.hexWidget)
		splitter1.addWidget(self.bookmarks)
		splitter1.setOrientation( Qt.Vertical)
		splitter1.setSizes((-1,0))
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
		self.hexWidget.jumpToEvent.connect(self.jumpto)
		self.hexWidget.findEvent.connect(self.search)
	
		self.synccheck = QCheckBox("Sync")
		self.statusBar.addWidget(self.synccheck)
		
		self.selectstatus = QLabel("")
		self.statusBar.addWidget(self.selectstatus)
		
		self.filestatus = QLabel("Welcome to HAxe")
		self.statusBar.addWidget(self.filestatus)
		
		self.filestatus.setAlignment(QtCore.Qt.AlignRight)
		self.statusBar.show()
		self.blink = False
		self.blinkstate = 0
		self.lastblink = 0
		self.startCursor(500)

	def startCursor(self,interval=500):
		# cursor blinking timer
		self.cursorTimer = QTimer()
		self.cursorBlinkInterval = interval
		self.cursorTimer.timeout.connect(self.updateCursor)
		self.cursorTimer.setInterval(interval)
		self.cursorTimer.start()

	def updateCursor(self):
# 		self.blink = not self.blink
		self.blinkstate += 1
		self.hexWidget.repaintWidget()

	def getSelection(self):
		return self.hexWidget.getCursor().getSelection()

	def jumpto(self,selection):
		f  = JumpToDialog(self,self.api)
		f.show()
					
	def contextEvent(self,event):
		menu = QMenu(self)		
	
		pluginmenus = {}
		for n,m in self.api.loaded_plugins.items():
			for pn, pf in m.pluginSelectionPlacement():
# 				try:
					sm =  m.pluginSelectionSubPlacement()
					if len(sm):
						submenu = QMenu(pn)		
						menu.addMenu(submenu)
						for spn, spf in  m.pluginSelectionSubPlacement():
							if spf != None:
								pluginmenus['plugin_%s' % n] = submenu.addAction("%s" % spn, lambda n = spn, fn = spf: fn(self))
							else:
								submenu.addSeparator()
					else:
						pluginmenus['plugin_%s' % n] = menu.addAction("%s" % pn, lambda n = pn, fn = pf: fn(self))
# 				except:
# 					self.api.pluginSinCallstack()

		
		action = menu.exec_(self.mapToGlobal(event.pos()))

		
	def maintainBookmarks(self, bookmarks):
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
			qtw = QTableWidgetItem(s.obj.labelAction())
			qtw.setBackground(QColor( s.color))
			self.bookmarks.setItem(i,2, qtw)
			i+=1
			
	def undo(self,selection):
		(start,end) = selection.getRange()
		self.filebuff.undo()		
		self.hexWidget.cursor.updateSelection(Selection(start, start))

	def redo(self,selection):
		self.filebuff.redo()		

	def search(self):
		self.dia = SearchDialog(self)
		self.dia.show()
		self.dia.raise_()
		self.dia.activateWindow()
		      	
	def getCursor(self):
		return self.hexWidget.getCursor()
		      	
	def addSelection(self,selection):
		self.hexWidget.addSelection(selection)
		      	
	def getSelection(self):
		start,end = self.hexWidget.getSelection().getRange()
		return Selection(start,end)

# 	def getNewSelectionfromSelection(self):
# 		return self.hexWidget.getSelection()

      	
	def select_changed(self,selection):
		(start,end) = selection.getRange()
		if len(selection):
			self.selectstatus.setText(" [%d bytes selected at offset 0x%x out of %d bytes]" % (len(selection), start, len(self.filebuff)))
		else:
			self.selectstatus.setText(" [offset 0x%x (%d) of %d bytes]" % (start,start, len(self.filebuff)))
# 		self.selectstatus.repaint()

		self.filestatus.setText(self.filebuff.statusString() + "[%s]" %self.hexWidget.charset)
	

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
		
	def edit(self,tup):
		(selection,edit) = tup
		self.filebuff.addEdit(selection,edit)

	def paste(self,selection):
		cb = QApplication.clipboard()
		try:
			if self.clipboarcopy == hash(cb.text()):
				t = self.clipboardata	
			else:
				t = cb.text().encode("utf-8")
				t = self.api.getPasteModeFn()(t)
						
			print(t)
			self.filebuff.addEdit(selection, t)
			(start,end) = self.hexWidget.cursor._selection.getRange()
			self.hexWidget.goto(start)
			self.hexWidget.cursor.updateSelection(Selection(start, start + len(t)))
		except:
			print("somthing has gone wrong in the paste translation system")
	
	def copy(self,slection):
		(start,end)  = self.hexWidget.cursor._selection.getRange()
		t = self.filebuff[start:end]			
		self.clipboardata = t
		cb = QApplication.clipboard()
		t = self.api.getCopyModeFn()(t)
		self.clipboarcopy  = hash(t)
		cb.setText(t, mode=cb.Clipboard)
		
		
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
		self.setWindowTitle("Jump to Offset")
		self.loadSettings()

	def dook(self):
		addr = 0
		if self.btn.isChecked():
			try:
				addr = int(self.le1.text().replace("0x",""),16)
			except:
				pass
		elif self.btn1.isChecked():
			try:				
				addr = int(self.le1.text())
			except ValueError:
				return
		self.parent.hexWidget.goto(addr) #fixme
						
	def doclose(self):
		self.close()

	def loadSettings(self):
		txt = self.api.settings.value("jumpto.address")
		if txt != None:
			self.le1.setText(txt)	
		txt = self.api.settings.value("jumpto.format")
		if  self.api.settings.value("jumpto.format") == "hex":
			self.btn.setChecked(True)
		else:
			self.btn1.setChecked(True)
         
	def saveSettings(self):
		self.api.settings.setValue("jumpto.address",self.le1.text())
		
		if self.btn.isChecked():
			self.api.settings.setValue("jumpto.format",'hex')
		else:
			self.api.settings.setValue("jumpto.format",'decimal')

	def closeEvent(self,event):
			self.saveSettings()


class FindAllDialog(QDialog):
	def __init__(self, po=None,parent=None):
		super(FindAllDialog, self).__init__(parent)
		self.lyt = QGridLayout()
		self.setLayout(self.lyt)
		self.parent = po
# 		self.api = api




class SearchDialog(QDialog):
	def __init__(self, po=None,parent=None):
		super(SearchDialog, self).__init__(parent)
		self.lyt = QGridLayout()
		self.setLayout(self.lyt)
		self.parent = po
# 		self.api = api
		self.searchline = QLineEdit()
		self.replaceLine = QLineEdit()
		
		self.searchlinel = QLabel("Search")
		self.pb_searchn = QPushButton("Find Next")
		self.pb_searchn.clicked.connect(self.find_next)
		self.pb_searchp = QPushButton("Find Prev")
		self.pb_searchp.clicked.connect(self.find_prev)
		self.pb_searcha = QPushButton("Find All")
		self.pb_searchp.clicked.connect(self.find_all)
		self.pb_replacen = QPushButton("Replace")
		self.pb_replacea = QPushButton("Replace All")
		self.pb_replace= QLabel("Replace")

		self.lyt.addWidget(self.searchlinel, 0,0,1,1)
		self.lyt.addWidget(self.searchline, 0, 1,1,2)

		self.lyt.addWidget(self.pb_replace, 1,0,1,1)# 
		self.lyt.addWidget(self.replaceLine, 1, 1,1,2)

		self.pm = QComboBox()
		for nf in self.parent.api.getConverters()[0]:
			(n,f) = nf
			self.pm.addItem(n)	
			
		self.lyt.addWidget(self.pm, 0, 3)

		self.lyt.addWidget(self.pb_searchn, 2, 1)
		self.lyt.addWidget(self.pb_searchp, 2, 0)
		self.lyt.addWidget(self.pb_replacen, 2, 2)
		self.lyt.addWidget(self.pb_replacea, 2, 3)
		self.loadSettings()
		
	def getsearchvalue(self):	
		ret = self.parent.api.getPasteModeFnbyName(self.pm.currentText())(bytearray(self.searchline.text(),"UTF-8"))
		return ret

	def find_all(self):
		pass

	def find_next(self):	
		searchval = self.getsearchvalue()
		self.parent.hexWidget.getCursor().selectNone()		
		x = self.parent.filebuff.findNext(searchval, self.parent.hexWidget.getCursor())		
		print(x)
			
		if x >= 0:
			self.parent.hexWidget.getCursor().setSelection(Selection(x, x+len(searchval)))
		else:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setText("The search term was not found")
			msg.setInformativeText("Not found")
			msg.setWindowTitle("find next")
			msg.setStandardButtons(QMessageBox.Ok)
			retval = msg.exec_()	

	def find_prev(self):	
		searchval = self.getsearchvalue()
		self.parent.hexWidget.getCursor().selectNone()		
		x = self.parent.filebuff.findPrev(searchval, self.parent.hexWidget.getCursor())		
		print(x)
					
		if x >= 0:
			self.parent.hexWidget.getCursor().setSelection(Selection(x, x+len(searchval)))
		else:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setText("The search term was not found")
			msg.setInformativeText("Not found")
			msg.setWindowTitle("find next")
			msg.setStandardButtons(QMessageBox.Ok)
			retval = msg.exec_()	
				
	def loadSettings(self):
		pass
         
	def saveSettings(self):
		pass
		
	def closeEvent(self,event):
			self.saveSettings()
			