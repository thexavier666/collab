# The Collab system consisting of the frontend and the backend

# . : NOTE : .
# All comments starting with '##' are used for debugging purpose
# Disable the comments to see whether the modules are firing or not

import sys        # For argument list
import xmlrpclib  # For XMLRPC
import os         # For making directories
import threading  # For running the server in the background
import time       # For calling the sleep function
import hashlib    # For hashing node addresses & file names

import config     # For using constants

from SimpleXMLRPCServer import SimpleXMLRPCServer

class collab_system:

	def __init__(self, local_ip, local_port):
		# IP of the current machine
		self.local_ip       = local_ip

		# Port number at which the process is running
		self.local_port     = local_port

		# Amount of data uploaded by the current node (in bytes)
		self.upload_amt     = 1

		# Amounf of data downloaded by the current node (in bytes)
		self.download_amt   = 1

		# The ratio of the upload data to the downloaded data
		self.ratio          = 1

		# Path of the files which are hosted by the current node
		self.dir_hosted     = "collab_hosted" + "_" + local_ip + "_" + local_port

		# Path of the files which have been downloaded by the current node
		self.dir_downloaded = "collab_downloaded" + "_" + local_ip + "_" + local_port

		# A data structure which contains a list of file names
		# which are hosted by the current node and their hashed equiv
		self.file_dict      = {}

#----------------- Suman --------------------------------------------------------------
		##print "INIT Function"
		self.local_address  =  local_ip + ":" + local_port

		self.pred_pred 		=  local_ip + ":" + local_port
		self.pred          	=  local_ip + ":" + local_port
		self.succ  			=  local_ip + ":" + local_port
		self.succ_succ		=  local_ip + ":" + local_port
#----------------- Suman -----------------------------------------------------------------

	# These functions are used in the frontend

	def return_pause(self):
		"""Used for creating a pause during input"""

		raw_input("\n\tPress enter to continue ... ")

		return True

	def mod_file_download(self, file_name, remote_proxy):
		"""Sending details to remote node which will send file to local node"""

		hash_digest = self.mod_hash_string(file_name)

		download_file_size = remote_proxy.mod_file_download_transfer(hash_digest, self.local_port, self.ratio)

		if download_file_size == -1:
			return False
		else:
			self.download_amt = self.download_amt + download_file_size

			self.mod_update_ratio()

			return True

	def mod_file_upload(self, file_path, file_name, remote_proxy):
		"""Used for sending files to a receiver"""

		with open(file_path, "rb") as handle:
			bin_data = xmlrpclib.Binary(handle.read())

		if remote_proxy.mod_file_upload_receive(bin_data, file_name) == True:

			self.upload_amt = self.upload_amt + os.stat(file_path).st_size

			self.mod_update_ratio()

			return True

		else:
			return False

	def mod_show_stats(self):
		"""Shows all statistics of the current node"""

		print "\n\t\tUpload   (Bytes) : %d" % (self.upload_amt)
		print "\n\t\tDownload (Bytes) : %d" % (self.download_amt)
		print "\n\t\tCurrent ratio    : %f" % (self.ratio)

	def mod_show_files(self):
		"""Returns a list of files present in the current directory"""

		return self.file_dict.values()

	def mod_update_ratio(self):
		"""Updated the upload to download ratio"""

		self.ratio = (self.upload_amt * 1.0)/(self.download_amt * 1.0)

	# These functions are used in the backend

	def mod_file_upload_receive(self, bin_data, file_name):
		"""Used to receive a file upon a request of an upload"""

		##print "[mod_file_receive fired]"

		# File not present in node, thus upload can proceed
		if self.mod_hash_check_file(self.mod_hash_string(file_name)) == False:

			new_file_name = self.dir_hosted + "/" + file_name

			with open(new_file_name, "wb") as handle:
				handle.write(bin_data.data)

			# Adding the file name to the hashed list of files
			self.mod_file_dict_append(file_name)		

			return True
		else:

			return False

	def mod_file_download_transfer(self, given_hash, remote_port, remote_ratio):
		"""Initiating the file transfer"""

		##print "[mod_file_transfer fired]"

		self.mod_download_sleep(remote_ratio)

		# Checking if the file name hash actually exists
		file_name = self.mod_hash_check_file(given_hash)

		if file_name != False:

			# Creating path of local file about to be transferred
			file_path = self.dir_hosted + "/" + file_name

			with open(file_path, "rb") as handle:
				bin_data = xmlrpclib.Binary(handle.read())

			# Creating connection object of requestor
			remote_proxy = xmlrpclib.ServerProxy("http://localhost:" + remote_port + "/")
			
			# Connecting to requestor's server
			remote_proxy.mod_file_download_receive(bin_data, file_name)

			sent_file_size = os.stat(file_path).st_size

			self.upload_amt = self.upload_amt + sent_file_size

			# print "Something should be happening :( %d" % self.upload_amt

			self.mod_update_ratio()

			return sent_file_size
		else:
			return -1

	def mod_file_download_receive(self, bin_data, file_name):
		"""Used to receive a file upon request of a download"""

		##print "[mod_file_download_receive fired]"

		new_file_name = self.dir_downloaded + "/" + file_name

		with open(new_file_name, "wb") as handle:
			handle.write(bin_data.data)

		return True

	def mod_download_sleep(self, ratio):
		"""A function which delays the download according to the upload/download ratio"""

		sleep_time = 0

		# Ratio greater than 1
		if ratio > 1:
			sleep_time = 0

		# No download or upload done yet or ratio is exactly 1
		elif ratio == 1:
			sleep_time = config.SLEEP_TIME_LEVEL_DEF()

		# Ratio is less than 1
		elif ratio >= 0.1 and ratio < 1:
			sleep_time = config.SLEEP_TIME_LEVEL_1()

		elif ratio >= 0.01 and ratio < 0.1:
			sleep_time = config.SLEEP_TIME_LEVEL_2()

		elif ratio >= 0.001 and ratio < 0.01:
			sleep_time = config.SLEEP_TIME_LEVEL_3()

		else:
			sleep_time = config.SLEEP_TIME_LEVEL_4()

		##print "Sleep Time : %d" % self.mod_calc_sleep_time(ratio)
		time.sleep(sleep_time)

	# Hashing related functions

	def mod_file_dict_append(self, file_name):
		"""Appending file name and hashed file name to file dictionary"""

		hash_digest = self.mod_hash_string(file_name)

		self.file_dict[hash_digest] = file_name

	def mod_hash_string(self, given_str):
		"""A hashing function which hashes according to a predefined key space"""

		hash_digest = hashlib.sha1()
		hash_digest.update(given_str)

		return int(hash_digest.hexdigest(),16) % config.KEY_SPACE()

	def mod_hash_check_file(self, given_hash):
		"""A function which checks if a file is present in the hash list"""

		if self.file_dict.has_key(given_hash) == True:
			return self.file_dict[given_hash]

		else:
			return False

#----------------- Suman -------------------------------------------------------------------------
#----------------- call this function to get the finger table ------------------------------------
	def mod_get_finger_table(self):
		finger_table = {'pred_pred':self.pred_pred,'pred':self.pred,'succ':self.succ,'succ_succ':self.succ_succ}
		return finger_table
		
#----------------- call this function to get own hash value --------------------------------------
	def mod_get_own_hash(self):
		return int(self.mod_hash_string(self.local_address))
		
#----------------- call this function to get successor hash value --------------------------------
	def mod_get_succ_hash(self):
		return int(self.mod_hash_string(self.succ))
		
#----------------- call this function to get succ's succ hash value ------------------------------
	def mod_get_succ_succ_hash(self):
		return int(self.mod_hash_string(self.succ_succ))
		
#----------------- call this function to get pred hash value -------------------------------------
	def mod_get_pred_hash(self):
		return int(self.mod_hash_string(self.pred))
		
#----------------- call this function to get pred's pred hash value ------------------------------
	def mod_get_pred_pred_hash(self):
		return int(self.mod_hash_string(self.pred_pred))
		
#----------------- after own join pre_succ_table_stabilization ----------------------PRINT--------
	def pre_succ_table_stabilization(self,local_pre_succ_table):
		if int(self.mod_hash_string(self.succ)) != int(self.mod_hash_string(self.local_address)):
			#print "mod_join_update_table_succ"

			succ_add 		= (local_pre_succ_table['succ']).split(":")
			remote_proxy2 	= xmlrpclib.ServerProxy("http://" + str(succ_add[0]) + ":" + str(succ_add[1]) + "/")
			ll 				= remote_proxy2.mod_join_update_table_succ(self.local_address,local_pre_succ_table)

		if int(self.mod_hash_string(self.succ_succ)) != int(self.mod_hash_string(self.local_address)):
			#print "mod_join_update_table_succ_succ"

			succ_add 		= (local_pre_succ_table['succ_succ']).split(":")
			remote_proxy2 	= xmlrpclib.ServerProxy("http://" + str(succ_add[0]) + ":" + str(succ_add[1]) + "/")
			ll 				= remote_proxy2.mod_join_update_table_succ_succ(self.local_address,local_pre_succ_table)

		if int(self.mod_hash_string(self.pred)) != int(self.mod_hash_string(self.local_address)):
			#print "mod_join_update_table_pred"

			pred_add 		= (local_pre_succ_table['pred_pred']).split(":")
			remote_proxy2 	= xmlrpclib.ServerProxy("http://" + str(pred_add[0]) + ":" + str(pred_add[1]) + "/")
			ll 				= remote_proxy2.mod_join_update_table_pred(self.local_address,local_pre_succ_table)

		return "DONE"
#-------------------------------------------------------------------------------------------------
#----------------- successor table updation -----------------------------------------PRINT--------
	def mod_join_update_table_succ(self,remote_address,remote_address_table):
		self.pred 		= remote_address
		self.pred_pred 	= remote_address_table['pred']

		if self.succ == remote_address_table['pred']:
			self.succ_succ = remote_address

		##print self.local_address,self.pred_pred,self.pred,self.succ,self.succ_succ

		return True
#-------------------------------------------------------------------------------------------------
#----------------- successor's successor table updation -----------------------------PRINT--------
	def mod_join_update_table_succ_succ(self,remote_address,remote_address_table):
		self.pred_pred 	= remote_address

		if self.succ == remote_address_table['pred']:
			self.succ_succ = remote_address		

		##print self.local_address,self.pred_pred,self.pred,self.succ,self.succ_succ

		return True
#-------------------------------------------------------------------------------------------------
#----------------- predeccesor table updation ---------------------------------------PRINT--------
	def mod_join_update_table_pred(self,remote_address,remote_address_table):
		self.succ_succ 	= remote_address

		if self.pred == remote_address_table['succ']:
			self.pred_pred = remote_address

		##print self.local_address,self.pred_pred,self.pred,self.succ,self.succ_succ

		return True
#-------------------------------------------------------------------------------------------------
#----------------- update own information table -------------------------------------PRINT--------
	def own_update(self,own_succ_pre_table_update):
		self.pred 		= own_succ_pre_table_update['pred']
		self.pred_pred 	= own_succ_pre_table_update['pred_pred']
		self.succ 		= own_succ_pre_table_update['succ']
		self.succ_succ 	= own_succ_pre_table_update['succ_succ']

		##print "own_update end",self.pred_pred,self.pred,self.succ,self.succ_succ

		return True	
#-------------------------------------------------------------------------------------------------
#----------------- node join receive module ------------- (Main module)---------------------------
	def mod_join_recv(self,remote_address):
		##print "Received::, remote_address

		remote_succ_pred = {'pred_pred':self.local_address,'pred':self.local_address,'succ':self.local_address,'succ_succ':self.local_address}

		##print self.local_address, type(self.local_address)
		##print self.succ, type(self.succ)
		##print self.pred,type(self.pred) 

		#------------------------- if there is only a single node in the system -------------------------------------------
		if int(self.mod_hash_string(self.succ)) == int(self.mod_hash_string(self.local_address)) and int(self.mod_hash_string(self.pred)) == int(self.mod_hash_string(self.local_address)):

			if int(self.mod_hash_string(self.local_address)) > int(self.mod_hash_string(remote_address)):
				#print "local port:",type(self.local_port),"remote_address:",type(remote_address)
				##print "localport > remote port"

				self.pred 		= remote_address
				self.pred_pred 	= self.local_address
				self.succ 		= remote_address
				self.succ_succ 	= self.local_address

				remote_succ_pred['pred'] 		= self.local_address
				remote_succ_pred['pred_pred'] 	= remote_address
				remote_succ_pred['succ'] 		= self.local_address
				remote_succ_pred['succ_succ'] 	= remote_address

			elif int(self.mod_hash_string(self.local_address)) < int(self.mod_hash_string(remote_address)):
				#print "local port:",type(self.local_port),"remote_address:",type(remote_address)
				##print "locaport < remote port"

				self.pred 		= remote_address
				self.pred_pred 	= self.local_address
				self.succ 		= remote_address
				self.succ_succ 	= self.local_address

				remote_succ_pred['pred'] 		= self.local_address
				remote_succ_pred['pred_pred'] 	= remote_address
				remote_succ_pred['succ'] 		= self.local_address
				remote_succ_pred['succ_succ'] 	= remote_address

			##print self.pred_pred,self.pred,self.succ,self.succ_succ

			return remote_succ_pred
		#------------------------------------------------------------------------------------------------------------------

		#---------------------------- if more than one node in the system -------------------------------------------------
		else:
		#---------------------------- if the node is the left most node ---------------------------------------------------
			if (int(self.mod_hash_string(self.pred)) > int(self.mod_hash_string(self.local_address))) and (int(self.mod_hash_string(self.succ)) > int(self.mod_hash_string(self.local_address))) :
				##print "edge case 1"

				if (int(self.mod_hash_string(remote_address)) > int(self.mod_hash_string(self.local_address))) and (int(self.mod_hash_string(remote_address)) < int(self.mod_hash_string(self.succ))) :
					##print remote_address,"lies between me and my succssor"

					remote_succ_pred['pred'] 		= self.local_address
					remote_succ_pred['pred_pred'] 	= self.pred
					remote_succ_pred['succ'] 		=  self.succ
					remote_succ_pred['succ_succ'] 	= self.succ_succ

					if int(self.mod_hash_string(self.pred)) == int(self.mod_hash_string(remote_succ_pred['succ'])):
						self.pred_pred = remote_address

					self.succ 		= remote_address
					self.succ_succ 	= remote_succ_pred['succ']

				elif int(self.mod_hash_string(remote_address)) > int(self.mod_hash_string(self.succ)):
					##print remote_address,"greater than my succsseor"

					succ_add 			= (self.succ).split(":")
					remote_proxy2 		= xmlrpclib.ServerProxy("http://" + str(succ_add[0]) + ":" + str(succ_add[1]) + "/")
					ll 					= remote_proxy2.mod_join_recv(remote_address)
					remote_succ_pred 	= ll

				elif int(self.mod_hash_string(remote_address)) < int(self.mod_hash_string(self.local_address)):
					##print remote_address,"less than mine"
					pred_add 			= (self.pred).split(":")
					remote_proxy2 		= xmlrpclib.ServerProxy("http://" + str(pred_add[0]) + ":" + str(pred_add[1]) + "/")
					ll 					= remote_proxy2.mod_join_recv(remote_address)
					remote_succ_pred 	= ll

				##print self.pred_pred,self.pred,self.succ,self.succ_succ

				return remote_succ_pred
			#---------------------------- if the node is the right most node ----------------------------------------------
			elif int(self.mod_hash_string(self.pred)) < int(self.mod_hash_string(self.local_address)) and int(self.mod_hash_string(self.succ)) < int(self.mod_hash_string(self.local_address)):
				##print "edge case 2"
					
				if( int(self.mod_hash_string(remote_address)) > int(self.mod_hash_string(self.local_address))) or ((int(self.mod_hash_string(remote_address)) < int(self.mod_hash_string(self.local_address))) and (int(self.mod_hash_string(remote_address)) < int(self.mod_hash_string(self.succ)))):
					##print remote_address,"greater than mine or less than mine and my succ"

					remote_succ_pred['pred'] 		= self.local_address
					remote_succ_pred['pred_pred'] 	= self.pred
					remote_succ_pred['succ'] 		= self.succ
					remote_succ_pred['succ_succ'] 	= self.succ_succ

					if int(self.mod_hash_string(self.pred)) == int(self.mod_hash_string(remote_succ_pred['succ'])):
						self.pred_pred = remote_address

					self.succ 		= remote_address
					self.succ_succ 	= remote_succ_pred['succ']
					##print self.pred_pred,self.pred,self.succ,self.succ_succ

				elif (int(self.mod_hash_string(remote_address)) < int(self.mod_hash_string(self.local_address))):
					##print remote_address,"less than mine"

					pred_add 			= (self.pred).split(":")
					remote_proxy2 		= xmlrpclib.ServerProxy("http://" + str(pred_add[0]) + ":" + str(pred_add[1]) + "/")
					ll 					= remote_proxy2.mod_join_recv(remote_address)
					remote_succ_pred 	= ll

				return remote_succ_pred
			#---------------------------- if the node is the intermediate node --------------------------------------------
			else:
				##print "Main case"

				if (int(self.mod_hash_string(remote_address)) > int(self.mod_hash_string(self.local_address)) and int(self.mod_hash_string(remote_address)) < int(self.mod_hash_string(self.succ)) ):
					##print remote_address,"lies between me and my succssor"

					remote_succ_pred['pred'] 		= self.local_address
					remote_succ_pred['pred_pred'] 	= self.pred
					remote_succ_pred['succ'] 		=  self.succ
					remote_succ_pred['succ_succ'] 	= self.succ_succ

					if int(self.mod_hash_string(self.pred)) == int(self.mod_hash_string(remote_succ_pred['succ'])):
						self.pred_pred = remote_address

					self.succ 		= remote_address
					self.succ_succ 	= remote_succ_pred['succ']

				elif int(self.mod_hash_string(remote_address)) < int(self.mod_hash_string(self.local_address)):
					##print remote_address,"less than mine"

					pred_add 			= (self.pred).split(":")
					remote_proxy2 		= xmlrpclib.ServerProxy("http://" + str(pred_add[0]) + ":" + str(pred_add[1]) + "/")
					ll 					= remote_proxy2.mod_join_recv(remote_address)
					remote_succ_pred 	= ll

				elif int(self.mod_hash_string(remote_address)) > int(self.mod_hash_string(self.succ)):
					##print remote_address,"greater than my succssor"

					succ_add 			= (self.succ).split(":")
					remote_proxy2 		= xmlrpclib.ServerProxy("http://" + str(succ_add[0]) + ":" + str(succ_add[1]) + "/")
					ll 					= remote_proxy2.mod_join_recv(remote_address)
					remote_succ_pred 	= ll

				##print self.pred_pred,self.pred,self.succ,self.succ_succ
				return remote_succ_pred

#----------------- node requesting for join -----------------------------------------PRINT--------
	def mod_join_req(self,master_ip,master_port):
		remote_proxy1 = xmlrpclib.ServerProxy("http://" + str(master_ip) + ":" + str(master_port) + "/")

		#local_address = self.local_ip+":"+self.local_port
		##print self.local_address," HASH ", int(self.mod_hash_string(self.local_address))

		pp = remote_proxy1.mod_join_recv(self.local_address)

		self.pred 		= pp['pred']
		self.pred_pred 	= pp['pred_pred']
		self.succ 		= pp['succ']
		self.succ_succ 	= pp['succ_succ']

		#remote_proxy2 = xmlrpclib.ServerProxy("http://" + self.local_ip + ":" + str(self.local_port) + "/")
		#kk = remote_proxy2.own_update(pp)
		##print "Node join req end",self.pred_pred,self.pred,self.succ,self.succ_succ

		mm = self.pre_succ_table_stabilization(pp)

		return mm				
#----------------- Suman -------------------------------------------------------------------------

def main():
	# Details of current node
	local_ip = "localhost"
	local_port = sys.argv[1]

	# Creating the local object
	local_node = collab_system(local_ip, local_port)

	# Declared an XMLRPC server
	# This is the listener part of the application
	local_listener = SimpleXMLRPCServer((local_ip, int(local_port)), logRequests = False, allow_none = True)
	
	##print "[Listening on port : %s]" % local_port

	local_listener.register_introspection_functions()
	local_listener.register_multicall_functions()
	local_listener.register_instance(local_node)

	# Initialized the XMLRPC server in a seperate thread
	server_thread = threading.Thread(target = local_listener.serve_forever)

	# Making the server thread a daemon process so that the server dies when the
	# client exits the front end
	server_thread.daemon = True

	# Starting the server thread
	server_thread.start()

	if len(sys.argv) == 3:
		# Details of master node
		master_ip 	= "localhost"
		master_port = sys.argv[2]

		pred_succ 	= local_node.mod_join_req(master_ip,master_port)

		##print pred_succ

	# Creating connection details of remote node
	# remote_proxy = xmlrpclib.ServerProxy("http://" + remote_ip + ":" + remote_port + "/")

	# Creating the directory which will contain all hosted files
	os.makedirs(local_node.dir_hosted)

	# Creating the directory which will contain all downloaded files
	os.makedirs(local_node.dir_downloaded)

	# local_node.return_pause()

	while True:
		os.system('clear')

		print "\n\n\t. : Collab Menu for %s : .\n" % local_port

		print "\t|HASH VALUE| : %d\n" % local_node.mod_hash_string(local_node.local_address) 

		print "\tSearch & download      ...[1]"
		print "\tUpload                 ...[2]"
		print "\tAdmin Menu             ...[3]"
		print "\tExit                   ...[0]"

		input_val = raw_input("\n\n\tEnter option : ")

		if input_val == "1":
			file_name = raw_input("\n\tEnter name of file to be downloaded : ")

			file_lookup = local_node.mod_file_download(file_name, remote_proxy)

			if file_lookup == False:
				print "\n\tFile not found at remote node!"

			else:
				print "\n\tFile downloaded!"

			local_node.return_pause()
			
		elif input_val == "2":
			file_name = raw_input("\n\tEnter name of file to be uploaded : ")

			# Creaating path of local file about to be uploaded
			file_path = "./" + file_name

			if os.path.exists(file_path) == True:
				local_node.mod_file_upload(file_path, file_name, remote_proxy)

				print "\n\tFile uploaded!"
			else:
				print "\n\tFile not found at current node!"

			local_node.return_pause()

		elif input_val == "3":
			while True:
				os.system('clear')

				print "\n\n\t. : Admin Menu for %s : .\n" % local_port

				print "\t|HASH VALUE| : %d\n" % local_node.mod_hash_string(local_node.local_address) 

				print "\tSee finger table       ...[1]"
				print "\tSee local files        ...[2]"
				print "\tSee query cache        ...[3]"
				print "\tSee statistics         ...[4]"
				print "\t<< Back <<             ...[0]"

				admin_inp_val = raw_input("\n\n\tEnter option : ")

				if admin_inp_val == "1":
					print "\n\n\t. : Finger Table : .\n"

					print "\t\tPredecessor's predeccesor : ", local_node.pred_pred 
					print "\t\tPredecessor               : ", local_node.pred
					print "\t\tSuccessor                 : ", local_node.succ
					print "\t\tSuccessor's successor     : ", local_node.succ_succ

					local_node.return_pause()

				elif admin_inp_val == "2":

					file_list = local_node.mod_show_files()

					if file_list:
						print "\n\tThe files are...\n"

						for files in file_list:
							print "\t\t%s" % files
					else:
						print "\n\tThe current directory is empty...\n"

					local_node.return_pause()

				elif admin_inp_val == "3":
					local_node.return_pause()

				elif admin_inp_val == "4":
					local_node.mod_show_stats()
					local_node.return_pause()

				elif admin_inp_val == "0":
					break

				else:
					print "\tIncorrect option value"
					print "\tTry again..."
					local_node.return_pause()

		elif input_val == "0":
			print "\n\tThank you for using Collab!"
			local_node.return_pause()
			
			break

		else:
			print "\n\tIncorrect option value"
			print "\n\tTry again..."
			local_node.return_pause()

	os.system('clear')

if __name__ == '__main__':
	main()