#modules provided by haxe
from plugin_base import *
from selection import *
#modules required for this plugin
# from construct import *
import construct
from construct import *
from math import *



class StructActionClass(SelectionActionClasss):
	pass

	def labelAction(self,selection):
		for i in self.selections:
			if i == selection:
				return "%s: %s"  % (self.name, selection.label)				
		return self.name
		
	def editAction(self,selection):
		print("dblckick!")
		True
		

class StructEditor(QTextEdit):
	structChanged = pyqtSignal(object)
	def __init__(self, parent):
		super(StructEditor, self).__init__()
		self.api = parent.api
		self.parent = parent
		self.setMinimumWidth(300)
		self.setText(self.parent.structbuff)
		self.refreshStructBuff()
		self.loadSettings()
		
	def setStructOk(self):
		self.setStyleSheet("background-color: rgb(232, 255, 232); color: rgb(0, 0, 0);")#green
		
	def setStructBad(self):
		self.setStyleSheet("background-color: rgb(255, 232, 232);color: rgb(0, 0, 0)")#red
	
	def contextMenuEvent(self, event):
		menu = QMenu()
		mnu = {} #fixme
		mnu["save"] = menu.addAction("Save Struct File", self.saveStructFile)	
		mnu["load"] = menu.addAction("Load Struct File", self.loadStructFile)		
		mnu["load"] = menu.addAction("Evaluate Structs", self.reEvalStructFile)		
		action = menu.exec_(self.mapToGlobal(event.pos()))

	def loadStructFile(self):
		self.parent.loadStructFile()
		self.setText(self.parent.structbuff)
	
	def saveStructFile(self):
		self.refreshStructBuff()
		self.parent.saveStructFile()
	
	def reEvalStructFile(self):
		self.parent.evalStructFile()
		self.refreshStructBuff()

	def refreshStructBuff(self):
		if self.parent.structbuff != self.toPlainText():
			self.parent.structbuff = self.toPlainText()
		if self.parent.structfilegood:
			self.setStructOk()
		else:
			self.setStructBad()
			
	def close(self):
		self.saveSettings()
	
	def saveSettings(self):
		self.api.settings.setValue("struct.editor.geometry", self.saveGeometry())
		self.api.settings.setValue("struct.editor.windowState", self.saveState())

	def loadSettings(self):
		geo = self.api.settings.value("struct.editor.geometry")
		if geo != None:
			self.restoreGeometry(geo)
		state = self.api.settings.value("struct.editor.windowState")
		if state != None:
			self.restoreState(state)

		
class StructPlugin(HexPlugin):
	def __init__(self, api):
		super(StructPlugin, self).__init__(api,"Structs")
		self.mainWin = None
		self.api = api
		self.hexdisplays = {}
		self.structs = {}
		self.structbuff = ""
		self.structfilegood = False
		print(dir(api))
		self.ac = StructActionClass(name='Struct')

		txt = self.api.settings.value("structs.laststructfile")
		if txt is not None:
			self.loadStructFile(txt)			
		self.structeditor = StructEditor(self)

	def start(self):
		pass
			
	def stop(self):
		if self.mainWin != None:
			self.mainWin.close()		

	def pluginSelectionSubPlacement(self):
		endlist = [("seperator", None),
					("Remove Struct", self.delStructHere),
					("seperator", None),
					("Struct Editor", self.structEditor),
					]
		structs = [] #fixme
		for n,s in self.structs.items():
			structs.append((n,lambda y, x=n : self.addStructHere(y, x)))
		return  structs + endlist


	def delStructHere(self,hexobj):
		print("moo",hexobj.getCursor().getSelection())
	
	def addStructHere(self,hexobj,struct):
		addr = hexobj.getCursor().getPosition()
		offset = 0

		try:
			foo = self.structs[struct].parse(hexobj.filebuff[addr:])
			hasdata = True
		except construct.core.StreamError:		
			hasdata = False
			
		except construct.core.ConstError:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Struct Error")
			msg.setInformativeText("this structure has defined constants which could not be applied at this locations")
			msg.setWindowTitle("Struct Error")
			msg.setStandardButtons(QMessageBox.Ok)
			retval = msg.exec_()
			return
			
		for i in self.structs[struct].subcons:
				try:
					selection = Selection(addr + offset, addr + offset + i.sizeof())
					offset += i.sizeof()
				except SizeofError: #dynamic field
					if hasdata:
						selection = Selection(addr + offset, addr + offset + len(foo[i.name]))
						offset += len(foo[i.name])
					else:
						selection = None
					
				if selection is not None:					
					selection.obj=self.ac
					selection.active=True
					selection.color = hexobj.hexWidget.getNextColor()
					selection.setLabel(".".join([struct, i.name]))
					self.ac.addSelection(hexobj, selection)	
						
# 		wholeselection = Selection(addr, addr + offset) #i though id like this
# 		wholeselection.obj=self.ac
# 		wholeselection.active=True
# 		wholeselection.color = hexobj.hexWidget.getNextColor()
# 		wholeselection.setLabel(struct)
# 		self.ac.addSelection(hexobj, wholeselection)


	


	def pluginSelectionPlacement(self, selection=None):
		return [("Struct (beta)", None)]

	def structEditor(self, hexobj):
		if self.mainWin == None:
			self.mainWin = StructEditor(self)
		self.mainWin.show()
		
	def evalStructFile(self):
		self.items = []
		ns = {}
		try:
			exec(compile("from math import *\nfrom construct import *\n" + self.structbuff, '<none>', 'exec'), ns)
			results = []
			self.structs = {}
			for name in sorted([x for x, v in ns.items() if isinstance(v, construct.Construct) and (x not in dir(construct)) ], key=self.foo):
				cons = ns[name]
				self.structs[name] = cons
			self.structfilegood = True
		except:
			self.structfilegood = False
			print(dir(traceback))
			traceback.print_exc()
		return self.structfilegood
			
	def loadStructFile(self,filename = None):
		if filename is None:
			filename = QFileDialog.getOpenFileName(None, "Load Struct defs From...")[0]
		if filename:
			f = open(filename, "rb")
			self.structbuff = f.read().decode("utf-8")
			f.close()
		if self.evalStructFile() == True:
			self.api.settings.setValue("structs.laststructfile",filename)
		self.filename = filename
		
	def saveStructFile(self):
		self.filename = QFileDialog.getSaveFileName(None, "Save Struct defs as...")[0]
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

	def getStruct(self,name):
		return self.structs[name]
		
	def getStructList(self):
		return [x for x,y in self.structs.items()]
		