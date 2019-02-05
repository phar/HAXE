from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport
from IPython.core.magic import register_line_magic
from IPython import get_ipython



class IPythonWidget(RichJupyterWidget):
    def __init__(self, parent=None, run='', **kwargs):
        super(self.__class__, self).__init__()
        self.app = app = guisupport.get_app_qt4()
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        try:
            kernel_manager.start_kernel()
        except:
            return


        self.kernel = kernel = kernel_manager.kernel
        kernel.gui = 'qt4'
        kernel.shell.push(kwargs)


        self.kernel_client = kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            self.hide()
            return
        kernel.shell.run_cell(run)
        self.exit_requested.connect(stop)
