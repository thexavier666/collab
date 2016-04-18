# collab
An Incentive Based Self Stabilizing P2P File Storage System. Developed by a team from IIT Kharagpur as a term project for the subject 'Distributed Systems' during the Spring 2016 session

### Developers
* Suman Mondal
* Sourav Bhattacharjee
* Midhun George
* Sumitro Bhaumik

### Features
* Nodes join together in the shape of a ring
* The ring can tolerate upto 1 fault
* Can upload and download files from each other
* Current node can view list of files which are hosted by itself
* Current node can view list of files which are downloaded by itself
* Incentive and penalty based on upload to download ratio
* Any node can be leader
* Redundant links in both forward and backward directions
* An implementation of cached queries so that repeat queries are processed faster

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
* Huge update from Suman. I made some purely cosmetic changes to Suman's code

### How to start the Collab system
* Run the following command for each node
* `python collab.py` for the first node
* `python collab.py IP_ADDRESS` where `IP_ADDRESS` can be the IP of node which has already joined the system

### To do (Sumitro)
* [x] Add support to work from another machine (very easy)
* [x] Node stabilize
* [x] Integration
* [x] Kill the server running in the background nicely
* [x] Integrate the hash function in the upload and download function
* [x] Put the downloaded files in a separate folder so that these files are not hosted
* [x] Fix the bug where remote downloads are not counted as uploads by the remote server
* [x] Data structure (Dictionary) of files downloaded at current node

### To do (Suman)
* [x] Node join
* [x] Node join with proper successor in the shape of a ring
* [x] Node finger table
* [x] Displaying the menu
* [x] Node leave

### To do (Midhun)
* [x] Global upload
* [x] Global search
* [x] Local search

### To do (Sourav)
* [x] Global search
* [x] Cache implementation