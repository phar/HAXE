#modules provided by haxe
from plugin_base import *

#modules required for this plugin
from capstone import *

CAPSTONE_SUPPORTED_ARCHMODES = [
        (CS_ARCH_X86, CS_MODE_16, "X86 16bit (Intel syntax)", None),
        (CS_ARCH_X86, CS_MODE_32, "X86 32bit (ATT syntax)", CS_OPT_SYNTAX_ATT),
        (CS_ARCH_X86, CS_MODE_32, "X86 32 (Intel syntax)", None),
        (CS_ARCH_X86, CS_MODE_64, "X86 64 (Intel syntax)", None),
        (CS_ARCH_ARM, CS_MODE_ARM, "ARM", None),
        (CS_ARCH_ARM, CS_MODE_ARM, "ARM: Cortex-A15 + NEON", None),
        (CS_ARCH_ARM, CS_MODE_THUMB, "THUMB", None),
        (CS_ARCH_ARM, CS_MODE_THUMB, "THUMB-2", None),
        (CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_MCLASS, "Thumb-MClass", None),
        (CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_V8, "Arm-V8", None),
        (CS_ARCH_ARM64, CS_MODE_ARM, "ARM-64", None),
        (CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_BIG_ENDIAN, "MIPS-32 (Big-endian)", None),
        (CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN, "MIPS-64-EL (Little-endian)", None),
        (CS_ARCH_MIPS, CS_MODE_MIPS32R6 + CS_MODE_MICRO + CS_MODE_BIG_ENDIAN, "MIPS-32R6 | Micro (Big-endian)", None),
        (CS_ARCH_MIPS, CS_MODE_MIPS32R6 + CS_MODE_BIG_ENDIAN, "MIPS-32R6 (Big-endian)", None),
        (CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, "PPC-64", None),
        (CS_ARCH_PPC, CS_MODE_BIG_ENDIAN + CS_MODE_QPX, "PPC-64 + QPX", None),
        (CS_ARCH_SPARC, CS_MODE_BIG_ENDIAN, "Sparc", None),
        (CS_ARCH_SPARC, CS_MODE_BIG_ENDIAN + CS_MODE_V9, "SparcV9", None),
        (CS_ARCH_SYSZ, 0, "SystemZ", None),
        (CS_ARCH_XCORE, 0, "XCore", None),
        (CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_040, "M68K (68040)", None),
        (CS_ARCH_M680X, CS_MODE_M680X_6809, "M680X_M6809", None),
]


class CapstoneGUIWin(QDialog):
	def __init__(self,pluginparent):
		QDialog.__init__(self)
# 		self.changeHexObj( obj)
		self.pluginparent = pluginparent
		
		self.setMinimumSize(QSize(630, 350))    
		self.setWindowTitle("Disassembler plugin") 

		gridLayout = QGridLayout()     
		self.setLayout(gridLayout)  

		l = QLabel("Select Arch:")
		self.archcb = QComboBox()
		for (arch, mode, name, syntax) in CAPSTONE_SUPPORTED_ARCHMODES:
			self.archcb.addItem(name)	

		gridLayout.addWidget(l, 0,0,1,1)
		gridLayout.addWidget(self.archcb, 0,1,1,1)

		self.disasmwindow = QPlainTextEdit("disassemble")
		gridLayout.addWidget(self.disasmwindow, 1,0,1,2)


		gobtn = QPushButton("disassemble")
		gridLayout.addWidget(gobtn, 2,0,1,2)
		gobtn.clicked.connect(self.dodisasm)

		self.loadSettings()
	
	def dodisasm(self):
		(start,end) = self.pluginparent.api.getActiveFocus().getCursor().getRange()

		md = Cs(CAPSTONE_SUPPORTED_ARCHMODES[self.archcb.currentIndex()][0],CAPSTONE_SUPPORTED_ARCHMODES[self.archcb.currentIndex()][1])
		md.detail = True
		if CAPSTONE_SUPPORTED_ARCHMODES[self.archcb.currentIndex()][3] is not None:
			md.syntax = CAPSTONE_SUPPORTED_ARCHMODES[self.archcb.currentIndex()][3]		
		outtxt = ""
		for i in md.disasm(self.pluginparent.api.getActiveFocus().filebuff[start:end], start):
			outtxt += "%x: %s \t\t%s\t%s\n" %(i.address,"".join(["%02x" % x for x in i.bytes]), i.mnemonic, i.op_str)
		self.disasmwindow.setPlainText(outtxt)
		self.disasmwindow.repaint() #had to do this on my new machine not sure why

		
	def loadSettings(self):
		txt = self.pluginparent.api.settings.value("%s.capstoneplugin.arch")
		index = self.archcb.findText(txt, Qt.MatchFixedString)
		if index >= 0:
			self.archcb.setCurrentIndex(index)
		pass
         
	def saveSettings(self):
		self.parent.api.settings.setValue("%s.capstoneplugin.arch",self.archcb.currentText())
		pass

# 	def changeHexObj(self, obj):
# 		self.obj = obj


	def closeEvent(self,event):
			self.saveSettings()

	

class CapstonePlugin(HexPlugin):
	def __init__(self,api):
		super(CapstonePlugin, self).__init__(api,"CapstonePlugin")
		self.mainWin = None

	def start(self):
		pass
			
	def stop(self):
		if self.mainWin != None:
			self.mainWin.close()		

	def pluginSelectionPlacement(self, selection=None):
		return [("disassemble (capstone)", self.selectionfilter)]

	def selectionfilter(self, hexobj):
		if self.mainWin == None:
			self.mainWin = CapstoneGUIWin(self)
		self.mainWin.show()
