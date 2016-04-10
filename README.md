# collab
An Incentive Based P2P Distributed File Storage System

## Current features
 * Can connect to another node but in the same machine
 * Can upload and download files from each other
 * Can view list of files which are hosted by the current node
 * Incentive and penalty based on upload to download ratio

## Changelog
 * Added a hash function which takes a string and a key space as input and returns a number. Key space is defined in the config file
 * Made the application as a single file
 * Added a configuration file named 'config.py' which consists of getter functions of different constants which are used by the various components of the system
 * Daemonized the listener thread
 * All downloads will take place in the current directory of the application while the uploads are saved in the collab directory
 * Integration of hash function
 * Made a dictionary of files stored in the current node
 * Upload and download amounts now currently reflect what actually happens

## How to run Collab
 * Run the following command for each node
 * python collab.py port_number
 * Inside the application, enter remote port as the port ID of the other node. Currently, the system supports pair wise connections

## To do
 * [To be done] Add support to work from another machine (very easy)
 * [Done] Kill the server running in the background nicely
 * [Done] Integrate the hash function in the upload and download function
 * [Done] Put the downloaded files in a separate folder so that these files are not hosted
 * [Done] Fix the bug where remote downloads are not counted as uploads by the remote server
 * [Done] Data structure (Dictionary) of files downloaded at current node
