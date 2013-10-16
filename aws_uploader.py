#!/usr/bin/env python3
import argparse
import os.path
import subprocess
import sys
import directory.parser
import directory.cache

__version__ = "1.0.0"
__author__ = "Okeke Emmanuel<emmanix2002@gmail.com>"
__license__ = ""

parser = cacher = src_path = user = identity_file = dest = host = None

def set_identity_file(identity_file_path):
	'''Sets the path to the identity file on the local machine.'''
	global identity_file
	if identity_file_path != None and len(identity_file_path.strip()) > 0:
		if os.path.exists(identity_file_path) and os.path.isfile(identity_file_path):
			identity_file = identity_file_path
	
def set_path(path):
	'''Sets the source path on the local machine.'''
	global src_path
	if path != None and len(path.strip()) > 0:
		if os.path.exists(path):
			src_path = path

def set_dest(path):
	'''Sets the destination path on the remote instance.'''
	global dest
	if path != None and len(path.strip()) > 0:
		dest = path			

def set_user(username):
	'''Sets the username to use in connecting to the EC2 instance.'''
	global user
	username = str(username)
	if username != None and len(username.strip()) > 0:
		user = username

def set_host(hostname):
	'''Sets the hostname of the EC2 instance.'''
	global host
	hostname = str(hostname)
	if hostname != None and len(hostname.strip()) > 0:
		host = hostname

def is_config_ok():
	'''Checks that all required variables have appropriate vlues.'''
	global src_path, user, identity_file, dest, host
	if src_path == None or user == None or identity_file == None or dest == None or host == None:
		return False
	return True

def collate_upload_list(cache_data, tree):
	'''Creates a list of files to be uploaded to the server comparing against data in the cache for changes.'''
	upload_list = []
	if cache_data == None:
		upload_list = tree
	else:
		for item in tree:
			is_item_found = False
			for entry in cache_data:
				if entry['path'] == item['path']:
					is_item_found = True
					if entry['last_modified_time'] < item['last_modified_time']:
						upload_list.append(item)
					break
			if not is_item_found:
				#the item was not in the list -- a new file
				upload_list.append(item)
	return upload_list

def show_errors(errors):
	if len(errors):
		print("*******ERRORS FROM PARSER*****************")
		for error in errors:
			print(error)
		print("******************************************")

def show_uploads(upload_list):
	'''Shows the files that will be uploaded to the server.'''
	global user, host
	print("Below is a list of files that will be uploaded to the remote machine {0}@{1}".format(user, host))
	for item in upload_list:
		print("{1} Bytes --> {0}".format(item['path'], item['size']))

if __name__ == '__main__':
	args_parser = argparse.ArgumentParser(description="Runs an upload using the `scp` command and uploads file[s] to an EC2 instance")
	args_parser.add_argument("-s","--src",help="Specify the source directory|file to be uploaded")
	args_parser.add_argument("-d","--dest",help="Specify the directory on the EC2 instance where the src is to be uploaded to")
	args_parser.add_argument("-u","--user",help="Specify the username to be used in connecting with the EC2 instance")
	args_parser.add_argument("-i","--identity_file",help="Specify the path to the .pem file to be used with the instance")
	args_parser.add_argument("--host",help="Specify the public IP address to the EC2 instance")
	args = args_parser.parse_args()
	#parse the command line arguments
	set_dest(args.dest)
	set_identity_file(args.identity_file)
	set_path(args.src)
	set_host(args.host)
	set_user(args.user)
	if is_config_ok():
		upload_list = []
		parser = directory.parser.AwsDirectoryParser(src_path)
		tree, errors = parser.getTree()
		show_errors(errors)
		cacher = directory.cache.AwsDirectoryCache(src_path, tree, "AwsDirectoryCache.db")
		try:
			cache_data = cacher.getCache()
		except KeyError as error:
			#no cache exists for the path -- so we just save the cache--and upload all files
			cache_data = None
		except:
			cache_data = None
		finally:
			cacher.setCache()
		upload_list = collate_upload_list(cache_data, tree)
		show_uploads(upload_list)
		for item in upload_list:
			print("Uploading {0}".format(item['path']))
			try:
				command = '''scp -i {0} -rCp {1} {2}@{3}:{4}'''.format(
					identity_file, item['path'], user, host, os.path.join(dest, item['relative_path'])
				)
				print("Command --> {0}".format(command))
				return_code = subprocess.call(command, shell=True)
				if return_code == 0:
					print("Upload successful...")
				elif return_code < 0:
					print("Child was terminated by signal: {0}".format(return_code))
				else:
					print("Child returned: {0}".format(return_code))
			except OSError as error:
				print("Execution failed: ", end="\t")
				print(error)
	else:
		print("Some required configuration parameters have not been set...See below")
		print("*"*50)
		print("Identity File: {0}".format(identity_file))
		print("Source: {0}".format(src_path))
		print("Remote User: {0}".format(user))
		print("Hostname: {0}".format(host))
		print("Destination: {0}".format(dest))
		print("*"*50)