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
#     with this program; if not, write to the Free Soft gware Foundation, Inc.,
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
# from math import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import string
import importlib
import construct
from encodings.aliases import aliases
import argparse
# from matplotlib.pyplot import *

# own submodules
from hexdialog import *
from ipythonwidget import *
from cursor import *
# from docks import *
import traceback
#from mmapslice import *


CLIPBOARD_MODE_RAW				=0
CLIPBOARD_MODE_CHEX				=1
CLIPBOARD_MODE_HEX_STRING		=2

CLIPBOARD_CONVERT_TO = [
	("RAW", lambda x : "".join([chr(y) if chr(y) in string.printable else ' ' for y in x])),
	("C-Hex",lambda x : "".join(["\\x%02x" % y for y in x])),
	("Hex string",lambda x : " ".join(["%02x" % y for y in x])),
]

CLIPBOARD_CONVERT_FROM = [
	("RAW",lambda x : bytearray([y for y in x])),
	("C-Hex",lambda x: bytearray([ord(y) for y in x.decode('unicode_escape')])),
	("Hex string",  lambda x : bytearray([int(y,16) for y in x.split()])),
]


class StructEditor(QTextEdit):
	structChanged = pyqtSignal(object)
	def __init__(self, api):
		super(StructEditor, self).__init__()
		self.api = api
		self.structs = {}
		self.setStructOk()
		self.setMinimumWidth(300)
		self.structbuff = ""
		self.refreshStructBuff()

	def widgetfunc(self):
		return ("Struct Editor","Alt+S",self)
			
	def setStructOk(self):
		self.setStyleSheet("background-color: rgb(232, 255, 232); color: rgb(0, 0, 0);")#green
		
	def setStructBad(self):
		self.setStyleSheet("background-color: rgb(255, 232, 232);color: rgb(0, 0, 0)")#red
	
	def contextMenuEvent(self, event):
		menu = QMenu()
		mnu = {} #fixme
		mnu["save"] = menu.addAction("Save Struct File", self.saveStructFile)	
		mnu["load"] = menu.addAction("Load Struct File", self.loadStructFile)		
		mnu["load"] = menu.addAction("Evaluate Structs", self.evalStructFile)		
		action = menu.exec_(self.mapToGlobal(event.pos()))

	def getStruct(self,name):
		return self.structs[name]
		
	def getStructList(self):
		return [x for x,y in self.structs.items()]
		
	def refreshStructBuff(self):
		if self.structbuff != self.toPlainText():
			self.structbuff = self.toPlainText()
			self.structChanged.emit(self.structbuff)
			
	def evalStructFile(self):
		self.items = []
		ns = {}
		self.refreshStructBuff()
		try:
			exec(compile("from construct import *\n" + self.structbuff, '<none>', 'exec'), ns)
			results = []
			self.structs = {}
			for name in sorted([x for x, v in ns.items() if isinstance(v, construct.Construct) and (x not in dir(construct)) ], key=self.foo):
				cons = ns[name]
				self.structs[name] = cons
			self.setStructOk()
		except:
			self.setStructBad()
			print(dir(traceback))
			traceback.print_exc()
			
		print (self.structs)

	def loadStructFile(self):
		self.filename = QFileDialog.getOpenFileName(self, "Load Struct defs From...")[0]
		if self.filename:
			f = open(self.filename, "rb")
			self.structbuff = f.read().decode("utf-8")
			self.setText(self.structbuff)
			f.close()
		self.evalStructFile()
			
	def saveStructFile(self):
		self.filename = QFileDialog.getSaveFileName(self, "Save Struct defs as...")[0]
		self.refreshStructBuff()
		if self.filename:
			f = open(self.filename, "wb")
			f.write(bytearray(self.structbuff,'utf-8'))
			f.close()

	def foo(self, x): #fixme
		try:
			y = ("\n" + self.structbuff).index("\n" + x)
		except:
			print( x)
			raise
		return y
		
		
					

class HaxeAPI(QObject):
	activeWindowChanged = pyqtSignal(object)
	structChanged = pyqtSignal(object)
	structStatusChanged = pyqtSignal(object)
	pluginLoadEvent = pyqtSignal(object)
	pluginUnLoadEvent = pyqtSignal(object)
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
		self.modules = {}
		self.loaded_plugins = {}
		self.scanPlugins()
		self.startPlugins()
		self.settings = QSettings("phar", "haxe hex editor")
		self.structeditor = StructEditor(self)
		
	def getConverters(self):
		return(CLIPBOARD_CONVERT_FROM,CLIPBOARD_CONVERT_TO)
	
	def pluginSinCallstack(self):
		self.log("-------BEGIN PLUGIN_SIN-------")
		traceback.print_exc()
		self.log("-------END PLUGIN_SIN-------")


	def runPluginOnHexobj(self,fn, hexobj):
		try:
			fn(hexobj)
		except:
			self.pluginSinCallstack()

	def scanPlugins(self):
		self.modules = {}
		fl = glob.glob(os.path.join("plugins","*.py"))
		for f in fl:
			try:
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
			except:
				self.log("failed to load plugin from file %s due to errors" % f)
				self.pluginSinCallstack()
				
	def listSelectionPlugins(self):
		ns = []
		for n,m in self.loaded_plugins.items():
			for pn, pf in m.pluginSelectionPlacement():
				ns.append((pn,pf))	
		return ns
						
	def startPlugins(self):
		print(self.modules)
		for n,m in self.modules.items():
			try:
				self.loaded_plugins[n] = m(self)
				self.loaded_plugins[n].start()
				self.pluginLoadEvent.emit(self.loaded_plugins[n])
			except:
				print("failed to start plugin %s" % n)
				self.pluginSinCallstack()


	def unloadPlugin(self, n):
		if n in loaded_plugins:
			try:
				self.loaded_plugins[n].stop()
				del(self.loaded_plugins[n])
				self.pluginUnLoadEvent.emit(self.loaded_plugins[n])
			except:
				print("failed to stop plugin %s" % n)
				traceback.print_exc()

	def reloadPlugins(self):
		self.stopPlugins()
		self.startPlugins()
		
	def stopPlugins(self):
		for n,p in self.loaded_plugins.items():
			self.unloadPlugin(n)
			
	def getCopyMode(self):
		return self.copy_mode
		
	def getPasteMode(self):
		return self.paste_mode

	def getCopyModeFn(self):
		return CLIPBOARD_CONVERT_TO[self.copy_mode][1]
		
	def getPasteModeFn(self):
		return CLIPBOARD_CONVERT_FROM[self.paste_mode][1]

	def getPasteModeFnbyName(self,mode):
		for i in range(len(CLIPBOARD_CONVERT_FROM)):
			if  CLIPBOARD_CONVERT_FROM[i][0] == mode:	
				return CLIPBOARD_CONVERT_FROM[i][1]
		return None
		
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
			self.api.log("Saving...")
# 			open(self.filename, 'wb').write(self.data)
			self.api.log("done.")
			pass

	def saveFile(self):
		self.filename = QFileDialog.getSaveFileName(self, "Save File as...")[0]
		if self.filename:
			self.api.log("Saving...")
			try:
# 				self.statusBar().showMessage("wrote %s done." % self.filename)
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Save confirm.")
				msg.setInformativeText("Are you really sure you want to save to the existing file?")
				msg.setWindowTitle("Confirm Operation")
				msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
				retval = msg.exec_()		
				if retval == QMessageBox.Ok:
					self.api.log("save confirmed.")
					raise("FIXME")
					self.api.log("save done.")

			except:
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Save Failed.")
				msg.setInformativeText("This is probably because you dont have permissions to write to the file.")
				msg.setWindowTitle("Critical Error")
				msg.setStandardButtons(QMessageBox.Ok)
				self.api.log("save failed.")
				retval = msg.exec_()		
		

	def find(self, filename, findval, selection=None):
		print("yep here2")
		return  self.openFiles[filename].find(findval, selection)
 		
	def findAll(self, filename, findval, selection=None):	
		return  self.openFiles[filename].findAll(findval, selection)
		
	def openFile(self, filename):
		try:
			self.openFiles[filename] =  FileBuffer(filename)
			return filename
		except:
			pass #fixme
			return None
				
	def log(self, logmsg):
		print(logmsg)
# 		self.qtparent.statusBar().showMessage(logmsg) 

	def getActiveFocus(self):
		if  self.activefocusfilename != None:
			return self.activefocusfilename
		else:
			return next(iter(self.openFiles.values()))
			
	def setActiveFocus(self,filename):
		if filename in self.openFiles:
			self.activefocusfilename = filename
			self.activeWindowChanged.emit(filename)
		
	def setCopyMode(self,mode):
		self.copy_mode = mode
		
	def setPasteMode(self,mode):
		self.paste_mode = mode	
	
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
		self.recentfiles = []

		self.font = QFont("Courier", 10)
		self.createToolbar()
		self.docks = {}
		self.createActions()
		self.createMenus()

		self.loadiPythonEnvironment("ipython.env")

		(name, dock, window, action, shortcut) = self.createDock(self.api.structeditor.widgetfunc)
		self.docks[name] = {'dock':dock, 'window':window,'action':action,'shortcut':shortcut}		
		self.viewmenu.addAction(self.docks[name]['action'])
 		
		(name, dock, window, action, shortcut) = self.createDock(self.iPuthonWindow)
		self.docks[name] = {'dock':dock, 'window':window,'action':action,'shortcut':shortcut}		
		self.viewmenu.addAction(self.docks[name]['action'])
		
		self.drawIcon()
# 		self.api.structChanged.connect(self.structChanged);
	
		self.open_file(args.filename)
		self.setAcceptDrops(True)
		self.loadSettings()
		self.loadRecentFiles()
	

	def dragEnterEvent(self, e):
		if e.mimeData().hasText():#only accept files that i can opn
			t = e.mimeData().text() 
			if t[:7] == 'file://' and os.path.exists(t[7:]):
				e.accept()
			else:
				e.ignore()
		else:
			e.ignore()

	def dropEvent(self, e):
		fn = e.mimeData().text()[7:]
		print("drag",fn)      	
		self.open_file(fn)
	
	

	def newHexDock(self, filebuff=None):
		tab = QDockWidget()
		if filebuff == None:
			filebuff = FileBuffer()
		
		tab.setWindowTitle(filebuff.filename)
		hw = HexDialog(self.api,self,filebuff)
		tab.setWidget(hw)
		tab.setAllowedAreas(Qt.AllDockWidgetAreas)
		self.tabs.append(tab)
		self.central.addDockWidget(Qt.RightDockWidgetArea, tab)
		
	def open_file(self, filename=None):
		print(filename)
		if filename in [None, False]:
			filename = QFileDialog.getOpenFileName(self, "Open File...")[0]
		if filename:
			hw = self.api.openFile(filename)
			if hw != None:
				self.pushRecentFiles(filename)
				self.newHexDock(self.api.openFiles[filename])	#fixme	
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


	def loadSettings(self):
		txt = self.api.settings.value("%s.copymode")
		index = self.cb.findText(txt, Qt.MatchFixedString)
		if index >= 0:
			self.cb.setCurrentIndex(index)
		txt = self.api.settings.value("%s.pastemode")
		index = self.pm.findText(txt, Qt.MatchFixedString)
		if index >= 0:
			self.pm.setCurrentIndex(index)
         
	def saveSettings(self):
		self.api.settings.setValue("%s.copymode",self.cb.currentText())
		self.api.settings.setValue("%s.pastemode",self.pm.currentText())
		self.api.settings.setValue("geometry", self.saveGeometry())
		self.api.settings.setValue("windowState", self.saveState())
		self.saveRecentFiles()

	def closeEvent(self, event):
		self.saveSettings()
		QMainWindow.closeEvent(self, event)

	def createToolbar(self):
		tb = self.addToolBar("Toolbar")
		
		l = QLabel("Copy Mode:")
		self.cb = QComboBox()
		for nf in CLIPBOARD_CONVERT_TO:
			(n,f) = nf
			self.cb.addItem(n)			
		tb.addWidget(l)
		tb.addWidget(self.cb)
		
		l = QLabel("Paste Mode:")
		self.pm = QComboBox()
		for nf in CLIPBOARD_CONVERT_FROM:
			(n,f) = nf
			self.pm.addItem(n)	
		tb.addWidget(l)
		tb.addWidget(self.pm)

# 		l = QLabel("Text Encoding:")
# 		self.enc = QComboBox()
# 		self.enc.addItems(aliases)			
# 		self.enc.setCurrentIndex(self.enc.findText('utf8', QtCore.Qt.MatchFixedString))			
# 		tb.addWidget(l)
# 		tb.addWidget(self.enc)
		self.cb.currentIndexChanged.connect(self.copy_mode)
		self.pm.currentIndexChanged.connect(self.paste_mode)

	def copy_mode(self,arg):
		self.api.setCopyMode(arg)
			
	def paste_mode(self,arg):
		self.api.setPasteMode(arg)

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

		self.act_openrecent = QAction("Open Recent", self)
		self.act_openrecent.setStatusTip("Open Re")
		self.act_openrecent.triggered.connect(self.open_recent)



		self.act_new = QAction("&New", self)
		self.act_new.setShortcuts(QKeySequence.New)
		self.act_new.setStatusTip("New file...")
		self.act_new.triggered.connect(self.new_file)


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


		self.act_import = QAction("Import", self)
		self.act_import.setStatusTip("Import Plugins")
		# 		self.act_import.triggered.connect(self.save_file_as)

		self.act_export = QAction("Export", self)
		self.act_export.setStatusTip("Export Plugins")
		# 		self.act_export.triggered.connect(self.save_file_as)

		self.act_quit = QAction("&Quit", self)
		self.act_quit.setShortcuts(QKeySequence.Quit)
		self.act_quit.setStatusTip("Quit HAxe")
		self.act_quit.triggered.connect(self.close)


	def loadRecentFiles(self):
		self.recentfiles = []
		for i in range(10):
			txt = self.api.settings.value("recent.%d" % i)
			if txt != None:
				self.pushRecentFiles(txt)	

	def pushRecentFiles(self,fn):
		if fn not in self.recentfiles:
			self.recentfiles.append(fn)	
			recentact  = QAction(fn,self)	
			print(fn)	
			recentact.triggered.connect(lambda state, x=fn: self.open_file(filename=x) )
			self.recentmenu.addAction(recentact)		


	def saveRecentFiles(self):
		for i,fn in enumerate(self.recentfiles):
			self.api.settings.setValue("recent.%d" % i,fn)

	def new_file(self):
		self.api.qtparent.newHexDock()

	def revert_file(self):
		pass
		
	def open_recent(self):
		pass
	
	def createMenus(self):
		self.filemenu = self.menuBar().addMenu("&File")

		self.filemenu.addAction(self.act_open)
		self.recentmenu = self.filemenu.addMenu("Recent Files")
		self.filemenu.addSeparator()
		self.filemenu.addAction(self.act_new)
		self.filemenu.addAction(self.act_save)
		self.filemenu.addAction(self.act_saveas)
		self.filemenu.addAction(self.act_revert)
		self.filemenu.addSeparator()
		self.filemenu.addAction(self.act_import)
		self.filemenu.addAction(self.act_export)
		self.filemenu.addSeparator()
		self.filemenu.addAction(self.act_quit)
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
# 	h.api.loadStructFile()
	h.show()
# 	h.api.evalStructFile()
	app.exec_()
