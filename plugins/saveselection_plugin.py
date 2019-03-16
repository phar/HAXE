#modules provided by haxe
from plugin_base import *

#modules required for this plugin


class SaveSelectionPlugin(HexPlugin):
	def __init__(self,api):
		super(SaveSelectionPlugin, self).__init__(api,"SaveSelection")
		self.mainWin = None

	def start(self):
		pass
			
	def stop(self):
		pass
		
	def pluginSelectionPlacement(self, selection=None):
		return [("Save Selection", self.selectionfilter)]

	def selectionfilter(self, hexobj):
		filename = QFileDialog.getSaveFileName(None, "Save File as...")[0]
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
					f  = open(filename,"wb")
					(start,end) = hexobj.getCursor().getRange()
					f.write(hexobj.filebuff[start:end])
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

