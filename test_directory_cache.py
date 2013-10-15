#!/usr/bin/env python3
import sys
import directory.parser
import directory.cache

test_path = "/home/eokeke/Development/workspace-python/awsuploader"
#the path we'll be running the test on
test_db_name = "TestShelveDb.db"

if __name__ == '__main__':
	parser = directory.parser.AwsDirectoryParser(test_path)
	tree, errors = parser.getTree()
	cacher = directory.cache.AwsDirectoryCache(test_path, tree, test_db_name)
	if len(sys.argv) > 1:
		arg = int(sys.argv[1])
		if (arg == 1):
			#let's test the getCache method
			print("Testing getCache() method...")
			cache_data = cacher.getCache()
			for item in cache_data:
				print(item)
		elif arg == 2:
			#let's test the setCache method
			print("Testing setCache() method...")
			cacher.setCache()
			cache_data = cacher.getCache()
			for item in cache_data:
				print(item)
		else:
			print("Supply an integer btw 1-2...")
	else:
		print("No test specified!!! ROTFL!!!")