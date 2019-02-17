#modules provided by haxe
from plugin_base import *

#modules required for this plugin
import hashlib

class HashGUIWin(QMainWindow):
	def __init__(self,obj):
		QMainWindow.__init__(self)
		self.changeHexObj( obj)
	
		self.setMinimumSize(QSize(430, 150))    
		self.setWindowTitle("Hashing plugin") 

		centralWidget = QWidget(self)          
		self.setCentralWidget(centralWidget)   

		gridLayout = QGridLayout()     
		centralWidget.setLayout(gridLayout)  

		l = QLabel("Select Hash:")
		self.hashcb = QComboBox()
		for i in hashlib.algorithms_available:
			self.hashcb.addItem(i)	

		gridLayout.addWidget(l, 0,0,1,1)
		gridLayout.addWidget(self.hashcb, 0,1,1,1)

		self.hashout = QPlainTextEdit("hash")
		gridLayout.addWidget(self.hashout, 1,0,1,2)


		gobtn = QPushButton("Go")
		gridLayout.addWidget(gobtn, 2,0,1,2)
		gobtn.clicked.connect(self.dohash)

		self.loadSettings()
	
	def loadSettings(self):
		txt = self.obj.api.settings.value("%s.hashplugin.hash")
		print(txt)
		index = self.hashcb.findText(txt, Qt.MatchFixedString)
		if index >= 0:
			self.hashcb.setCurrentIndex(index)
         
	def saveSettings(self):
		self.obj.api.settings.setValue("%s.hashplugin.hash",self.hashcb.currentText())

	def changeHexObj(self, obj):
		self.obj = obj

	def dohash(self):		
		h = hashlib.new(self.hashcb.currentText())
		(start,end) = self.obj.hexWidget.cursor._selection.getRange()
		h.update(self.obj.filebuff[start:end])
		self.hashout.setPlainText(h.hexdigest())
# 		print(h.hexdigest())

	def closeEvent(self,event):
			self.saveSettings()

	

class HashPlugin(HexPlugin):
	def __init__(self,api):
		super(HashPlugin, self).__init__(api,"Hash")
		self.mainWin = None

	def start(self):
		pass
			
	def stop(self):
		if self.mainWin != None:
			self.mainWin.close()		

	def pluginSelectionPlacement(self, selection=None):
		return [("hash", self.selectionfilter)]

	def selectionfilter(self, hexobj):
		if self.mainWin == None:
			self.mainWin = HashGUIWin(hexobj)
		self.mainWin.show()
