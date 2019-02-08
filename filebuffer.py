FILEMODE_READONLY =  1
FILEMODE_OVERWRITE = 2
import os
import mmap

class FileBuffer(object):
	def __init__(self,filename):
		self.readonly = True
		self.modified = False
		self.mode = FILEMODE_READONLY;
		self.editlist = []
		self.editindex = 0
		self.bufferlen = 0
		
		if filename != None:
			self.filename = filename
			self.datafd = os.open(self.filename, os.O_RDWR | os.O_SYNC | os.O_CREAT)
			self.data = mmap.mmap(self.datafd, os.stat(self.filename).st_size)
		else:
			self.data = mmap.mmap(-1, size)
			self.filename = "<buffer>"	
		
		self.bufferlen = len(self.data)		

	def addEdit(self, addr, edit):
		if self[addr] != edit:
			self.editlist.append((addr, self[addr], edit))
			self.editindex += 1

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
			for (a,c,e) in self.editlist[:self.editindex]:
				if a in ar:
					t[a-start] = e
			return t[:key.step]
			
		t = self.data[key]
		for (a,c,e) in self.editlist[:self.editindex]:
			if (a-key) == 0:
				t = e		
		return t

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
		print("save")
		ar =  range(0,self.bufferlen)
		for (a,c,e) in self.editlist[:self.editindex]:
			if a in ar:
				self.data[a] = e
		self.editlist = []
		self.editindex = 0
		
	def saveFileAs(self,filename):
		self.editlist = []
		self.editindex = 0
		
	def closeFile(self):
		os.close(self.datafd)