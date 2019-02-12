import os
import mmap



class FileBuffer(object):
	def __init__(self,filename,readonly=False,largefile=False):
		self.readonly = True
		self.modified = False
		self.mode = 'overwrite';
		self.editlist = []
		self.editindex = 0
		self.bufferlen = 0
		self.readonly = False
		self.largdocumentmode = largefile
		self.filename = filename
		
		if filename != None:
			self.filestat = os.stat(self.filename)
			if self.largdocumentmode:
				self.datafd = os.open(self.filename, os.O_RDWR | os.O_SYNC | os.O_CREAT)
				self.data = mmap.mmap(self.datafd, os.stat(self.filename).st_size)
			else:
				try:
					self.datafd = os.open(self.filename, os.O_RDWR | os.O_SYNC | os.O_CREAT)
				except PermissionError:
					self.datafd = os.open(self.filename, os.O_RDONLY | os.O_SYNC)
					self.readonly = True;
				self.data = bytearray(os.read(self.datafd,self.filestat.st_size))
		else:
			self.data = []
			self.filename = None
		
		self.bufferlen = len(self.data)		

	def addEdit(self, selection, edit):
		self.editlist.append((selection.start, self[selection.start:selection.end], edit))
		if not self.largdocumentmode:
			if  (not isinstance(edit,int)):
					print(edit)
# 				if (len(edit) > 1):
					if not self.largdocumentmode:	
						if selection.end != None:
							self.data = self.data[:selection.start] + edit + self.data[selection.end:]	
						else:
							self.data = self.data[:selection.start] + edit + self.data[selection.start:]	
						self.bufferlen = len(self.data)
# 					print("yep",type(edit))
			else:
				self.data[selection.start] = edit
		self.editindex += 1

# 	def __setitem__(self, key):
# 		if isinstance(key, slice):
# 			if key.stop == None:
# 				stop = self.bufferlen
# 			else:
# 				stop = key.stop
# 			
# 			if key.start == None:
# 				start = 0
# 			else:
# 				start = key.start



	def __len__(self):
		return self.bufferlen

	def __getitem__(self, key):
		if isinstance(key, slice):
			if key.stop == None:
				stop = self.bufferlen
			else:
				stop = key.stop
			
			if key.start == None:
				start = 0
			else:
				start = key.start

			t =  bytearray(self.data[start:stop])
			ar =  range(start,stop)
			va = start
			if self.largdocumentmode:
				for (a,c,e) in self.editlist[:self.editindex]:
					if a in ar:
						t[a-start] = e
			return t[:key.step]
			
		t = self.data[key]
		if self.largdocumentmode:
			for (a,c,e) in self.editlist[:self.editindex]:
				if (a-key) == 0:
					t = e		
		return t

	def find(self, findbuf, start=None, end=None):
		
		return 0

	def readOnly(self, tf):
		if tf == True:
			self.readonly = True
		elif tf == False:
			self.readonly == False
	
	def modified(self,tf):
		if tf == True:
			self.modified = True
		elif tf == False:
			self.modified == False
		
	def saveFile(self):
		ar =  range(0,self.bufferlen)
		for (a,c,e) in self.editlist[:self.editindex]:
			if a in ar:
				self.data[a] = e
		if not self.largdocumentmode and not self.readonly:
			os.lseek(self.datafd,0,os.SEEK_SET)
			os.write(self.datafd,self.data)
			os.fsync(self.datafd)
		self.editlist = []
		self.editindex = 0
		
	def saveFileAs(self,filename):
		self.editlist = []
		self.editindex = 0
		
	def closeFile(self):
		os.close(self.datafd)