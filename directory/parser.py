#!/usr/bin/env python3
import os.path
import glob

class AwsDirectoryParser:
	'''This class performs the function of taking a path (as a string) and creates a tree structure of it.
		
		It keeps track of each file as well as some attributes of the file like the modification time and can return
		the data.
		The caller can use this data for caching purposes or as desired'''
	def __init__(self, path=None):
		self.tree = []
		self.setPath(path)
	
	def setPath(self, path):
		'''Sets the path to the directory to be parsed.'''
		if(path != None and len(path.strip()) > 0):
			if not os.path.exists(path):
				raise IOError("The path {0} does not exist on this machine".format(path))
			else:
				self.path = path
		else:
			self.path = None
			
	def getTree(self):
		'''Returns a tree structure appropriate for the specified path.
		
		It returns the processed tree as well as a list containing error messages as a tuple.'''
		errors = []
		if(self.path != None):
			path_info = self.parsePath(self.path)
			if (len(path_info) == 0):
				#an empty directory
				raise IOError("The directory {0} is empty...".format(self.path))
			self.tree, errors = self.processPathInfo(path_info)
		return (self.tree, errors)
	
	def processPathInfo(self, path_info):
		'''Gets the required attributes for all paths in the path_info list.
		
		It returns a list of processed paths and errors encountered while processing them as a 2 tuple.'''
		errors = []
		processed_paths = []
		for path in path_info:
			entry = {"path": path, "relative_path":path.replace(self.path,"")}
			try:
				type = ""
				if os.path.isfile(path):
					type = "file"
				else:
					type = "dir"
				entry['type'] = type
				entry['last_modified_time'] = os.path.getmtime(path)
				entry['size'] = os.path.getsize(path)
				processed_paths.append(entry)
			except OSError as exc:
				errors.append("Error on path {0}".format(path))
		return (processed_paths, errors)
		
	def parsePath(self, path):
		'''Returns a structure containing all files and directories within the specified path.
		
		It recursively parses the specified structure returning all sub paths'''
		path_info = []
		if os.path.isdir(path):
			sub_paths = glob.glob(os.path.join(path,"*"))
			dirs = [dirpath for dirpath in sub_paths if os.path.isdir(dirpath)] #list the directories
			files = [filepath for filepath in sub_paths if os.path.isfile(filepath)] #list the files
			path_info.extend(files)
			for directory in dirs:
				path_info.extend(self.parsePath(directory)) #do this recursively
		elif os.path.isfile(path):
			path_info.extend(path)
		return path_info	