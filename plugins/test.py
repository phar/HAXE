from plugin_base import *
# import foobaz #to test if modules fail to load

import prevent_example_plugin_from_loading


class HelloWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(640, 480))    
        self.setWindowTitle("Hello world") 

        centralWidget = QWidget(self)          
        self.setCentralWidget(centralWidget)   

        gridLayout = QGridLayout(self)     
        centralWidget.setLayout(gridLayout)  

        title = QLabel("Hello World from PyQt", self) 
        title.setAlignment(Qt.AlignCenter) 
        gridLayout.addWidget(title, 0, 0)
        

class HashPlugin(HexPlugin):
	def __init__(self,api):
		super(HashPlugin, self).__init__(api,"Test plugin test")
		print("plugin loaded")

	def start(self):
		self.mainWin = HelloWindow()
		self.mainWin.show()
		
	def stop(self):
		self.mainWin.close()		


	def pluginSelectionPlacement(self, selection=None):
		return [("test", self.selectionfilter)]


	def selectionfilter(self, hexobj):
		print(hexobj.getSelection())
		return "foo"