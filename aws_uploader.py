#!/usr/bin/env python3
import argparse
import os.path
import subprocess
import directory.parser
import directory.cache

__version__ = "1.0.0"
__author__ = "Okeke Emmanuel<emmanix2002@gmail.com>"
__license__ = ""

parser = cacher = src_path = user = identity_file = dest = host = None

def collate_upload_list():
	pass

def set_identity_file(identity_file_path):
	global identity_file
	if identity_file_path != None and len(identity_file_path.strip()) > 0:
		if os.path.exists(identity_file_path) and os.path.isfile(identity_file_path):
			identity_file = identity_file_path
	
def set_path(path):
	global src_path
	if path != None and len(path.strip()) > 0:
		if os.path.exists(path):
			src_path = path

def set_dest(path):
	global dest
	if path != None and len(path.strip()) > 0:
		if os.path.exists(path):
			dest = path

def set_user(username):
	global user
	username = str(username)
	if username != None and len(username.strip()) > 0:
		user = username

def set_host(hostname):
	global host
	hostname = str(hostname)
	if hostname != None and len(hostname.strip()) > 0:
		host = hostname

def is_config_ok():
	global src_path, user, identity_file, dest, host
	if src_path == None or user == None or identity_file == None or dest == None or host == None:
		return False
	return True

def generate_upload_list(cache_data, tree):
	upload_list = []
	for item in tree:
		pass
	return upload_list

def show_errors(errors):
	print("*******ERRORS FROM PARSER*****************")
	for error in errors:
		print(error)
	print("******************************************")

'''
try:
    retcode = call("mycmd" + " myarg", shell=True)
    if retcode < 0:
        print >>sys.stderr, "Child was terminated by signal", -retcode
    else:
        print >>sys.stderr, "Child returned", retcode
except OSError as e:
    print >>sys.stderr, "Execution failed:", e
'''

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
		parser = directory.parser.AwsDirectoryParser(test_path)
		tree, errors = parser.getTree()
		show_errors(errors)
		cacher = directory.cache.AwsDirectoryCache(src_path, tree)
		try:
			cache_data = cacher.getCache()
			upload_list = generate_upload_list(cache_data, tree)
		except KeyError as error:
			#no cache exists for the path -- so we just save the cache--and upload all files
			upload_list = tree
		finally:
			cacher.setCache()
		
	else:
		pass