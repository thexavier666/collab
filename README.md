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
 * [Done] Download from remote
 * [Done] Upload to download ratio
 * [Done] Incentive/penalty based on ratio
 * [Done] Sleep based on ratio
 * [To be done] Add support to work from another machine (very easy)
 * [Dropped] Adding a download bar/current speed

## [Defunct][Removed] How to run the scripts in mod_fileTransfer
 * python fileTransfer_download.py
 * python fileTransfer_upload.py "file name" "sleep time in milisecond"
 * Run the above two commands without the quotes
 * The file should be in the current directory
