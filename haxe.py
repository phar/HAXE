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
import os
import collections
import numpy as np
import inspect
import logging
import glob
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import string
import importlib
import argparse
import codecs
import traceback

# own submodules
from hexdialog import *


CLIPBOARD_CONVERT_TO = [
	("RAW", lambda x : "".join([chr(y) if chr(y) in string.printable else ' ' for y in x])),
	("C-Hex",lambda x : "".join(["\\x%02x" % y for y in x])),
# 	("Hex string",lambda x : " ".join(["%02x" % y for y in x])),
	("Hex string",lambda x : "".join([chr(y) for y in codecs.encode(x,"hex")])),
	("Base64",lambda x : "".join([chr(y) for y in codecs.encode(x,"base64")])),
]


CLIPBOARD_CONVERT_FROM = [
	("RAW",lambda x : bytearray([y for y in x])),
	("C-Hex",lambda x: bytearray([ord(y) for y in x.decode('unicode_escape')])),
# 	("Hex string",  lambda x : bytearray([int(y,16) for y in x.split()])),
	("Hex string",lambda x: bytearray([y for y in codecs.decode(x,'hex')])),
	("Base64",lambda x: bytearray([y for y in codecs.decode(x,'base64')])),
]

					

class HaxeAPI(QObject):
	activeWindowChanged = pyqtSignal(object)
	structChanged = pyqtSignal(object)
	structStatusChanged = pyqtSignal(object)
	pluginLoadEvent = pyqtSignal(object)
	pluginUnLoadEvent = pyqtSignal(object)
	def __init__(self, parent):
		super(HaxeAPI, self).__init__(parent)
		self.settings = QSettings("phar", "haxe hex editor")
		self.activefocusfilename = None
		self.openFiles = {}
		self.hexdocks = {}
		self.qtparent = parent
		self.copy_mode = 0
		self.paste_mode = 0
		self.modules = {}
		self.loaded_plugins = {}
		self.scanPlugins()
		self.startPlugins()
		self.largfilethreshold = 1073741824
		
		
	def getConverters(self):
		return(CLIPBOARD_CONVERT_FROM,CLIPBOARD_CONVERT_TO)
	
	def pluginSinCallstack(self):
		self.log("-------BEGIN PLUGIN_SIN-------")
		traceback.print_exc()
		self.log("-------END PLUGIN_SIN-------")

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

# 	def getBytes(self,file,range=(0,None)):
# 		(start,stop) = range
# 		if stop == None:
# 			stop == len(self.openFiles[file].data)
# 		return self.openFiles[file].data[start:stop] 
# 	def getSelectedRange(self,file):
# 		return self.openFiles[file].selection.getRange()
# 	
# 	def getSelectedBytes(self,file):
# 		(start,stop) = self.getSelectedRange(file)
# 		return self.openFiles[file].data[start:stop] 
# 
# 	def patchBytes(self,file,range=(0,None), patch=b'', padchar=b'\x00'):
# 		(start,stop) = range
# 		if stop == None:
# 			return False
# 		self.openFiles[file].data[start:stop] = patch.ljust((stop-start),padchar)
# 		return True
# 		
# 	def histogram(self,file,range=(0,None)): #why is this so slow
# 		(start,stop) = range
# 		a  = np.ndarray.__new__(np.ndarray,
# 		   shape=(len(self.openFiles[file].data[start:stop]),),
# 		   dtype=np.uint8,
# 		   buffer=self.openFiles[file][start:stop],
# 		   offset=0,
# 		   strides=(1,),
# 		   order='C')
# 		hist(a, bins=256, range=(0,256), histtype='step')

	def find(self, filename, findval, selection=None):
		return  self.openFiles[filename].find(findval, selection)
 		
	def findAll(self, filename, findval, selection=None):	
		return  self.openFiles[filename].findAll(findval, selection)
		
	def openFile(self, filename):
		try:
			fs = os.stat(filename)
			largefile = fs.st_size > self.largfilethreshold
			if largefile == True:
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Large file!")
				msg.setInformativeText("This is a big file, would you like to open this file in 'largefile' mode?, this will require less memory, but will disable insertion and deletion as the filesize cannot be changed in this mode.")
				msg.setWindowTitle("Large File Support")
				msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No |  QMessageBox.Cancel )
				retval = msg.exec_()		
				if retval == QMessageBox.No:
					largefile = False
				if retval == QMessageBox.Cancel:
					return None
			self.openFiles[filename] =  FileBuffer(filename,largefile=largefile)
			return filename
		except:
			self.log("error opening file")
			return None
				
	def log(self, logmsg):
		print(logmsg)

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
	
		for n,p in self.api.loaded_plugins.items():
			dw = p.pluginDockableWidget()
			if dw is not None:
				print("%s is dockable!" % n)		
				(name, dock, window, action, shortcut) = self.createDock(p.pluginDockableWidget)
				self.docks[name] = {'dock':dock, 'window':window,'action':action,'shortcut':shortcut}		
				self.viewmenu.addAction(self.docks[name]['action'])
			
		self.drawIcon()
	
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
		print("drag-drop",fn)      	
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
		geo = self.api.settings.value("geometry")
		if geo != None:
			self.restoreGeometry(geo)
		state = self.api.settings.value("windowState")
		if state != None:
			self.restoreState(state)
	
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


	def save_file(self):
		self.api.log("Saving...")
		try:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Save confirm.")
			msg.setInformativeText("Are you really sure you want to save to the existing file?")
			msg.setWindowTitle("Confirm Operation")
			msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
			retval = msg.exec_()		
			if retval == QMessageBox.Ok:
				self.api.log("save confirmed.")
				self.api.openFiles[self.api.getActiveFocus()].saveFile()
				self.api.log("save done.")
			else:
				self.api.log("aborted")
		except:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Save Failed.")
			msg.setInformativeText("This is probably because you dont have permissions to write to the file.")
			msg.setWindowTitle("Critical Error")
			msg.setStandardButtons(QMessageBox.Ok)
			self.api.log("save failed.")
			retval = msg.exec_()	
			
	def save_file_as(self):
		filename = QFileDialog.getSaveFileName(self, "Save File as...")[0]
		if filename:
			self.api.log("Saving...")
			try:
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Save confirm.")
				msg.setInformativeText("Are you really sure you want to save to the existing file?")
				msg.setWindowTitle("Confirm Operation")
				msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
				retval = msg.exec_()		
				if retval == QMessageBox.Ok:
					self.api.log("save confirmed.")
					self.api.openFiles[self.api.getActiveFocus()].saveFileAs(filename)
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
		else:
			self.api.log("no filename selected")		


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
	h.show()
	app.exec_()
