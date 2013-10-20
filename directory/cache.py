#!/usr/bin/env python3
import os.path
import shelve

class AwsDirectoryCache:
	'''This class performs the sole purpose of maintaining a cache for all directories.
	
	It maintains a cache containing metadata relevant to files on a per folder basis for directories/files
	uploaded using the script.'''
	def __init__(self, path=None, tree=None, db_name="AwsDirectoryCache.db", cache_key=None):
		self.setDbName(db_name)
		self.setPath(path)
		self.setTree(tree)
		self.setCacheKey(cache_key)
	
	def setCacheKey(self, cache_key):
		"""Sets the value for the cache key."""
		if cache_key is None or len(cache_key.strip()) == 0:
			self.cache_key = self.path
		else:
			self.cache_key = cache_key
	
	def setDbName(self, db_name):
		"""Sets the name of the database to be used by the cache manager."""
		if db_name is None or len(db_name.strip()) == 0:
			raise TypeError("The DB name cannot be None or an empty string")
		self.db_name = db_name
	
	def setPath(self, path):
		"""Sets the path to the directory whose data is to be cached."""
		self.path = None
		if path is not None and len(path.strip()) > 0:
			if not os.path.exists(path):
				raise IOError("The path {0} does not exist on this machine".format(path))
			else:
				self.path = path
	
	def setTree(self, tree):
		"""Sets the tree that will be used to generate the cache data to be stored."""
		self.tree = None
		tree = list(tree) #enforce the list type
		if tree is not None and len(tree) > 0:
			entry_0 = tree[0]
			if "path" in entry_0 and "relative_path" in entry_0 and "last_modified_time" in entry_0:
				self.tree = tree
			else:
				raise KeyError("One or more of the keys (path,relative_path,last_modified_time) was not found in your entries")			
	
	def getCache(self):
		"""Gets the cache data for the specified path in the db if it exists else it throws an error."""
		shelve_db = shelve.open(self.db_name)
		if not self.cache_key in shelve_db:
			raise KeyError("The index for key {0} was not found".format(self.cache_key))
		cache_data = shelve_db[self.cache_key]
		shelve_db.close()
		return cache_data
	
	def setCache(self):
		"""Sets the new data for the value of this path in the cache."""
		if self.path is None or self.tree is None:
			raise EnvironmentError("Either or both the path and path tree data are set to None")
		cache_data = [{"path": entry['path'], "relative_path": entry['relative_path'],
					   "last_modified_time": entry['last_modified_time']} for entry in self.tree]
		return self.writeCache(cache_data)
	
	def writeCache(self, cache_data):
		"""Writes the generated cache data for the directory to the shelve store.

		This works by creating an entry for the directory in the shelve db."""
		save_status = False
		if self.cache_key is not None:
			shelve_db = shelve.open(self.db_name) #open the shelve db for the data
			shelve_db[self.cache_key] = cache_data
			shelve_db.close()
			save_status = True
		return save_status