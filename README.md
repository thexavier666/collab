# collab
Collab : An Incentive Based P2P Distributed File Storage System

## How to run the scripts in mod_main
 * Run the following two commands
 * python collab_server (Currently, it will run at localhost at port 9000)
 * python collab_client (A CUI menu-driven program)
 * The file should be in the current directory
 * Custom speed has not been implemented

## How to run the scripts in mod_fileTransfer
 * python fileTransfer_download.py
 * python fileTransfer_upload.py "file name" "sleep time in milisecond"
 * Run the above two commands without the quotes
 * The file should be in the current directory

## To do
 * Currently, this is the upload module. Meaning, the client gives a command to upload to a server. The next aim is to download a file which is residing in the server
 * Adding a download bar/current speed
