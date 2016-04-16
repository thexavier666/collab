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

#----------------- Sourav --------------------------------------------------------------
import Queue
import thread
import datetime
import shutil
#----------------- Sourav --------------------------------------------------------------

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
		self.local_address  = local_ip + ":" + local_port

		self.pred_pred 		= local_ip + ":" + local_port
		self.pred          	= local_ip + ":" + local_port
		self.succ  			= local_ip + ":" + local_port
		self.succ_succ		= local_ip + ":" + local_port
#----------------- Suman --------------------------------------------------------------

#----------------- Sourav --------------------------------------------------------------
		self.cache			= {}
		self.q 				= Queue.Queue()
		self.lock 			= thread.allocate_lock()
#----------------- Sourav --------------------------------------------------------------

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

		return self.file_dict

	def mod_show_downloaded_files(self):
		""""""

		return os.listdir(self.dir_downloaded)

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

	def mod_file_download_transfer(self, given_hash, remote_ip, remote_port, remote_ratio):
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
			remote_proxy = xmlrpclib.ServerProxy("http://" + remote_ip + ":" + remote_port + "/")
			
			# Connecting to requestor's server
			remote_proxy.mod_file_download_receive(bin_data, file_name)

			sent_file_size = os.stat(file_path).st_size

			self.upload_amt = self.upload_amt + sent_file_size

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

		time.sleep(sleep_time)

	def mod_file_stabilize_req(self):

		curr_pred = self.mod_get_pred_hash()

		remote_proxy = xmlrpclib.ServerProxy("http://" + self.pred + "/")

		tmp_dict = self.file_dict

		file_list = []
		file_hash = []

		for key in tmp_dict:

			if key < curr_pred:

				file_path = self.dir_hosted + "/" + tmp_dict[key]

				with open(file_path, "rb") as handle:
					bin_data = xmlrpclib.Binary(handle.read())

				remote_proxy.mod_file_upload_receive(bin_data, tmp_dict[key])

				file_list.append(file_path)

				file_hash.append(key)

		for files in file_list:	
			os.remove(files)

		for files in file_hash:
			self.file_dict.pop(files, None)

	# Hashing related functions

	def mod_file_dict_append(self, file_name):
		"""Appending file name and hashed file name to file dictionary"""

		hash_digest = self.mod_hash_string(file_name)

		self.file_dict[hash_digest] = file_name

	def mod_hash_string(self, given_str):
		"""A hashing function which hashes according to a predefined key space"""

		hash_digest = hashlib.sha1()
		hash_digest.update(given_str)

		return int(hash_digest.hexdigest(), 16) % config.KEY_SPACE()

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
		"""get own hash value"""

		return int(self.mod_hash_string(self.local_address))
		
#----------------- call this function to get successor hash value --------------------------------
	def mod_get_succ_hash(self):
		"""get successor hash value"""
		return int(self.mod_hash_string(self.succ))
		
#----------------- call this function to get succ's succ hash value ------------------------------
	def mod_get_succ_succ_hash(self):
		"""get succ's succ hash value"""

		return int(self.mod_hash_string(self.succ_succ))
		
#----------------- call this function to get pred hash value -------------------------------------
	def mod_get_pred_hash(self):
		"""get pred hash value"""

		return int(self.mod_hash_string(self.pred))
		
#----------------- call this function to get pred's pred hash value ------------------------------
	def mod_get_pred_pred_hash(self):
		"""get pred's pred hash value"""

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

		return True

#----------------- successor table updation -----------------------------------------PRINT--------
	def mod_join_update_table_succ(self,remote_address,remote_address_table):
		self.pred 		= remote_address
		self.pred_pred 	= remote_address_table['pred']

		if self.succ == remote_address_table['pred']:
			self.succ_succ = remote_address

		return True

#----------------- successor's successor table updation -----------------------------PRINT--------
	def mod_join_update_table_succ_succ(self,remote_address,remote_address_table):
		self.pred_pred 	= remote_address

		if self.succ == remote_address_table['pred']:
			self.succ_succ = remote_address		

		return True

#----------------- predeccesor table updation ---------------------------------------PRINT--------
	def mod_join_update_table_pred(self,remote_address,remote_address_table):
		self.succ_succ 	= remote_address

		if self.pred == remote_address_table['succ']:
			self.pred_pred = remote_address

		return True

#----------------- update own information table -------------------------------------PRINT--------
	def own_update(self,own_succ_pre_table_update):
		self.pred 		= own_succ_pre_table_update['pred']
		self.pred_pred 	= own_succ_pre_table_update['pred_pred']
		self.succ 		= own_succ_pre_table_update['succ']
		self.succ_succ 	= own_succ_pre_table_update['succ_succ']

		return True	

#----------------- node join receive module ------------- (Main module)---------------------------
	def mod_join_recv(self,remote_address):
		##print "Received::, remote_address

		remote_succ_pred = {'pred_pred':self.local_address,'pred':self.local_address,'succ':self.local_address,'succ_succ':self.local_address} 

		#------------------------- if there is only a single node in the system -------------------------------------------
		if int(self.mod_hash_string(self.succ)) == int(self.mod_hash_string(self.local_address)) and int(self.mod_hash_string(self.pred)) == int(self.mod_hash_string(self.local_address)):

			if int(self.mod_hash_string(self.local_address)) > int(self.mod_hash_string(remote_address)):

				self.pred 		= remote_address
				self.pred_pred 	= self.local_address
				self.succ 		= remote_address
				self.succ_succ 	= self.local_address

				remote_succ_pred['pred'] 		= self.local_address
				remote_succ_pred['pred_pred'] 	= remote_address
				remote_succ_pred['succ'] 		= self.local_address
				remote_succ_pred['succ_succ'] 	= remote_address

			elif int(self.mod_hash_string(self.local_address)) < int(self.mod_hash_string(remote_address)):

				self.pred 		= remote_address
				self.pred_pred 	= self.local_address
				self.succ 		= remote_address
				self.succ_succ 	= self.local_address

				remote_succ_pred['pred'] 		= self.local_address
				remote_succ_pred['pred_pred'] 	= remote_address
				remote_succ_pred['succ'] 		= self.local_address
				remote_succ_pred['succ_succ'] 	= remote_address

			return remote_succ_pred

		#---------------------------- if more than one node in the system -------------------------------------------------
		else:
		#---------------------------- if the node is the left most node ---------------------------------------------------
			if (int(self.mod_hash_string(self.pred)) > int(self.mod_hash_string(self.local_address))) and (int(self.mod_hash_string(self.succ)) > int(self.mod_hash_string(self.local_address))) :
				##print "edge case 1"

				if (int(self.mod_hash_string(remote_address)) > int(self.mod_hash_string(self.local_address))) and (int(self.mod_hash_string(remote_address)) < int(self.mod_hash_string(self.succ))) :
					##print remote_address,"lies between me and my succssor"

					remote_succ_pred['pred'] 	= self.local_address
					remote_succ_pred['pred_pred'] 	= self.pred
					remote_succ_pred['succ'] 	=  self.succ
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

				return remote_succ_pred

#----------------- node requesting for join -----------------------------------------PRINT--------
	def mod_join_req(self,master_ip,master_port):
		remote_proxy1 = xmlrpclib.ServerProxy("http://" + str(master_ip) + ":" + str(master_port) + "/")

		pp = remote_proxy1.mod_join_recv(self.local_address)

		self.pred 		= pp['pred']
		self.pred_pred 	= pp['pred_pred']
		self.succ 		= pp['succ']
		self.succ_succ 	= pp['succ_succ']

		mm = self.pre_succ_table_stabilization(pp)

		#----------------- [Sumitro] -------------------------------------------------------------

		remote_proxy = xmlrpclib.ServerProxy("http://" + self.succ + "/")

		remote_proxy.mod_file_stabilize_req()

		#----------------- [Sumitro] -------------------------------------------------------------
		return mm

#----------------- Probe sending ---------------------------------------------------------NEW-----
	def mod_prob_sent(self):
		succ_add = (self.succ).split(":")
		try:
			remote_proxy2 	= xmlrpclib.ServerProxy("http://" + str(succ_add[0]) + ":" + str(succ_add[1]) + "/")
			ll 				= remote_proxy2.mod_prob_recv()

		except:
			##print self.local_address,"My succ has died"

			self.succ 		= self.succ_succ
			finger_table 	= {'pred_pred':self.pred_pred,'pred':self.pred,'succ':self.succ,'succ_succ':self.succ_succ}
			succ_add 		= (self.succ).split(":")
			remote_proxy2 	= xmlrpclib.ServerProxy("http://" + str(succ_add[0]) + ":" + str(succ_add[1]) + "/")
			ll 				= remote_proxy2.mod_stabilize_succ(self.local_address,finger_table)
			self.succ_succ 	= ll
			
			finger_table 	= {'pred_pred':self.pred_pred,'pred':self.pred,'succ':self.succ,'succ_succ':self.succ_succ}
			succ_succ_add 	= (self.succ_succ).split(":")
			remote_proxy2 	= xmlrpclib.ServerProxy("http://" + str(succ_succ_add[0]) + ":" + str(succ_succ_add[1]) + "/")
			ll 				= remote_proxy2.mod_stabilize_succ_succ(self.local_address,finger_table)
			
			finger_table 	= {'pred_pred':self.pred_pred,'pred':self.pred,'succ':self.succ,'succ_succ':self.succ_succ}
			pred_add 		= (self.pred).split(":")
			remote_proxy2 	= xmlrpclib.ServerProxy("http://" + str(pred_add[0]) + ":" + str(pred_add[1]) + "/")
			ll 				= remote_proxy2.mod_stabilize_pred(self.local_address,finger_table)

#----------------- succ stabilization function after node left ---------------------------NEW-----
	def mod_stabilize_succ(self,remote_address,remote_finger_table):
		self.pred 		= remote_address
		self.pred_pred 	= remote_finger_table['pred']

		return self.succ	

#----------------- succ's succ stabilization function after node left --------------------NEW-----
	def mod_stabilize_succ_succ(self,remote_address,remote_finger_table):
		self.pred_pred = remote_address

		return True

#----------------- succ's succ stabilization function after node left --------------------NEW-----
	def mod_stabilize_pred(self,remote_address,remote_finger_table):
		self.succ_succ = remote_finger_table['succ']

		return True

#----------------- probling recv message -------------------------------------------------NEW-----
	def mod_prob_recv(self):
		"""probling recv message"""

		return True

#-----------------------------------------------------------------------------------------NEW-----
	def mod_prob(self):
		while(1):
			self.mod_prob_sent()
			time.sleep(config.DEF_PROBE_TIME())

#----------------- call this function to get the address corresponding to hash value -------------
	def mod_get_address(self,hash_value):
		address_table = [self.local_address, self.pred_pred,self.pred,self.succ,self.succ_succ]

		for i in address_table:

			if int(self.mod_hash_string(i)) == int(hash_value):
				address = i.split(":")

				break

		return address

#----------------- Suman -----------------------------------------------------------------NEW-----

#----------------- Sourav & Midhun----------------------------------------------------------------
#----------------- Cache to store previous downloads in each node --------------------------------
	def mod_cache_update(self,file_hash, actual_ip, actual_port):

		if len(self.cache) == 50:
			del_item=self.q.get()

			self.lock.acquire()
			del self.cache[del_item]
			self.lock.release()

		self.lock.acquire()

		showtime 				= datetime.datetime.now().strftime("%d-%m-%Y:%H-%M-%S")
		cache_list				= [actual_ip, actual_port, showtime]
		self.cache[file_hash]	= cache_list

		self.q.put(file_hash)
		self.lock.release()

#----------------- Insert Comment ----------------------------------------------------------------
	def mod_check_cache_validity(self,file_hash):

		if self.cache.has_key(file_hash):
			
			ttl_live = format((datetime.datetime.strptime(self.cache.get(file_hash)[2],"%d-%m-%Y:%H-%M-%S" )+ datetime.timedelta(seconds=config.DEF_CACHE_TIMEOUT())), '%d-%m-%Y:%H-%M-%S')

			if ttl_live < format(datetime.datetime.now(),'%d-%m-%Y:%H-%M-%S'):
				self.lock.acquire()
				del self.cache[file_hash]
				self.lock.release()

				return False

			else:
				log_file_name = "log_" + self.local_ip + "_" + self.local_port + ".txt"

				fp = open(log_file_name,"a")
				fp.write("NODE " + self.local_ip + " : " + self.local_port + " | DOWNLOAD FILE HASH : " + str(file_hash) + " | TIME : " + str(datetime.datetime.now().strftime("%d-%m-%Y:%H-%M-%S")))
				fp.close()

				return True

		else:
			return False

#----------------- searching if the file is present in the node ----------------------------------
	def mod_file_is_present(self,file_hash):
		# just have to check whether the file_dict(file_hash,file_name) contains the file_hash or not.
		# add map in class
		return self.file_dict.has_key(file_hash)

	# This function invoke from the mod_search if local node does not contain the file
	# returns a list containing list[IP,PORT] of the node contains the file. Otherwise returns list[0,0]

	def mod_rpc_search(self, file_hash):

		if (file_hash < self.mod_get_own_hash() or file_hash > self.mod_get_pred_hash()) and self.mod_get_own_hash() < self.mod_get_pred_hash() and self.mod_get_own_hash() < self.mod_get_succ_hash():
			#if file_hash < self.mod_get_own_hash() and self.mod_get_pred_hash() > self.mod_get_own_hash():
			#it is with me
			if self.mod_file_is_present(file_hash):
				actual_ip 	= self.mod_get_address( self.mod_get_own_hash() )[0]
				actual_port	= self.mod_get_address( self.mod_get_own_hash() )[1]
			else:
				actual_ip	= 0
				actual_port	= 0

			actual_list = [actual_ip,actual_port]

		elif file_hash > self.mod_get_pred_hash() and file_hash < self.mod_get_own_hash():
			#it is with me
			if self.mod_file_is_present(file_hash):
				actual_ip	= self.mod_get_address( self.mod_get_own_hash() )[0]
				actual_port	= self.mod_get_address( self.mod_get_own_hash() )[1]

			else:
				actual_ip	= 0
				actual_port	= 0

			actual_list = [actual_ip,actual_port]

		elif file_hash < self.mod_get_pred_hash():
			remote_proxy1 	= xmlrpclib.ServerProxy("http://" + self.mod_get_address(self.mod_get_pred_hash())[0] + ":" + self.mod_get_address(self.mod_get_pred_hash())[1] + "/")
			actual_list		= remote_proxy1.mod_rpc_search(file_hash)

		else:
			remote_proxy1 	= xmlrpclib.ServerProxy("http://" + self.mod_get_address(self.mod_get_succ_hash())[0] + ":" + self.mod_get_address(self.mod_get_succ_hash())[1] + "/")
			actual_list		= remote_proxy1.mod_rpc_search(file_hash)

		return actual_list

#------------------ Returns true on successful file download, otherwise false --------------------
	def mod_search(self, file_hash):

		actual_ip 	= 0
		actual_port = 0

		if self.mod_check_cache_validity(file_hash):
			actual_ip 	= self.cache.get(file_hash)[0]
			actual_port = self.cache.get(file_hash)[1]

		else:
			if (file_hash < self.mod_get_own_hash() or file_hash > self.mod_get_pred_hash()) and self.mod_get_own_hash() < self.mod_get_pred_hash() and self.mod_get_own_hash() < self.mod_get_succ_hash():

				if self.mod_file_is_present(file_hash):
					actual_ip	= self.mod_get_address( self.mod_get_own_hash() )[0]
					actual_port	= self.mod_get_address( self.mod_get_own_hash() )[1]

				else:
					actual_ip	= 0
					actual_port	= 0

			elif file_hash > self.mod_get_pred_hash() and file_hash < self.mod_get_own_hash():
				#it is with me

				if self.mod_file_is_present(file_hash):
					actual_ip	= self.mod_get_address( self.mod_get_own_hash() )[0]
					actual_port	= self.mod_get_address( self.mod_get_own_hash() )[1]

				else:
					actual_ip	= 0
					actual_port	= 0

			elif file_hash < self.mod_get_pred_hash() and self.mod_get_own_hash() != self.mod_get_pred_hash():
				remote_proxy1 	= xmlrpclib.ServerProxy("http://" + self.mod_get_address(self.mod_get_pred_hash())[0]+ ":" + self.mod_get_address(self.mod_get_pred_hash())[1] + "/")
				actual_list		= remote_proxy1.mod_rpc_search(file_hash)

				actual_ip		= actual_list[0]
				actual_port		= actual_list[1]

			elif file_hash >= self.mod_get_own_hash() and self.mod_get_own_hash() != self.mod_get_succ_hash():
				remote_proxy1 	= xmlrpclib.ServerProxy("http://" + self.mod_get_address(self.mod_get_succ_hash())[0] + ":" + self.mod_get_address(self.mod_get_succ_hash())[1] + "/")
				actual_list		= remote_proxy1.mod_rpc_search(file_hash)

				actual_ip		= actual_list[0]
				actual_port		= actual_list[1]

		#---------- Downloading File-----------------------------------------------------------
		if actual_ip == 0 and actual_port == 0:
			return False

		else:
			if self.local_ip==actual_ip and self.local_port==actual_port:
				# Checking if the file name hash actually exists
				file_name = self.mod_hash_check_file(file_hash)

				if file_name != False:

					# Creating path of local file about to be transferred
					file_path = self.dir_hosted + "/" + file_name

					dst_path = self.dir_downloaded

					assert not os.path.isabs(file_path)

					dstdir = os.path.join(dst_path, os.path.dirname(dst_path))

					shutil.copy(file_path, dstdir)

					sent_file_size = os.stat(file_path).st_size

					self.upload_amt = self.upload_amt + sent_file_size

					self.mod_update_ratio()

					return sent_file_size

				else:
					return -1

			else:
				remote_proxy1 = xmlrpclib.ServerProxy("http://" + actual_ip + ":" + actual_port + "/")
				download_file_size = remote_proxy1.mod_file_download_transfer(file_hash, self.local_ip, self.local_port, self.ratio)

		self.download_amt = self.download_amt + download_file_size

		self.mod_update_ratio()

		self.mod_cache_update(file_hash, actual_ip, actual_port)

		return True

#----------------- To check the destination Node of the File - Forward the Probe if needed -------
	def mod_rpc_upload(self, file_hash):

		if (file_hash < self.mod_get_own_hash() or file_hash > self.mod_get_pred_hash()) and self.mod_get_own_hash() < self.mod_get_pred_hash() and self.mod_get_own_hash() < self.mod_get_succ_hash():
			actual_ip	= self.mod_get_address( self.mod_get_own_hash() )[0]
			actual_port	= self.mod_get_address( self.mod_get_own_hash() )[1]

		elif file_hash > self.mod_get_pred_hash() and file_hash < self.mod_get_own_hash():
			#it should be with me - Normal Condition

			actual_ip	= self.mod_get_address( self.mod_get_own_hash() )[0]
			actual_port	= self.mod_get_address( self.mod_get_own_hash() )[1]

		elif file_hash < self.mod_get_pred_hash() and self.mod_get_own_hash() != self.mod_get_pred_hash():
			remote_proxy1 = xmlrpclib.ServerProxy("http://" + self.mod_get_address(self.mod_get_pred_hash())[0]+ ":" + self.mod_get_address(self.mod_get_pred_hash())[1] + "/")

			###print remote_proxy1

			actual_list = remote_proxy1.mod_rpc_upload( int(file_hash) )
			actual_ip 	= actual_list[0]
			actual_port = actual_list[1]

		elif file_hash >= self.mod_get_own_hash() and self.mod_get_own_hash() != self.mod_get_succ_hash():
			remote_proxy1 = xmlrpclib.ServerProxy("http://" + self.mod_get_address(self.mod_get_succ_hash())[0] + ":" + self.mod_get_address(self.mod_get_succ_hash())[1] + "/")

			###print remote_proxy1

			actual_list	= remote_proxy1.mod_rpc_upload( int(file_hash) )
			actual_ip	= actual_list[0]
			actual_port	= actual_list[1]

		actual_list	= [actual_ip,actual_port]	

		return actual_list

#----------------- Function to UPLOAD the file to Collab------------------------------------------
	def mod_upload(self, file_path, file_name):
		
		file_hash = self.mod_hash_string(file_name)	
		
		###print self.mod_get_address(self.mod_get_succ_hash())[0] , ":" , self.mod_get_address(self.mod_get_succ_hash())[1]

		if (file_hash < self.mod_get_own_hash() or file_hash > self.mod_get_pred_hash()) and self.mod_get_own_hash() < self.mod_get_pred_hash() and self.mod_get_own_hash() < self.mod_get_succ_hash():
			actual_ip	= self.mod_get_address( self.mod_get_own_hash() )[0]
			actual_port	= self.mod_get_address( self.mod_get_own_hash() )[1]

		elif file_hash > self.mod_get_pred_hash() and file_hash < self.mod_get_own_hash():
			#it should be with me - Normal Condition

			actual_ip	= self.mod_get_address( self.mod_get_own_hash() )[0]
			actual_port	= self.mod_get_address( self.mod_get_own_hash() )[1]

		elif file_hash < self.mod_get_pred_hash() and self.mod_get_own_hash() != self.mod_get_pred_hash():
			remote_proxy1 = xmlrpclib.ServerProxy("http://" + self.mod_get_address(self.mod_get_pred_hash())[0]+ ":" + self.mod_get_address(self.mod_get_pred_hash())[1] + "/")
			
			###print remote_proxy1

			actual_list = remote_proxy1.mod_rpc_upload( int(file_hash) )
			actual_ip 	= actual_list[0]
			actual_port = actual_list[1]

		elif file_hash >= self.mod_get_own_hash() and self.mod_get_own_hash() != self.mod_get_succ_hash():
			remote_proxy1 = xmlrpclib.ServerProxy("http://" + self.mod_get_address(self.mod_get_succ_hash())[0] + ":" + self.mod_get_address(self.mod_get_succ_hash())[1] + "/")

			###print remote_proxy1

			actual_list	= remote_proxy1.mod_rpc_upload( int(file_hash) )
			actual_ip	= actual_list[0]
			actual_port	= actual_list[1]

		else:	
			actual_ip	= self.mod_get_address( self.mod_get_own_hash() )[0]
			actual_port	= self.mod_get_address( self.mod_get_own_hash() )[1]
	

		#---------- Uploading File-----------------------------------------------------------
		remote_proxy1 = xmlrpclib.ServerProxy("http://" + actual_ip + ":" + actual_port + "/")
		self.mod_file_upload(file_path, file_name, remote_proxy1)
		return True

	def mod_cache_query(self):
			print "File Hash\tLocal_IP\tLocal_Port\tTimestamp"

			for key, val_list in self.cache.items():
				
				print str(key) + "\t" + val_list[0] + "\t" + val_list[1] + "\t" + val_list[2]

#----------------- Sourav and Midhun -------------------------------------------------------------

def main():
	# Details of current node
	f = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
	your_ip=f.read()
	your_ip = your_ip[0:-1]
	#local_ip = "localhost"
	local_ip = your_ip
	#local_port = sys.argv[1]
	local_port = '8000'
	# Creating the local object
	
	local_node = collab_system(local_ip, local_port)

	# Creating the directory which will contain all hosted files
	os.makedirs(local_node.dir_hosted)

	# Creating the directory which will contain all downloaded files
	os.makedirs(local_node.dir_downloaded)

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

	if len(sys.argv) == 2:
		# Details of master node

		#master_ip 	= "localhost"
		master_ip = sys.argv[1]
		master_port = '8000'

		conf = local_node.mod_join_req(master_ip,master_port)

		# Confirmation
		if conf == -1:
			print "\n\n\t\tGiven node IP does not exist ..."
			print "\n\n\t\tSystem will now exit ..."

			local_node.return_pause()

			return 0
	
	# Probing if successor is alive or not
	# The probe is in a seperate thread so that menu is not distrubed
	probe_thread = threading.Thread(target = local_node.mod_prob)
	probe_thread.daemon = True
	probe_thread.start()

	# local_node.return_pause()

	while True:
		os.system('clear')

		print "\n\n\t. : Collab Menu for %s : .\n" % local_ip

		print "\t|HASH VALUE| : %d\n" % local_node.mod_hash_string(local_node.local_address) 

		print "\tSearch & download      ...[1]"
		print "\tUpload                 ...[2]"
		print "\tAdmin Menu             ...[3]"
		print "\tExit                   ...[0]"

		input_val = raw_input("\n\n\tEnter option : ")

		if input_val == "1":
			file_name = raw_input("\n\tEnter name of file to be downloaded : ")

			# file_lookup = local_node.mod_file_download(file_name, remote_proxy)
			
			#------------ Sourav & Midhun ------------------------------------------------
			file_hash	= local_node.mod_hash_string(file_name)
			file_lookup = local_node.mod_search(file_hash )
			#------------ Sourav & Midhun ------------------------------------------------
			
			
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
				# local_node.mod_file_upload(file_path, file_name, remote_proxy)
				
				#------------ Sourav & Midhun ------------------------------------------------
				local_node.mod_upload( file_path, file_name )
				#------------ Sourav & Midhun ------------------------------------------------
				
				print "\n\tFile uploaded!"
			else:
				print "\n\tFile not found at current node!"

			local_node.return_pause()

		elif input_val == "3":
			while True:
				os.system('clear')

				print "\n\n\t. : Admin Menu for %s : .\n" % local_ip

				print "\t|HASH VALUE| : %d\n" % local_node.mod_hash_string(local_node.local_address) 

				print "\tSee finger table       ...[1]"
				print "\tSee hosted files       ...[2]"
				print "\tSee query cache        ...[3]"
				print "\tSee statistics         ...[4]"
				print "\tSee downloaded files   ...[5]"
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

						for files in file_list.keys():
							print "\t\t%s\t%s" % (files, file_list[files])
					else:
						print "\n\tThe current directory is empty...\n"

					local_node.return_pause()

				elif admin_inp_val == "3":
					local_node.mod_cache_query()

					local_node.return_pause()

				elif admin_inp_val == "4":
					local_node.mod_show_stats()

					local_node.return_pause()

				elif admin_inp_val == "5":
					file_list = local_node.mod_show_downloaded_files()

					print "\n\tThe files are...\n"

					for files in file_list:
						print "\t\t%s" % files

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
