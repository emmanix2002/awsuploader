#!/usr/bin/env python3
import sys
import directory.parser

test_path = "/home/eokeke/Development/workspace-python/awsuploader"
#the path we'll be running the test on

if __name__ == '__main__':
	parser = directory.parser.AwsDirectoryParser(test_path)
	if len(sys.argv) > 1:
		arg = int(sys.argv[1])
		if (arg == 1):
			#let's test the parsePath method
			print("Testing parsePath() method...")
			paths = parser.parsePath(test_path)
			for path in paths:
				print(path)
		elif arg == 2:
			#let's test the processPathInfo method
			print("Testing processPathInfo() method...")
			paths, directories = parser.parsePath(test_path)
			print(directories)
			print(paths)
			processed_path_info, errors = parser.processPathInfo(paths)
			for path_entry in processed_path_info:
				print(path_entry)
			for path_entry in directories:
				print(path_entry)
			print(errors)
		else:
			print("Testing getTree() method...")
			tree, errors, directories = parser.getTree()
			for entry in tree:
				print(entry)
			for path_entry in directories:
				print(path_entry)
	else:
		print("Testing getTree() method...")
		tree, errors, directories = parser.getTree()
		print(tree)