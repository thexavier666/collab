# collab
An Incentive Based P2P Distributed File Storage System

### Current features
* Can connect to another node but in the same machine
* Can upload and download files from each other
* Can view list of files which are hosted by the current node
* Incentive and penalty based on upload to download ratio

### Changelog
* Added a hash function which takes a string and a key space as input and returns a number. Key space is defined in the config file
* Made the application as a single file
* Added a configuration file named `config.py` which consists of getter functions of different constants which are used by the various components of the system
* Daemonized the listener thread
* All downloads will take place in the current directory of the application while the uploads are saved in the collab directory
* Integration of hash function
* Made a dictionary of files stored in the current node
* Upload and download amounts now currently reflect what actually happens
* Made the sleep function simpler
* Added more comments to the constructor and the import section
* Downloads now take place in separate folders
* Updated README files with individual responsibilities
* Added a shell script which will delete all folders created due to the system

### How to run Collab
* Run the following command for each node
* `python collab.py port_number`
* Inside the application, enter remote port as the port ID of the other node. Currently, the system supports pair wise connections
* After running the application and exiting it, run the shell script `del.sh`

### To do (Sumitro)
* [ ] Add support to work from another machine (very easy)
* [x] Kill the server running in the background nicely
* [x] Integrate the hash function in the upload and download function
* [x] Put the downloaded files in a separate folder so that these files are not hosted
* [x] Fix the bug where remote downloads are not counted as uploads by the remote server
* [x] Data structure (Dictionary) of files downloaded at current node

### To do (Suman)
* [x] Node join
* [ ] Node join with proper successor in the shape of a ring
* [ ] Node stabilize
* [ ] Node finger table
* [ ] Displaying the menu

### To do (Midhun)
* [ ] Local search
* [ ] Node leave

### To do (Sourav)
* [ ] Global search
* [ ] Node leave
