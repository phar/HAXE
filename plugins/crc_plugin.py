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
		for n in crcmod.predefined._crc_definitions:
			self.crccb.addItem(n['name'])	
		self.crccb.currentIndexChanged.connect(self.setcrc)

		gridLayout.addWidget(l, 0,0,1,1)
		gridLayout.addWidget(self.crccb, 0,1,1,1)

		l = QLabel("Polynomial")
		self.poly = QLineEdit("")
		gridLayout.addWidget(l, 1,0,1,2)
		gridLayout.addWidget(self.poly, 1,1,1,2)

		l = QLabel("XOR in")
		self.xorin = QLineEdit("")
		gridLayout.addWidget(l, 2,0,1,2)
		gridLayout.addWidget(self.xorin, 2,1,1,2)

		l = QLabel("XOR out")
		self.xorout = QLineEdit("")
		gridLayout.addWidget(l, 3,0,1,2)
		gridLayout.addWidget(self.xorout, 3,1,1,2)

		l = QLabel("Bit Width")
		self.bitwidth = QLineEdit("")
		gridLayout.addWidget(l, 4,0,1,2)
		gridLayout.addWidget(self.bitwidth, 4,1,1,2)

		self.refout = QCheckBox("Reflect out")
		gridLayout.addWidget(self.refout, 5,0,1,2)

		l = QLabel("CRC Out")
		self.crcout = QLineEdit("")
		gridLayout.addWidget(l, 6,0,1,2)
		gridLayout.addWidget(self.crcout, 6,1,1,2)

		gobtn = QPushButton("Go")
		gridLayout.addWidget(gobtn, 8,2,1,1)

		gobtn.clicked.connect(self.docrcfunc)
		self.loadSettings()
		
	def getBitLengthFromPoly(self,poly):
		return int(poly).bit_length() - 1

	def setcrc(self):
		print("yep")
		for i in crcmod.predefined._crc_definitions:
			if i['name'] == self.crccb.currentText():
				bl = self.getBitLengthFromPoly(i['poly'])
				self.poly.setText(hex(i['poly']))
				self.xorin.setText(hex(i['init']))
				self.xorout.setText( hex( i['xor_out']))


				self.bitwidth.setText("%d" %bl)
				self.refout.setChecked(i['reverse'])
				return		

	def docrcfunc(self):	
		try:
			poly = int(self.poly.text(),16)
			init =  int(self.xorin.text(),16)
			xorout =  int(self.xorout.text(),16)		
			rev = self.refout.isChecked()
			crc32_func = crcmod.mkCrcFun(poly, rev=False, initCrc=init, xorOut=xorout)
			(start,end) = self.obj.hexWidget.cursor._selection.getRange()
			self.crcout.setText (hex(crc32_func(self.obj.filebuff[start:end])))
		except:
			self.crcout.setText ("invalid input values")
			
		print("booop")
		
	def changeHexObj(self, obj):
		self.obj = obj

	def loadSettings(self):
		txt = self.obj.api.settings.value("crcplugin.predefinedcrc")
		index = self.crccb.findText(txt, Qt.MatchFixedString)
		if index >= 0:
			self.crccb.setCurrentIndex(index)

		txt = self.obj.api.settings.value("crcplugin.poly")
		if txt != None:
			self.poly.setText(txt)		
		txt = self.obj.api.settings.value("crcplugin.xorin")
		if txt != None:
			self.xorin.setText(txt)
		txt = self.obj.api.settings.value("crcplugin.xorout")
		if txt != None:
			self.xorout.setText(txt)
		txt = self.obj.api.settings.value("crcplugin.refout")
		if txt != None:
			self.refout.setChecked(txt)
         
	def saveSettings(self):
		self.obj.api.settings.setValue("crcplugin.predefinedcrc",self.crccb.currentText())
		self.obj.api.settings.setValue("crcplugin.poly",self.poly.text())
		self.obj.api.settings.setValue("crcplugin.xorin",self.xorin.text())
		self.obj.api.settings.setValue("crcplugin.xorout",self.xorout.text())
		self.obj.api.settings.setValue("crcplugin.refout",self.refout.isChecked())

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
