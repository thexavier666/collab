import sys
import xmlrpclib
import os

# This is the front end of the Collab system
# All functions present in this class are the APIs provided to the user 
class Collab_front:

	def __init__(self, local_ip, local_port):
		self.local_ip = local_ip
		self.local_port = local_port
		self.upload_amt = 1
		self.download_amt = 1
		self.ratio = 1

	def return_pause(self):
		"""Used for creating a pause during input"""

		raw_input("\n\tPress enter to continue")

		return True

	def mod_file_download(self, file_name, remote_proxy):
		"""Sending details to remote node which will send file to local node"""

		download_file_size = remote_proxy.mod_file_transfer(file_name, self.local_port, self.ratio)

		if download_file_size == -1:
			return False
		else:
			self.download_amt = self.download_amt + download_file_size
			return True

	def mod_file_upload(self, file_path, file_name, remote_proxy):
		"""Used for sending files to a receiver. Sent file will always have the name file_1.txt"""

		new_file_name = file_name + "_" + self.local_port

		with open(file_path, "rb") as handle:
			bin_data = xmlrpclib.Binary(handle.read())

		remote_proxy.mod_file_receive(bin_data, new_file_name)

		self.upload_amt = self.upload_amt + os.stat(file_path).st_size

		return True

	def mod_show_stats(self):
		"""Shows all statistics of the current node"""

		# Nothing done
		if self.upload_amt == 0 and self.download_amt == 0:
			self.ratio = 0
		# Only uploads done
		elif self.upload_amt != 0 and self.download_amt == 0:
			self.ratio = -1
		# Both done
		else:
			self.ratio = (self.upload_amt * 1.0)/(self.download_amt * 1.0)

		print "\n\t\tUpload   (Bytes) : %d" % (self.upload_amt)
		print "\n\t\tDownload (Bytes) : %d" % (self.download_amt)
		print "\n\t\tCurrent ratio    : %f" % (self.ratio)

##MAIN MODULE STARTS HERE##

def main():

	# Details of local node
	local_ip = "localhost"
	local_port = sys.argv[1]

	# Connection details of remote node
	remote_ip = "localhost"

	# Getting details of remote node
	remote_port = raw_input("\n\tEnter remote port ID : ")

	# Creating connection details of remote node
	remote_proxy = xmlrpclib.ServerProxy("http://" + remote_ip + ":" + remote_port + "/")

	local_node = Collab_front(local_ip, local_port)

	while True:
		os.system('clear')

		print "\t. : Collab Menu for %s : .\n" % local_port
		print "\tSearch & download ...[1]"
		print "\tUpload            ...[2]"
		print "\tAdmin Mode        ...[3]"
		print "\tExit              ...[0]"

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

				print "\t. : Admin Collab Menu for %s : .\n" % local_port
				print "\tSee finger table  ...[1]"
				print "\tSee local files   ...[2]"
				print "\tList query cache  ...[3]"
				print "\tSee neighbours    ...[4]"
				print "\tSee statistics    ...[5]"
				print "\tBack              ...[0]"

				admin_inp_val = raw_input("\n\n\tEnter option : ")

				if admin_inp_val == "1":
					local_node.return_pause()

				elif admin_inp_val == "2":
					local_node.return_pause()

				elif admin_inp_val == "3":
					local_node.return_pause()

				elif admin_inp_val == "4":
					local_node.return_pause()

				elif admin_inp_val == "5":
					local_node.mod_show_stats()
					local_node.return_pause()

				elif admin_inp_val == "0":
					break
					local_node.return_pause()

				else:
					print "\tIncorrect option value"
					print "\tTry again..."
					local_node.return_pause()

		elif input_val == "0":
			print "\tExiting"
			break

		else:
			print "\tIncorrect option value"
			print "\tTry again..."
			local_node.return_pause()

	os.system('clear')

if __name__ == '__main__':
	main()