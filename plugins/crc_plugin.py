#modules provided by haxe
from plugin_base import *

#modules required for this plugin
import crcmod

class CRCGUIWin(QMainWindow):
	def __init__(self,obj):
		QMainWindow.__init__(self)
		self.changeHexObj( obj)
	
		self.setMinimumSize(QSize(430, 150))    
		self.setWindowTitle("CRC plugin") 

		centralWidget = QWidget(self)          
		self.setCentralWidget(centralWidget)   

		gridLayout = QGridLayout()     
		centralWidget.setLayout(gridLayout)  

		l = QLabel("Preconfigured CRCs:")
		self.crccb = QComboBox()
		for n,v in crcmod.predefined._crc_definitions_by_name.items():
			self.crccb.addItem(n)	


		gridLayout.addWidget(l, 0,0,1,1)
		gridLayout.addWidget(self.crccb, 0,1,1,1)


		l = QLabel("Polynomial")
		self.hashout = QLineEdit("")
		gridLayout.addWidget(self.hashout, 1,0,1,2)
		gridLayout.addWidget(self.hashout, 1,0,1,2)


		l = QLabel("XOR in")
		self.hashout = QLineEdit("")
		gridLayout.addWidget(self.hashout, 1,0,1,2)
		gridLayout.addWidget(self.hashout, 1,0,1,2)

		l = QLabel("XOR out")
		self.hashout = QLineEdit("")
		gridLayout.addWidget(self.hashout, 1,0,1,2)
		gridLayout.addWidget(self.hashout, 1,0,1,2)


		self.refin = QCheckBox("Reflect in")
		gridLayout.addWidget(self.refin, 1,0,1,2)

		self.refout = QCheckBox("Reflect out")
		gridLayout.addWidget(self.refout, 1,0,1,2)



#{'name': 'crc-64-we', 'identifier': 'Crc64We', 'poly': 23270347676907615891, 'reverse': False, 'init': 0, 'xor_out': 18446744073709551615, 'check': 7128171145767219210}
	

		gobtn = QPushButton("Go")
		gridLayout.addWidget(gobtn, 2,0,1,2)
		gobtn.clicked.connect(self.dohash)


	def changeHexObj(self, obj):
		self.obj = obj

	def dohash(self):		
		h = hashlib.new(self.hashcb.currentText())
		(start,end) = self.obj.cursor._selection.getRange()
		h.update(self.obj.parent.filebuff[start:end])
		self.hashout.setText(h.hexdigest())
# 		print(h.hexdigest())
	
	
	def loadSettings(self):
		txt = self.obj.api.settings.value("%s.crcplugin.hash")
		index = self.crccb.findText(txt, Qt.MatchFixedString)
		if index >= 0:
			self.crccb.setCurrentIndex(index)
         
	def saveSettings(self):
		self.obj.api.settings.setValue("%s.crcplugin.hash",self.crccb.currentText())

	def closeEvent(self,event):
			self.saveSettings()

	



class CRCPlugin(HexPlugin):
	def __init__(self,api):
		super(CRCPlugin, self).__init__(api,"CRC")
		self.mainWin = None

	def start(self):
		pass
			
	def stop(self):
		if self.mainWin != None:
			self.mainWin.close()		

	def pluginSelectionPlacement(self, selection=None):
		return [("CRC", self.selectionfilter)]

	def selectionfilter(self, hexobj):
		if self.mainWin == None:
			self.mainWin = CRCGUIWin(hexobj)
		self.mainWin.show()
