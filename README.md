AWS FileSync/Uploader for Ubuntu
================================

A python script that handles file uploads to an EC2 instance requiring very little configuration

## Command-Line Options
This section specifies the command line options for the script    

``` 
usage: awsuploader [-h] [-s SRC] [-d DEST] [-u USER] [-i IDENTITY_FILE] [--host HOST]

Runs an upload using the `scp` command and uploads file[s] to an EC2 instance

optional arguments:
  -h, --help            show this help message and exit
  -s SRC, --src SRC     Specify the source directory to be uploaded
  -d DEST, --dest DEST  Specify the directory on the EC2 instance where the
                        src is to be uploaded to
  -u USER, --user USER  Specify the username to be used in connecting with the
                        EC2 instance
  -i IDENTITY_FILE, --identity_file IDENTITY_FILE
                        Specify the path to the .pem file to be used with the
                        instance
  --host HOST           Specify the public IP address to the EC2 instance
```

### Notes    
When specifying paths (For example: to the ```identity_file```) try to avoid using **relative paths**.     
