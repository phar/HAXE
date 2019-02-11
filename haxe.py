#     PyQt hex editor widget
#     Copyright (C) 2015 Christoph Sarnowski

#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License along
#     with this program; if not, write to the Free Software Foundation, Inc.,
#     51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# standard modules
import time
import mmap
import re
import os
import collections
import numpy as np
import inspect
import logging
import glob
from binascii import *
from math import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import string
import importlib
import construct
from encodings.aliases import aliases

import argparse
from matplotlib.pyplot import *
import binwalk
# # %matplotlib inline

# own submodules
from hexwidget import *
from ipythonwidget import *
from cursor import *
from docks import *
#from mmapslice import *



CLIPBOARD_MODE_RAW				=1
CLIPBOARD_MODE_ASCII_ISPRINT	=2
CLIPBOARD_MODE_ASCII_ONLY		=3
CLIPBOARD_MODE_CHEX				=4
CLIPBOARD_MODE_CHEX_ISPRINT		=5
CLIPBOARD_MODE_HEX_STRING		=6




CLIPBOARD_CONVERT_TO = {
	CLIPBOARD_MODE_RAW : ("RAW", lambda x : bytearray([y if chr(y) in string.printable else 0x20 for y in x])),
	CLIPBOARD_MODE_CHEX : ("C-Hex",lambda x : "".join(["\\x%02x" % y for y in x])),
	CLIPBOARD_MODE_HEX_STRING : ("Hex string",lambda x : " ".join(["%02x" % y for y in x])),
}

CLIPBOARD_CONVERT_FROM = {
	CLIPBOARD_MODE_RAW : ("RAW",lambda x : bytearray([y for y in x])),
	CLIPBOARD_MODE_CHEX_ISPRINT : ("C-Hex",lambda x: bytearray([y for y in x.decode('unicode_escape')])),
	CLIPBOARD_MODE_HEX_STRING : ("Hex string",  lambda x : bytearray([int(y,16) for y in x.split()])),
}


class Delegate(QItemDelegate):
    def __init__(self):
        super(Delegate, self).__init__()
        self.validator = QIntValidator()

    def setModelData(self, editor, model, index):
        print (editor, model, index)
        editor = QLineEdit(editor)
        editor.setValidator(self.validator)
        super(Delegate, self).setModelData(editor, model, index)



class HaxeAPI(QObject):
	activeWindowChanged = pyqtSignal(object)
	structChanged = pyqtSignal(object)
	structStatusChanged = pyqtSignal(object)
	def __init__(self, parent):
		super(HaxeAPI, self).__init__(parent)
		self.activefocusfilename = None
		self.openFiles = {}
		self.hexdocks = {}
		self.qtparent = parent
		self.copy_mode = CLIPBOARD_MODE_RAW
		self.paste_mode = CLIPBOARD_MODE_RAW
		self.structfile = None
		self.structbuff = ""
		self.structs = {}
		self.modules = {}
		self.reloadPlugins()
		
		
	def reloadPlugins(self):
		self.modules = {}
		fl = glob.glob(os.path.join("plugins","*.py"))
		for f in fl:
			a = importlib.import_module(".".join(os.path.split(".".join(f.split(".")[:-1]))))	
			for cn in dir(a):
				c  = getattr(a,cn)
				if inspect.isclass(c):
					is_plugin_class = False
					for base in c.__bases__:
						if (base.__name__ == 'HexPlugin'):
							is_plugin_class = True
					if is_plugin_class:
						print("found plugin class \"%s\"" % cn)
						self.modules[cn] = c	
		
	def getCopyMode(self):
		return self.copy_mode
		
	def getPasteMode(self):
		self.paste_mode

	def getCopyModeFn(self):
		return CLIPBOARD_CONVERT_TO[self.copy_mode][1]
		
	def getPasteModeFn(self):
		return CLIPBOARD_CONVERT_FROM[self.paste_mode][1]

		
	def isActiveWindow(self,filename):
		return self.activefocusfilename == filename

	def listOpenFiles(self):
		return [x for x,y in self.openFiles.items()]

	def getBytes(self,file,range=(0,None)):
		(start,stop) = range
		if stop == None:
			stop == len(self.openFiles[file].data)
		return self.openFiles[file].data[start:stop] 

	def getSelectedRange(self,file):
		return self.openFiles[file].selection.getRange()
	
	def getSelectedBytes(self,file):
		(start,stop) = self.getSelectedRange(file)
		return self.openFiles[file].data[start:stop] 

	def patchBytes(self,file,range=(0,None), patch=b'', padchar=b'\x00'):
		(start,stop) = range
		if stop == None:
			return False
		self.openFiles[file].data[start:stop] = patch.ljust((stop-start),padchar)
		return True
		
	def histogram(self,file,range=(0,None)): #why is this so slow
		(start,stop) = range
		a  = np.ndarray.__new__(np.ndarray,
		   shape=(len(self.openFiles[file].data[start:stop]),),
		   dtype=np.uint8,
		   buffer=self.openFiles[file][start:stop],
		   offset=0,
		   strides=(1,),
		   order='C')
		hist(a, bins=256, range=(0,256), histtype='step')
				

	def saveFileAs(self):
		self.filename = QFileDialog.getSaveFileName(self, "Save File as...")[0]
		if self.filename:
			self.statusBar().showMessage("Saving...")
# 			open(self.filename, 'wb').write(self.data)
			self.statusBar().showMessage("done.")

	def saveFile(self):
		self.filename = QFileDialog.getSaveFileName(self, "Save File as...")[0]
		if self.filename:
			self.statusBar().showMessage("Saving...")
			try:
				self.statusBar().showMessage("wrote %s done." % self.filename)
			except:
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Save Failed.")
				msg.setInformativeText("This is probably because you dont have permissions to write to the file.")
				msg.setWindowTitle("Critical Error")
				msg.setStandardButtons(QMessageBox.Ok)
				self.statusBar().showMessage("save failed.")
				retval = msg.exec_()		
		

	def openFile(self, filename):
		self.openFiles[filename] =  FileBuffer(filename)
		return filename
			
	def log(self, logmsg):
		self.qtparent.statusBar().showMessage(logmsg) 


	def foo(self, x): #fixme
		try:
			y = ("\n" + self.structbuff).index("\n" + x)
		except:
			print( x)
			raise
		return y
		
	def getStructList(self):
		return [x for x,y in self.structs.items()]
			
	def evalStructFile(self):
		self.items = []
		ns = {}
		exec(compile("from construct import *\n" + self.structbuff, '<none>', 'exec'), ns)
		results = []
		self.structs = {}
		for name in sorted([x for x, v in ns.items() if isinstance(v, construct.Construct) and (x not in dir(construct)) ], key=self.foo):
			cons = ns[name]
			self.structs[name] = cons

	def closeEvent(self, event):

		settings = QSettings("phar", "haxe hex editor")
		settings.setValue("geometry", self.saveGeometry())
		settings.setValue("windowState", self.saveState())
		QMainWindow.closeEvent(self, event)


	
	def getActiveFocus(self):
		return self.activefocusfilename
		
	def setActiveFocus(self,filename):
		if filename in self.openFiles:
			self.activefocusfilename = filename
			self.activeWindowChanged.emit(filename)
		
	def setCopyMode(self,mode):
		self.copy_mode = mode
		
	def setPasteMode(self,mode):
		self.paste_mode = mode	
	
	def loadStructFile(self, filename="demostruct.txt"):
		f = open(filename)
		self.structfile = filename
		self.structbuff = f.read()
		self.evalStructFile()
		self.structChanged.emit(filename)

	def saveStructFile(self,filename):
		f = open(filename)
		f.write(self.structbuff)
		f.close()

	

class HaxEditor(QMainWindow):
	def __init__(self):
		super(HaxEditor, self).__init__()
		self.setWindowTitle("HAxe Hex Editor")
		self.api = HaxeAPI(self);

		self.central = QMainWindow()
		self.central.setWindowFlags(Qt.Widget)
		self.central.setDockOptions(self.central.dockOptions()|QMainWindow.AllowNestedDocks)
		self.tabs = []
		self.setCentralWidget(self.central)
		
		self.font = QFont("Courier", 10)
		self.createToolbar()
		self.docks = {}
		self.createActions()
		self.createMenus()

		self.loadiPythonEnvironment("ipython.env")

		(name, dock, window, action, shortcut) = self.createDock(self.structExplorerWindow)
		self.docks[name] = {'dock':dock, 'window':window,'action':action,'shortcut':shortcut}				
		self.viewmenu.addAction(self.docks[name]['action'])
		
		(name, dock, window, action, shortcut) = self.createDock(self.structEditorWindow)
		self.docks[name] = {'dock':dock, 'window':window,'action':action,'shortcut':shortcut}		
		self.viewmenu.addAction(self.docks[name]['action'])
		
		(name, dock, window, action, shortcut) = self.createDock(self.iPuthonWindow)
		self.docks[name] = {'dock':dock, 'window':window,'action':action,'shortcut':shortcut}		
		self.viewmenu.addAction(self.docks[name]['action'])
		
	
		
		self.drawIcon()
		self.api.structChanged.connect(self.structChanged);
	
		self.open_file(args.filename)

	
	
	def structChanged(self):
# 		self.structeditor.setText(self.api.structbuff)			
		pass		
		
	def newHexDock(self, filebuff):
		tab = QDockWidget()
		tab.setWindowTitle(filebuff.filename)
		hw = HexDialog(self.api,self,filebuff)
		tab.setWidget(hw)
		tab.setAllowedAreas(Qt.AllDockWidgetAreas)
		self.tabs.append(tab)
		self.central.addDockWidget(Qt.RightDockWidgetArea, tab)
		
	def open_file(self, filename=None):
		if filename in [None, False]:
			filename = QFileDialog.getOpenFileName(self, "Open File...")[0]
		if filename:
			hw = self.api.openFile(filename)
# 			self.cursor
			self.newHexDock(self.api.openFiles[filename])		
		else:
			pass #i dont know what to do with this
				

	def drawIcon(self):
		self.pixmap = QPixmap(64,64)  #lol, thats fucking adorable.. im tempted to keep this
		painter = QPainter(self.pixmap)
		painter.fillRect(0,0,64,64,Qt.green)
		painter.setPen(QColor(192,0,192))
		painter.setFont(QFont("Courier", 64))
		painter.drawText(6,57,"H")
		
		self.icon = QIcon(self.pixmap)
		self.setWindowIcon(self.icon)


	def createToolbar(self):
		tb = self.addToolBar("Toolbar")
		l = QLabel("Copy Mode:")
		self.cb = QComboBox()
		for v,nf in CLIPBOARD_CONVERT_TO.items():
			print(nf)
			(n,f) = nf
			self.cb.addItem(n,v)	
				
		tb.addWidget(l)
		tb.addWidget(self.cb)
		self.cb.currentIndexChanged.connect(self.copy_mode)

		l = QLabel("Paste Mode:")
		self.pm = QComboBox()
		for v,nf in CLIPBOARD_CONVERT_FROM.items():
			(n,f) = nf
			self.pm.addItem(n,v)	
			
		tb.addWidget(l)
		tb.addWidget(self.pm)

		l = QLabel("Text Encoding:")
		self.enc = QComboBox()
# 		for v,nf in aliases.items():
		self.enc.addItems(aliases)	
			
		self.enc.setCurrentIndex(self.enc.findText('utf8', QtCore.Qt.MatchFixedString))			
		tb.addWidget(l)
		tb.addWidget(self.enc)


		self.pm.currentIndexChanged.connect(self.paste_mode)

	def copy_mode(self,arg):
		self.api.setCopyMode(arg)
			
	def paste_mode(self,arg):
		self.api.setPasteMode(arg)


	def structEditorWindow(self):
		structeditor = QTextEdit()
		# qscintilla compatibility
		structeditor.text = structeditor.toPlainText
		structeditor.setText = structeditor.setPlainText
		structeditor.setStyleSheet("background-color: rgb(255, 232, 232);")#red
		structeditor.setFont(self.font)
		structeditor.setMinimumWidth(300)
		
		return ("Struct Editor","Alt+S",structeditor)
			
	def structExplorerWindow(self):
		structexplorer = QTreeWidget()
		structexplorer.setColumnCount(3)
		structexplorer.setMinimumWidth(300)
		
		return ("Struct Explorer", "Alt+X", structexplorer)

	def loadiPythonEnvironment(self, filename="ipython.env"):
		f = open(filename)
		self.ipythonenv = f.read()
		f.close()

	def iPuthonWindow(self):
		
		ipython = IPythonWidget(run=self.ipythonenv,main=self)
		ipython.setMinimumWidth(300)
		return  ("IPython","Alt+P",ipython)
		
	def createDock(self, widgetfunc):
		self.setDockOptions(self.dockOptions() | QMainWindow.AllowNestedDocks)
		allowed_positions = Qt.AllDockWidgetAreas
		
		(title, shortcut, window) = widgetfunc()
		dock1 = QDockWidget()
		dock1.setWindowTitle(title)
		dock1.setWidget(window)
		dock1.setAllowedAreas(allowed_positions)
		dock1.hide()

		self.addDockWidget(Qt.RightDockWidgetArea, dock1)		
		ed = dock1.toggleViewAction()
		ed.setShortcut(QKeySequence(shortcut))
		return (title,dock1,window,ed,shortcut)

	def createActions(self):
		self.act_open = QAction("&Open", self)
		self.act_open.setShortcuts(QKeySequence.Open)
		self.act_open.setStatusTip("Open file")
		self.act_open.triggered.connect(self.open_file)

		self.act_save = QAction("&Save ...", self)
		self.act_save.setShortcuts(QKeySequence.Save)
		self.act_save.setStatusTip("Save file...")
		self.act_save.triggered.connect(self.save_file)
		
		self.act_revert = QAction("Revert to saved", self)
		self.act_revert.setShortcuts(QKeySequence.Refresh)
		self.act_revert.setStatusTip("Revert to saved")
		self.act_revert.triggered.connect(self.revert_file)
				
		self.act_saveas = QAction("Save as...", self)
		self.act_saveas.setShortcuts(QKeySequence.SaveAs)
		self.act_saveas.setStatusTip("Save file as...")
		self.act_saveas.triggered.connect(self.save_file_as)

		self.act_quit = QAction("&Quit", self)
		self.act_quit.setShortcuts(QKeySequence.Quit)
		self.act_quit.setStatusTip("Quit HAxe")
		self.act_quit.triggered.connect(self.close)

# 		self.act_search = QAction("&Search", self)
# 		self.act_search.setShortcuts(QKeySequence.Find)
# 		self.act_search.setStatusTip("Search current buffer for a string")
# 		self.act_search.triggered.connect(self.search)



	def revert_file(self):
		pass
	
	def createMenus(self):
		self.filemenu = self.menuBar().addMenu("&File")
		self.filemenu.addAction(self.act_open)
		self.filemenu.addAction(self.act_save)
		self.filemenu.addAction(self.act_revert)
		self.filemenu.addAction(self.act_saveas)
		self.filemenu.addAction(self.act_quit)
# 		self.filemenu.addAction(self.act_search)
		self.viewmenu = self.menuBar().addMenu("&View")


	def toggle_structedit(self):
		if self.structeditor.isVisible():
			self.structeditor.setVisible(False)
		else:
			self.structeditor.setVisible(True)




	def save_file(self):
		self.api.openFiles[self.api.getActiveFocus()].saveFile()
		pass

	def save_file_as(self):
		pass



if __name__ == '__main__':
	app = QApplication([])
	

	parser = argparse.ArgumentParser()

	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
	parser.add_argument("-d", "--debug", help="debug output", action="store_true")
	parser.add_argument("-f", "--filename", help="filename") #fixme

	args = parser.parse_args()
	if args.verbose:
		print("verbosity turned on")


	h = HaxEditor()
	h.api.loadStructFile()
	h.show()
	h.api.evalStructFile()
	app.exec_()
