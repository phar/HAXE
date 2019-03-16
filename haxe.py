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
		self.newHexDock = {}
		self.hexdocks = {}
		self.hexwidgets = {}
		self.qtparent = parent
		self.copy_mode = 0
		self.paste_mode = 0
		self.modules = {}
		self.loaded_plugins = {}
		self.scanPlugins()
		self.startPlugins()
		self.openFiles = {}
		self.largfilethreshold = 1073741824
		self.color_palette = [ #high contrast color mapping
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
# 		print(self.modules)
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
				self.alertMessage(self,msg,buttons=None, title=None, informativetext =None)
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
		
	def alertMessage(self,msg,buttons=None, title=None, informativetext =None):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Critical)
		if title is not None:
			msg.setText(title)
		else:
			msg.setText("HAxe")
			
		if informativetext is not None:
			msg.setInformativeText(informativetext)
		msg.setWindowTitle("Confirm Operation")
		if buttons is not None:
			msg.setStandardButtons(buttons)
		else:
			msg.setStandardButtons(QMessageBox.Ok )
		return msg.exec_()	
	
	def standardMessage(self,msg,buttons=None, title=None, informativetext =None):
		msg = QMessageBox()
# 		msg.setIcon(QMessageBox.Critical)
		if title is not None:
			msg.setText(title)
		else:
			msg.setText("HAxe")
			
		if informativetext is not None:
			msg.setInformativeText(informativetext)
		msg.setWindowTitle("Confirm Operation")
		if buttons is not None:
			msg.setStandardButtons(buttons)
		else:
			msg.setStandardButtons(QMessageBox.Ok )
		return msg.exec_()	
	
			
					
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
							
			self.openFiles[filename] = HexDialog(self,parent=self.qtparent,fileobj=FileBuffer(filename,largefile=largefile))
			return filename
		except:
			self.log("error opening file")
			return None
				
	def log(self, logmsg):
		print(logmsg)

	def getActiveFocus(self):
		if  self.activefocusfilename != None:
			return self.openFiles[self.activefocusfilename]
		# else:
# 			return self.openFiles.next(iter(self.openFiles.values()))
			
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
# 		self.setGraphicsSystem('native')
	
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
		

	def newHexDock(self, hexobj):
		tab = QDockWidget()
		
		tab.setWindowTitle(hexobj.filebuff.filename)
		tab.setWidget(hexobj)
		
		tab.setAllowedAreas(Qt.AllDockWidgetAreas)
		self.tabs.append(tab)
		self.central.addDockWidget(Qt.RightDockWidgetArea, tab)
		
	def open_file(self, filename=None):
	
		if filename in [None, False]:
			filename = QFileDialog.getOpenFileName(self, "Open File...")[0]
			
		if filename:
			hexobj = self.api.openFile(filename)
			if hexobj != None:
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
# 		self.api.qtparent.newHexDock()
		print("booot")

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
