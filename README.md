# collab
An Incentive Based P2P Distributed File Storage System

## Current features
 * Can connect to another node but in the same machine
 * Can upload and download files from each other
 * Upload to download ratio

## How to run the scripts in mod_main
 * Run the following two commands for each node
 * python collab_listener port_number
 * python collab_client port_number
 * Inside collab_client, enter remote port as the port ID of the other node. Currently, the system supports pair wise connections
 * Upload download files should be in the same directory

## To do
 * [Done] Currently, this is the upload module. Meaning, the client gives a command to upload to a server. The next aim is to download a file which is residing in the server
 * [Done] Upload to download ratio
 * [To be done] Incentive/penalty based on ratio
 * [To be done] Add support to work from another machine (very easy)
 * [To be done] Sleep based on ratio
 * [Dropped] Adding a download bar/current speed

## [Defunct] How to run the scripts in mod_fileTransfer
 * python fileTransfer_download.py
 * python fileTransfer_upload.py "file name" "sleep time in milisecond"
 * Run the above two commands without the quotes
 * The file should be in the current directory