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
from binascii import *
from math import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import argparse
from matplotlib.pyplot import *
import binwalk
# # %matplotlib inline

# own submodules
from hexwidget import *
from ipythonwidget import *
from cursor import *
from docks import *
from mmapslice import *

class Delegate(QItemDelegate):
    def __init__(self):
        super(Delegate, self).__init__()
        self.validator = QIntValidator()

    def setModelData(self, editor, model, index):
        print (editor, model, index)
        editor = QLineEdit(editor)
        editor.setValidator(self.validator)
        super(Delegate, self).setModelData(editor, model, index)


class SearchDialog(QWidget):
	def __init__(self, hexwidget=None, parent=None):
		super(SearchDialog, self).__init__(parent)
		self.hexwidget = hexwidget
		self.lyt = QGridLayout()
		self.setLayout(self.lyt)

		self.searchline = QLineEdit()
		self.pb_search = QPushButton("Search")
		self.search_a = QRadioButton("ASCII")
		self.search_a.setChecked(True)
		self.search_chex = QRadioButton("C Hex")
		self.search_hex = QRadioButton("Hex String")
		self.search_reg = QRadioButton("RegEx")

		self.lyt.addWidget(self.searchline, 0, 0,1,3)
		self.lyt.addWidget(self.search_a, 1, 0)
		self.lyt.addWidget(self.search_hex, 1, 1)
		self.lyt.addWidget(self.search_reg, 1, 2)


		self.lyt.addWidget(self.pb_search, 2, 2)

		self.pb_search.clicked.connect(self.do_search)

	def do_search(self):
		phrase = self.searchline.text()
		if self.search_a.isChecked():
			index = self.hexwidget.data.find(phrase.encode('utf-8'), self.hexwidget.cursor.address)
		elif self.search_chex.isChecked():
			pass
		elif self.search_hex.isChecked():
			phrase = self.searchline.text().decode("hex").encode('utf-8')
			index = self.hexwidget.data.find(phrase.encode('utf-8'), self.hexwidget.cursor.address)
		
		elif self.search_reg.isChecked():
			pass			
		
		if index >= 0:
			self.hexwidget.goto(index)
# 			self.statusBar().showMessage("found at offset 0x%08x" % index)
		else:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Informational)
			msg.setText("Search String was not found")
			msg.setInformativeText("Search string not found.")
			msg.setWindowTitle("Not found")
			msg.setStandardButtons(QMessageBox.Ok)
# 			self.statusBar().showMessage("search string not found")
			retval = msg.exec_()		
		
		self.close()





class HexEditor(QMainWindow):
	def __init__(self,args):
		super(HexEditor, self).__init__()

		self.setWindowTitle("Best Hex Editor")
		self.hexwidgets = []
		self.central = QMainWindow()
		self.central.setWindowFlags(Qt.Widget)
		self.central.setDockOptions(self.central.dockOptions()|QMainWindow.AllowNestedDocks)
		self.tabs = {}
		self.openFiles = {}
# 		self.
		self.open_file(args.filename)
		self.setCentralWidget(self.central)
		self.font = QFont("Courier", 10)
		self.indicator = QLabel("Overwrite")
		self.statusBar().showMessage("yay")
		self.statusBar().addPermanentWidget(self.indicator)
		self.createDocks()
		self.createActions()
		self.createMenus()
		self.set_example_data()
		self.drawIcon()

	def drawIcon(self):
		self.pixmap = QPixmap(64,64)
		painter = QPainter(self.pixmap)
		painter.fillRect(0,0,64,64,Qt.green)
		painter.setPen(QColor(192,0,192))
		painter.setFont(QFont("Courier", 64))
		painter.drawText(6,57,"H")
		self.icon = QIcon(self.pixmap)
		self.setWindowIcon(self.icon)


	def createDocks(self):
		self.setDockOptions(self.dockOptions() | QMainWindow.AllowNestedDocks)
		allowed_positions = Qt.AllDockWidgetAreas
		# make struct editor widget
		self.structeditor = QTextEdit()
		# qscintilla compatibility
		self.structeditor.text = self.structeditor.toPlainText
		self.structeditor.setText = self.structeditor.setPlainText
		self.structeditor.setStyleSheet("background-color: rgb(255, 232, 232);")#red
# 		self.structeditor.setStyleSheet("background-color: rgb(242, 255, 232);")#green
		

		self.structeditor.setFont(self.font)

		self.dock1 = QDockWidget()
		self.dock1.setWindowTitle("Struct Editor")
		self.dock1.setWidget(self.structeditor)
		self.dock1.setAllowedAreas(allowed_positions)
		self.dock1.hide()
		self.addDockWidget(Qt.RightDockWidgetArea, self.dock1)



		# make struct explorer widget
		self.structexplorer = s = QTreeWidget()
		s.setColumnCount(3)
		self.d = Delegate()

		self.dock2 = QDockWidget()
		self.dock2.setWindowTitle("Struct Explorer")
		self.dock2.setWidget(self.structexplorer)
		self.dock2.setAllowedAreas(allowed_positions)
		self.dock2.hide()

		self.addDockWidget(Qt.RightDockWidgetArea, self.dock2)


		self.hexwidgets[0].cursor.changed.connect(self.eval)
		self.hexwidgets[0].cursor.changed.connect(self.eval)

		
		
		self.structeditor.setMinimumWidth(300)
		self.structexplorer.setMinimumWidth(300)


		self.ipython = IPythonWidget(run='''
# import matplotlib
%matplotlib inline
from pylab import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from construct import *
from binascii import *
import binwalk
import numpy as np

api = main

#data = main.hexwidgets[0].data
#a  = np.ndarray.__new__(np.ndarray,
#        shape=(len(data),),
#        dtype=np.uint8,
#        buffer=data,
#        offset=0,
#        strides=(1,),
#        order='C')

def histogram():
    hist(a, bins=256, range=(0,256))

''',main=self)
		self.ipython.setMinimumWidth(300)
		self.dock3 = QDockWidget()
		self.dock3.setWindowTitle("IPython")
		self.dock3.setWidget(self.ipython)
		self.dock3.setAllowedAreas(allowed_positions)
		self.addDockWidget(Qt.LeftDockWidgetArea, self.dock3)


		self.dock1.setObjectName("structedit")
		self.dock2.setObjectName("structexp")
		self.dock3.setObjectName("ipython")
		self.dock3.hide()

		
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
		   buffer=self.openFiles[file].data[start:stop],
		   offset=0,
		   strides=(1,),
		   order='C')
		hist(a, bins=256, range=(0,256), histtype='step')
				
	def open_file(self, filename=None):
# 		print(filename)
		if filename in [None, False]:
			filename = QFileDialog.getOpenFileName(self, "Open File...")[0]
		#print self.filename
		if filename:
# 			w = HexWidget(filename=filename)
			self.openFiles[filename] =  HexWidget(self, filename=filename)			
			self.hexwidgets.append(self.openFiles[filename])
			self.tabs[filename] = QDockWidget()
			self.tabs[filename].setWindowTitle(self.openFiles[filename].filename)
			self.tabs[filename].setWidget(self.openFiles[filename])
			self.tabs[filename].setAllowedAreas(Qt.AllDockWidgetAreas)
			self.central.addDockWidget(Qt.RightDockWidgetArea, self.tabs[filename])
		else:
			pass #i dont know what to do with this
		
	def save_file_as(self):
		self.filename = QFileDialog.getSaveFileName(self, "Save File as...")[0]
		if self.filename:
			self.statusBar().showMessage("Saving...")
			open(self.filename, 'wb').write(self.hexwidgets[0].data)
			self.statusBar().showMessage("done.")

	def save_file(self):
#		self.filename = QFileDialog.getSaveFileName(self, "Save File as...")[0]
#		if self.filename:
		self.statusBar().showMessage("Saving...")
		try:
			open(self.hexwidgets[0].filename, 'wb').write(self.hexwidgets[0].data)
			self.statusBar().showMessage("wrote %s done." % self.hexwidgets[0].filename)
		except:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Save Failed.")
			msg.setInformativeText("This is probably because you dont have permissions to write to the file.")
			msg.setWindowTitle("Critical Error")
			msg.setStandardButtons(QMessageBox.Ok)
			self.statusBar().showMessage("save failed.")
			retval = msg.exec_()		
		


	def createActions(self):
		self.act_open = QAction("&Open", self)
		self.act_open.setShortcuts(QKeySequence.Open)
		self.act_open.setStatusTip("Open file")
		self.act_open.triggered.connect(self.open_file)

		self.act_save = QAction("&Save ...", self)
		self.act_save.setShortcuts(QKeySequence.Save)
		self.act_save.setStatusTip("Save file...")
		self.act_save.triggered.connect(self.save_file)
		
		self.act_saveas = QAction("Save as...", self)
		self.act_saveas.setShortcuts(QKeySequence.SaveAs)
		self.act_saveas.setStatusTip("Save file as...")
		self.act_saveas.triggered.connect(self.save_file_as)

		self.act_quit = QAction("&Quit", self)
		self.act_quit.setShortcuts(QKeySequence.Quit)
		self.act_quit.setStatusTip("Quit Best Hex Editor")
		self.act_quit.triggered.connect(self.close)

		self.act_search = QAction("&Search", self)
		self.act_search.setShortcuts(QKeySequence.Find)
		self.act_search.setStatusTip("Search current buffer for a string")
		self.act_search.triggered.connect(self.search)

		self.ta_sed = self.dock1.toggleViewAction()
		self.ta_sed.setShortcut(QKeySequence("Alt+S"))
		self.ta_sexp = self.dock2.toggleViewAction()
		self.ta_sexp.setShortcut(QKeySequence("Alt+X"))
		self.ta_ipy = self.dock3.toggleViewAction()
		self.ta_ipy.setShortcut(QKeySequence("Alt+P"))

	def createMenus(self):
		self.filemenu = self.menuBar().addMenu("&File")
		self.filemenu.addAction(self.act_open)
		self.filemenu.addAction(self.act_save)
		self.filemenu.addAction(self.act_saveas)
		self.filemenu.addAction(self.act_quit)
		self.filemenu.addAction(self.act_search)

		self.viewmenu = self.menuBar().addMenu("&View")

		self.viewmenu.addAction(self.ta_sed)
		self.viewmenu.addAction(self.ta_sexp)
		self.viewmenu.addAction(self.ta_ipy)

	def toggle_structedit(self):
		if self.structeditor.isVisible():
			self.structeditor.setVisible(False)
		else:
			self.structeditor.setVisible(True)


	def search(self):
		self.dia = SearchDialog(hexwidget = self.hexwidgets[0])
		self.dia.show()
		self.dia.raise_()
		self.dia.activateWindow()



	def foo(self, x):
		try:
			y = ("\n" + self.structeditor.text()).index("\n" + x)
		except:
			print( x)
			raise
		return y

	def eval(self):
		try:
			self.structexplorer.clear()
			self.hexwidgets[0].clearHilights()
			self.items = []
			ns = {}
# 			print(self.structeditor.text())
			exec(compile("from construct import *\n" + self.structeditor.text(), '<none>', 'exec'), ns)
			results = []
			import construct
			for name in sorted([x for x, v in ns.items() if isinstance(v, construct.Construct) and (x not in dir(construct)) ], key=self.foo):
				cons = ns[name]
				try:
					self.structeditor.setStyleSheet("background-color: rgb(242, 255, 232);")#green
					parsed = cons.parse(self.hexwidgets[0].data[self.hexwidgets[0].cursor.address:])
				except:
					parsed = "<parse error>"
					
				if isinstance(parsed, construct.Container):
					self.items.append(QTreeWidgetItem(self.structexplorer, [cons.name,'Container',"none"]))
					parent = self.items[-1]
					parent.setExpanded(True)
					offt =  self.hexwidgets[0].cursor.address
					for i in cons.subcons:
						self.hexwidgets[0].addHilight(offt,offt+i.sizeof()-1)
						offt+=i.sizeof()						

					for k, v in parsed.items():
						if not k.startswith('_'):
							it = QTreeWidgetItem(parent, [k, str(v), "0x%x" % v, 'none'])
							it.setFlags(it.flags() | Qt.ItemIsEditable)
							self.items.append(it)
				else:
					it = QTreeWidgetItem(self.structexplorer,[cons.name, str(parsed),"none"])
					self.items.append(it)
			for i in range(4):
				self.structexplorer.resizeColumnToContents(i)

			self.hexwidgets[0].viewport().update()
		except Exception as e:
			self.structeditor.setStyleSheet("background-color: rgb(255, 232, 232);")#red
			print ("except",e)

	def closeEvent(self, event):

		settings = QSettings("csarn", "best hex editor")
		settings.setValue("geometry", self.saveGeometry())
		settings.setValue("windowState", self.saveState())
		QMainWindow.closeEvent(self, event)

	def set_example_data(self):
#		self.hexwidgets[0].highlights.append(Selection(10,20))
		self.structeditor.setText("""foo = Struct(
    "foo" / Int16ul,
    "bar" / Int32ul,
    "baz" / Int64ul
    )
    
    """)
		self.eval()




if __name__ == '__main__':
	app = QApplication([])

	parser = argparse.ArgumentParser()

	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
	parser.add_argument("-d", "--debug", help="debug output", action="store_true")
	parser.add_argument("-f", "--filename", help="filename") #fixme

	args = parser.parse_args()
	if args.verbose:
		print("verbosity turned on")

	h = HexEditor(args)
	h.show()
	app.exec_()
