import os
import mmap
from selection import *
import time

class FileBuffer(object):
	def __init__(self,filename=None,readonly=False,largefile=False):
		self.readonly = True
		self.modified = False
		self.editlist = []
		self.editindex = None
		self.bufferlen = 0
		self.readonly = False
		self.largdocumentmode = largefile
		self.filename = filename
		self.newfile = True
		
		if filename != None:
			self.filestat = os.stat(self.filename)
			if self.largdocumentmode:
				self.datafd = os.open(self.filename, os.O_RDWR | os.O_SYNC | os.O_CREAT)
				self.data = mmap.mmap(self.datafd, os.stat(self.filename).st_size)
				self.newfile = False
			else:
				try:
					self.datafd = os.open(self.filename, os.O_RDWR | os.O_SYNC | os.O_CREAT)
					self.newfile = False
				except PermissionError:
					try:
						self.datafd = os.open(self.filename, os.O_RDONLY | os.O_SYNC)
						self.readonly = True;
						self.newfile = False
					except:
						pass #fixme
				
			self.data = bytearray(os.read(self.datafd,self.filestat.st_size))
		else:
			self.data = bytearray(b"")
			self.filename = "untitld-%d" % time.time()
		
		self.bufferlen = len(self.data)		

	def statusString(self):
		string = ""
		if self.modified:
			string += "[modifid]"
		if self.newfile:
			string += "[new]"
		if self.largdocumentmode:
			string += "[large]"
		if self.readonly:
			string += "[readonly]"
		else:
			string += "[read/write]"
		return string		
						
	def addEdit(self, selection, edit):	
		if self.editindex == None:
			self.editindex = 0
		else:
			self.editindex += 1
		self.editlist = self.editlist[:self.editindex]
		self.editlist.append((selection.start, self[selection.start:selection.end], edit))
		self.modified = True
		if not self.largdocumentmode:
			if  (not isinstance(edit,int)):
					if not self.largdocumentmode:	
						if selection.end != None:
							self.data = self.data[:selection.start] + edit + self.data[selection.end:]	
						else:
							self.data = self.data[:selection.start] + edit + self.data[selection.start:]	
						self.bufferlen = len(self.data)
			else:
				self.data[selection.start] = edit

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
			
		if key < self.bufferlen:
			t = self.data[key]
			if self.largdocumentmode:
				for (a,c,e) in self.editlist[:self.editindex]:
					if (a-key) == 0:
						t = e		
		else:
			print (self.bufferlen)
			self.addEdit(Selection(self.bufferlen, self.bufferlen), b'\x00')
			return self[key]
			t = 0
			
		return t
	
	def redo(self):
		if self.editindex != None and  self.editindex == len(self.editlist):
			(addr, oldval, curval) = self.editlist[self.editindex ]
			if isinstance(curval, int):
				clen = 1
			else:
				clen = len(curval)

			self.data = self.data[:addr] + curval + self.data[addr + clen:]
			self.bufferlen -= len(oldval)	
			self.bufferlen += clen
			
			if self.editindex ==None:
				self.editindex = 0
			else:
				self.editindex += 1
				
			return Selection(addr, )
		else:
			print("no more undo levels")
			return None

	def find(self, findval, cursor=None):
		if(len( cursor.getSelection())):
			(start,end) = cursor.getSelection().getRange()
			return  self.data.find(findval, start, end )
		else:
			return  self.data.find(findval)

	def findNext(self, findval, cursor=None):
		(start,end) = cursor.getSelection().getRange()
		if(len( cursor.getSelection())):
			return  self.data.find(findval, start+1, end )
		else:
			return  self.data.find(findval,start+1)

	def rfind(self, findval, cursor=None):
		if(len( cursor.getSelection())):
			(start,end) = cursor.getSelection().getRange()
			return  self.data.rfind(findval, start, end)
		else:
			return  self.data.find(findval)

	def findPrev(self, findval, cursor=None):
		(start,end) = cursor.getSelection().getRange()
		if(len( cursor.getSelection())):
			return  self.data.rfind(findval, start, end - 1)
		else:
			return  self.data.rfind(findval,0, end-1)
									
	def findAll(self, findval, selection=None):	
		if selection == None:	
			return [i for i in range(len(self)) if self.data.startswith(findval, i)]
		else:
			(start,end) = selection.getRange()
			return [i for i in range(start,end) if self.data.startswith(findval, i, end)]
	
	def undo(self):
		if self.editindex != None:
			print(self.editindex, len(self.editlist))
			(addr, oldval, curval) = self.editlist[self.editindex]
			if isinstance(curval, int):
				clen = 1
			else:
				clen = len(curval)

			self.data = self.data[:addr] + oldval + self.data[addr + clen:]				
			self.bufferlen -= clen
			self.bufferlen += len(oldval)	
				
			if self.editindex == 0:
				self.editindex = None
			else:
				self.editindex -= 1
		else:
			print("no more undo levels")
					

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
				print([e])
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