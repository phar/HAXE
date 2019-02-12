

class HexPlugin():
	def __init__(self,api):
		self.api = api

	def name(self):
		raise "must implement"	

	def load(self):
		raise "must implement"	
		
	def unload(self):
		raise "must implement"	

	def preRunGui(self, selection=None):
		raise "must implement"	
		
	def postRunGui(self, selection=None):
		raise "must implement"	

	def run(self, selection=None):
		raise "must implement"	
