#!/usr/bin/env python3
import os.path
import shelve

class AwsDirectoryCache:
	'''This class performs the sole purpose of maintaining a cache for all directories.
	
	It maintains a cache containing metadata relavant to files on a per folder basis for directories/files
	uploaded using the script.'''
	def __init__(self, path=None, tree=None, db_name="AwsDirectoryCache.db"):
		self.setDbName(db_name)
		self.setPath(path)
		self.setTree(tree)
		
	def setDbName(self, db_name):
		if db_name == None or len(db_name.strip()) == 0:
			raise TypeError("The DB name cannot be None or an empty string")
		self.db_name = db_name
	
	def setPath(self, path):
		'''Sets the path to the directory to be cached.'''
		if(path != None and len(path.strip()) > 0):
			if not os.path.exists(path):
				raise IOError("The path {0} does not exist on this machine".format(path))
			else:
				self.path = path
		else:
			self.path = None
	
	def setTree(self, tree):
		pass		
	
	def getCache(self, path):
		'''Gets the cache data for the specified path in the db if it exists else it throws an error.'''
		shelve_db = shelve.open(self.db_name)
		if not shelve_db.has_key(path):
			raise IndexError("The index for key {0} was not found".format(path))
		cache_data = shelve_db[path]
		shelve_db.close()
		return cache_data
	
	def setCache(self):
		'''Sets the new data for the value of this path in the cache.'''
		cache_data = [{"path": entry['path'], "relative_path": entry['relative_path'],
					   "last_modified_time": entry['last_modified_time']} for entry in self.tree]
		self.writeCache(cache_data)
	
	def writeCache(self, cache_data):
		'''Writes the generated cache data for the directory to the shelve store.
		
		This works by creating an entry for the directory in the shelve db.'''
		shelve_db = shelve.open(self.db_name) #open the shelve db for the data
		shelve_db[self.path] = cache_data
		shelve_db.close()