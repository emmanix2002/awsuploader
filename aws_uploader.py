#!/usr/bin/env python3
import argparse
import directory.parser

__version__ = "1.0.0 alpha"

if __name__ == '__main__':	
	args_parser = argparse.ArgumentParser(description="Runs an upload using the `scp` command and uploads file[s] to an EC2 instance")
	args_parser.add_argument("-p","--path",help="Specify the directory to be uploaded to the EC2 instance")
	args_parser.add_argument("-u","--user",help="Specify the username to be used in connecting with the EC2 instance")
	args_parser.add_argument("-i","--identity-file",help="Specify the path to the .pem file to be used with the instance")
	args_parser.add_argument("--host",help="Specify the public IP address to the EC2 instance")
	args = args_parser.parse_args()
	for option in args:
		print("{0} --> {1}".format(option,args[option]))