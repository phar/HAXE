from plugin_base import *



class TestPlugin(HexPlugin):
	def __init__(self,api):
		super(TestPlugin, self).__init__(api)
		print("woop")
