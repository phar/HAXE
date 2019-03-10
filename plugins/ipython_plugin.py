#modules provided by haxe
from plugin_base import *
from selection import *
#modules required for this plugin
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport
from IPython.core.magic import register_line_magic
from IPython import get_ipython






	

class IPythonPlugin(HexPlugin):
	def __init__(self,api):
		super(IPythonPlugin, self).__init__(api,"iPython")
		self.loadiPythonEnvironment("ipython.env")

		self.dw = None
		
	def start(self):
		self.dw = IPythonWidget(run=self.ipythonenv,main=self)
		self.dw.setMinimumWidth(300)
			
	def stop(self):
		if self.mainWin != None:
			self.mainWin.close()		
			
	def pluginDockableWidget(self):
# 		ipython = IPythonWidget(run=self.ipythonenv,main=self)
# 		return  ("IPython","Alt+P",self.dw)
		return ("IPython","Alt+P",self.dw)

	def loadiPythonEnvironment(self, filename="ipython.env"):
		f = open(filename)
		self.ipythonenv = f.read()
		f.close()


class IPythonWidget(RichJupyterWidget):
	def __init__(self, parent=None, run='', **kwargs):
		super(self.__class__, self).__init__()
		self.app = app = guisupport.get_app_qt4()
		self.kernel_manager = kernel_manager = QtInProcessKernelManager()
		try:
			kernel_manager.start_kernel()
		except:
			return

		self.kernel_manager.kernel._abort_queues = self._abort_queues #"monkey patch"
		self.kernel = kernel = kernel_manager.kernel
		kernel.gui = 'qt'
		kernel.shell.push(kwargs)

		self.kernel_client = kernel_client = kernel_manager.client()
		kernel_client.start_channels()

		def stop():
			self.hide()
			return
		kernel.shell.run_cell(run)
		self.exit_requested.connect(stop)

	def _abort_queues(self, kernel):
		pass
