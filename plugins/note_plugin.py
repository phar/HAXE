#modules provided by haxe
from plugin_base import *
from selection import *
#modules required for this plugin


class NoteActionClass(SelectionActionClasss):		
	def editAction(self,selection):
		self.mainWin = NotesGUIWin(self,selection,  action='edit')
		self.mainWin.show()
		
	def labelAction(self,selection):
		if selection in self.selections:
			return "Note: %s" % selection.getLabel()
			
	def dragAction(self,selection,dragdistance):
		if selection in self.selections:
			selection += dragdistance
# 			print("click! %d" % dragdistance)


class NotesGUIWin(QDialog):
	def __init__(self,obj,hexobj,action='new'):
		QDialog.__init__(self)
		self.actionclass = obj
		self.api = hexobj.api
		self.hexdialog  = hexobj
		
		self.setMinimumSize(QSize(430, 150))    
		self.setWindowTitle("Notes plugin") 

		gridLayout = QGridLayout()     
		self.setLayout(gridLayout)  
		self.action = action
		self.selection = hexobj.getSelection()

		self.note = QPlainTextEdit("note text")
		gridLayout.addWidget(self.note, 1,0,1,2)

		gobtn = QPushButton("OK")
		gobtn.clicked.connect(self.addnote)
		gridLayout.addWidget(gobtn, 2,0,1,2)

		self.notetext = ""
		
		if self.action=='edit':
			self.notetext = self.hexdialog.getSelection.getLabel() #i think this is wrong
			pass
		else:
			txt =  self.api.settings.value("%s.notes.lastnote")
			if txt != None:
				self.notetext = txt
			else:
				self.notetext =  ""
			
		self.note.setPlainText(self.notetext)
			
	def addnote(self):
		text = self.note.toPlainText()
		if self.action=='edit':
			self.selection.setLabel(text)
		else:
			self.selection.obj=self.actionclass
			self.selection.active=True
			self.selection.color = self.hexdialog.hexWidget.getNextColor()
			self.selection.setLabel(text)
			self.actionclass.addSelection(self.hexdialog,self.selection)
		self.close()
	
	def loadSettings(self):
# 		txt = self.obj.api.settings.value("%s.notes.lastnote")
		pass

	def saveSettings(self):
		self.api.settings.setValue("%s.notes.lastnote",self.note.toPlainText())
# 
	def closeEvent(self,event):
		self.saveSettings()

	

class NotesPlugin(HexPlugin):
	def __init__(self,api):
		super(NotesPlugin, self).__init__(api,"Notes")
		self.ac = NoteActionClass(name='Note')

	def start(self):
		pass
			
	def stop(self):
		if self.mainWin != None:
			self.mainWin.close()		

	def pluginSelectionPlacement(self, selection=None):
		return [("add Notes", self.addNote)]

	def addNote(self, hexobj):
		self.mainWin = NotesGUIWin(self.ac,hexobj)
		self.mainWin.show()
	
