#modules provided by haxe
from plugin_base import *
from selection import *
#modules required for this plugin


class NoteActionClass(SelectionActionClasss):	
	def __init__(self,pluginparent, name=None):
		super(NoteActionClass, self).__init__(pluginparent, name )
	
	def editAction(self, hexobj, selection):
		self.mainWin = NotesGUIWin(self.pluginparent, 'edit', selection)
		self.mainWin.show()
		
	def labelAction(self, hexobj, selection):
		if selection in self.selections:
			return "Note: %s" % selection.getLabel()
			
	def dragAction(self, hexobj, selection, dragdistance):
		if selection in self.selections:
			selection += dragdistance
			print(dragdistance)


class NotesGUIWin(QDialog):
	def __init__(self,pluginparent,action='new',selection=None):
		QDialog.__init__(self)
		self.actionclass = pluginparent.ac
		self.api = pluginparent.api
		self.pluginparent = pluginparent
		
		self.setMinimumSize(QSize(430, 150))    
		self.setWindowTitle("Notes plugin") 

		gridLayout = QGridLayout()     
		self.setLayout(gridLayout)  
		self.action = action

		self.note = QPlainTextEdit("note text")
		gridLayout.addWidget(self.note, 1,0,1,2)

		gobtn = QPushButton("OK")
		gobtn.clicked.connect(self.addnote)
		gridLayout.addWidget(gobtn, 2,0,1,2)

		self.notetext = ""
		
		if self.action=='edit':
			self.notetext = selection.getLabel() #i think this is wrong
			self.selection = selection
			pass
		else:
			txt =  self.api.settings.value("%s.notes.lastnote")
			if txt != None:
				self.notetext = txt
			else:
				self.notetext =  ""
			self.selection = self.pluginparent.api.getActiveFocus().getSelection()

			
		self.note.setPlainText(self.notetext)
		self.note.selectAll()
	
	def addnote(self):
		text = self.note.toPlainText()
		if self.action=='edit':
			self.selection.setLabel(text)
		else:
			self.selection.obj=self.actionclass
			self.selection.active=True
			self.selection.color =  self.api.color_palette[len( self.pluginparent.api.getActiveFocus().hexWidget.highlights)]  
			self.selection.setLabel(text)
			self.actionclass.addSelection(self.pluginparent.api.getActiveFocus(),self.selection)
		self.close()
		self.pluginparent.ac.updated.emit()

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
		self.ac = NoteActionClass(self, name='Note')

	def start(self):
		pass
			
	def stop(self):
		if self.mainWin != None:
			self.mainWin.close()		 

	def pluginSelectionPlacement(self, selection=None):
		return [("add Notes", self.addNote)]

	def addNote(self, hexobj):
		self.mainWin = NotesGUIWin(self)
		self.mainWin.show()
	
