#!/usr/bin/env python3
import argparse
import os
import os.path
import subprocess
import directory.parser
import directory.cache

__version__ = "1.2.1"
__author__ = "Okeke Emmanuel<emmanix2002@gmail.com>"
__license__ = ""
awsuploader_dir = "/home/eokeke/Development/workspace-python/awsuploader"

parser = cacher = src_path = user = identity_file = dest = host = None

def set_identity_file(identity_file_path):
    """Sets the path to the identity file on the local machine."""
    global identity_file
    if identity_file_path is not None and len(identity_file_path.strip()) > 0:
        if os.path.exists(identity_file_path) and os.path.isfile(identity_file_path):
            identity_file = identity_file_path

def set_path(path):
    """Sets the source path on the local machine."""
    global src_path
    if path is not None and len(path.strip()) > 0:
        if os.path.exists(path):
            src_path = path

def set_dest(path):
    """Sets the destination path on the remote instance."""
    global dest
    if path is not None and len(path.strip()) > 0:
        dest = path

def set_user(username):
    """Sets the username to use in connecting to the EC2 instance."""
    global user
    username = str(username)
    if username is not None and len(username.strip()) > 0:
        user = username

def set_host(hostname):
    """Sets the hostname of the EC2 instance."""
    global host
    hostname = str(hostname)
    if hostname is not None and len(hostname.strip()) > 0:
        host = hostname

def is_config_ok():
    """Checks that all required variables have appropriate value."""
    global src_path, user, identity_file, dest, host
    if src_path is None or user is None or identity_file is None or dest is None or host is None:
        return False
    return True

def collate_upload_list(cache_data, tree):
    """Creates a list of files to be uploaded to the server comparing against data in the cache for changes."""
    upload_list = []
    cached_items = []
    if cache_data is None:
        upload_list = tree
    else:
        for item in tree:
            is_item_found = False
            for entry in cache_data:
                if entry['path'] == item['path']:
                    is_item_found = True
                    if entry['last_modified_time'] < item['last_modified_time']:
                        upload_list.append(item)
                    else:
                        # remains the same
                        cached_items.append(item)
                    break
            if not is_item_found:
                # the item was not in the list -- a new file
                upload_list.append(item)
    return upload_list, cached_items

def show_errors(errors):
    if len(errors):
        print("*******ERRORS FROM PARSER*****************")
        for error in errors:
            print(error)
        print("******************************************")

def show_uploads(upload_list):
    """Shows the files that will be uploaded to the server."""
    global user, host
    if len(upload_list) > 0:
        print("Below is a list of files that will be uploaded to the remote machine {0}@{1}".format(user, host))
        for item in upload_list:
            print("{1} Bytes --> {0}".format(item['path'], item['size']))
    else:
        print("No items need to be uploaded to machine {0}@{1} since there are no recent changes".format(user, host))

def collate_remote_directories(upload_list):
    """Determines the directories to be created on the remote server based on the files to be uploaded."""
    remote_directories = []
    for item in upload_list:
        remote_dir = os.path.dirname(item['path'])
        if remote_dir not in remote_directories:
            remote_directories.append(remote_dir)
    return remote_directories


def create_remote_directories(directories):
    """Uses SSH to create all the required directories on the remote machine.

    This has to be done before upload can begin to the machine."""
    global identity_file, user, host, dest, src_path
    status = True
    relative_paths = []
    created_dirs = []
    for path in directories:
        if path == src_path or path + "/" == src_path:
            # we don't need to create the source path tree
            continue
        rel_path = path.replace(src_path, "")
        if rel_path.startswith("/"):
            # remove the preceding / if it's found
            rel_path = rel_path[1:]
        relative_paths.append(rel_path)
    try:
        for rel_path in relative_paths:
            remote_dir_path = os.path.join(dest, rel_path)
            command = '''ssh -i {0} {1}@{2} mkdir -m 755 -p {3}'''.format(
                identity_file, user, host, remote_dir_path
            )
            print("Command --> {0}".format(command))
            return_code = subprocess.call(command, shell=True)
            if return_code == 0:
                print("Successfully created directory {0}".format(remote_dir_path))
                created_dirs.append(remote_dir_path)
            elif return_code < 0:
                message = "Child was terminated by signal: {0}".format(return_code)
                raise Exception(message)
            else:
                message = "Child returned: {0}".format(return_code)
                raise Exception(message)
    except OSError as error:
        status = False
        print("Execution failed: ", end="\t")
        print(error)
    except Exception as error:
        status = False
        print("Process failed: ", end="\t")
        print(error)
    return (status, created_dirs)

if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description="Runs an upload using the `scp` command and uploads file[s] to an EC2 instance")
    args_parser.add_argument("-s","--src",help="Specify the source directory to be uploaded")
    args_parser.add_argument("-d","--dest",help="Specify the directory on the EC2 instance where the src is to be uploaded to")
    args_parser.add_argument("-u","--user",help="Specify the username to be used in connecting with the EC2 instance")
    args_parser.add_argument("-i","--identity_file",help="Specify the path to the .pem file to be used with the instance")
    args_parser.add_argument("--host",help="Specify the public IP address to the EC2 instance")
    args = args_parser.parse_args()
    # parse the command line arguments
    set_dest(args.dest)
    set_identity_file(args.identity_file)
    set_path(args.src)
    set_host(args.host)
    set_user(args.user)
    if is_config_ok():
        oscurrent_working_directory = os.getcwd()
        os.chdir(awsuploader_dir)
        upload_list = []
        parser = directory.parser.AwsDirectoryParser(src_path)
        tree, errors, directories = parser.getTree()
        show_errors(errors)
        cacher = directory.cache.AwsDirectoryCache(src_path, tree, cache_key=src_path+"-"+dest)
        try:
            cache_data = cacher.getCache()
        except KeyError as error:
            # no cache exists for the path -- so we just save the cache--and upload all files
            cache_data = None
        except:
            cache_data = None
        upload_list, cache_items = collate_upload_list(cache_data, tree)
        show_uploads(upload_list)
        if len(upload_list) > 0:
            remote_dirs = collate_remote_directories(upload_list)
            status, created_dirs = create_remote_directories(remote_dirs)
            if status:
                # since the directory creation process was successful --  we can begin the upload
                uploaded_items = 0
                for item in upload_list:
                    print("Uploading {0}".format(item['path']))
                    try:
                        command = '''scp -i {0} -Cp {1} {2}@{3}:{4}'''.format(
                            identity_file, item['path'], user, host, os.path.join(dest, item['relative_path'])
                        )
                        print("Command --> {0}".format(command))
                        return_code = subprocess.call(command, shell=True)
                        if return_code == 0:
                            print("Upload successful...")
                            cache_items.append(item)
                            #add the item to the upload list
                            uploaded_items += 1
                        elif return_code < 0:
                            print("Child was terminated by signal: {0}".format(return_code))
                        else:
                            print("Child returned: {0}".format(return_code))

                    except OSError as error:
                        print("Execution failed: ")
                        print(error)
                cacher.setCache(cache_items)
                # now it'll only cache the successfully uploaded items
            else:
                # the directory creation process was not successful
                print("Upload failed because issues were encountered while trying"+
                     " to create the directory structure on the remote machine")
        os.chdir(oscurrent_working_directory)
        # switch it back to the initial working directory
    else:
        print("Some required configuration parameters have not been set...See below")
        print("*"*50)
        print("Identity File: {0}".format(identity_file))
        print("Source: {0}".format(src_path))
        print("Remote User: {0}".format(user))
        print("Hostname: {0}".format(host))
        print("Destination: {0}".format(dest))
        print("*"*50)
        print("Try adding the --help parameter: e.g. awsuploader --help")
