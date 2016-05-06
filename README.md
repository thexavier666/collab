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
* Incentive and penalty based on upload to download ratio
* Any node can be leader
* Redundant links in both forward and backward directions
* An implementation of cached queries so that repeat queries are processed faster
* Has an administrative menu which has lots of features to see the workings of the system like
  * See list of files which are hosted by itself
  * See list of files which are downloaded by itself
  * See finger table
  * See cache

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

### Note
The application takes the IP address according to a string-based script. Currently, it's set to take the IP address of the interface named `em1`. In a later update, it will be configurable by editing the config file
