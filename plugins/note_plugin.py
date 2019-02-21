#modules provided by haxe
from plugin_base import *
from selection import *
#modules required for this plugin
from construct import *


class NoteActionClass(SelectionActionClasss):		
	def editAction(self):
		self.mainWin = NotesGUIWin(self, action='edit')
		self.mainWin.show()


class NotesGUIWin(QDialog):
	def __init__(self,obj,action='new'):
		QDialog.__init__(self)
# 		self.changeHexObj( obj)
		self.actionclass = obj
		self.api = self.actionclass.hexdialog.api
		
		self.setMinimumSize(QSize(430, 150))    
		self.setWindowTitle("Notes plugin") 

		gridLayout = QGridLayout()     
		self.setLayout(gridLayout)  

		self.note = QPlainTextEdit("hash")
		gridLayout.addWidget(self.note, 1,0,1,2)

		gobtn = QPushButton("OK")
		gobtn.clicked.connect(self.addnote)
		gridLayout.addWidget(gobtn, 2,0,1,2)

		self.notetext = ""
		
		if action=='edit':
			self.notetext = self.actionclass.labelAction()
			pass
		else:
			txt =  self.api.settings.value("%s.notes.lastnote")
			if txt != None:
				self.notetext = txt
			else:
				self.notetext =  ""
			
		self.note.setPlainText(self.notetext)
			

	def addnote(self):
		(start,end) = self.actionclass.hexdialog.getSelection().getRange()
		text = self.note.toPlainText()
		self.actionclass.setLabel(text)
		self.actionclass.hexdialog.addSelection(start,end, obj=self.actionclass, color=self.actionclass.hexdialog.hexWidget.getNextColor()) #fixme
		self.close()
	
	def loadSettings(self):
# 		txt = self.obj.api.settings.value("%s.notes.lastnote")
		pass

	def saveSettings(self):
		self.api.settings.setValue("%s.notes.lastnote",self.note.toPlainText())
# 
# 	def changeHexObj(self, obj):
# 		self.obj = obj

	def closeEvent(self,event):
		self.saveSettings()

	

class NotesPlugin(HexPlugin):
	def __init__(self,api):
		super(NotesPlugin, self).__init__(api,"Notes")
# 		self.mainWin = None

	def start(self):
		pass
			
	def stop(self):
		if self.mainWin != None:
			self.mainWin.close()		

	def pluginSelectionPlacement(self, selection=None):
		return [("add Notes", self.addNote)]

	def addNote(self, hexobj):
# 		if self.mainWin == None:
		self.mainWin = NotesGUIWin(NoteActionClass(hexobj))
		self.mainWin.show()
	
