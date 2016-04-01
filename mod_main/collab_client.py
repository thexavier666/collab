import sys
import xmlrpclib
import os

class Collab_front:

	def __init__(self, local_ip, local_port):
		self.local_ip = local_ip
		self.local_port = local_port

	def return_pause(self):
		"""Used for creating a pause during input"""

		raw_input("\n\tPress enter to continue")

		return True

	def mod_file_download(self, file_name, remote_proxy):
		"""Sending details to remote node which will send file to local node"""

		remote_proxy.mod_file_transfer(file_name, self.local_port)

		return True

	def mod_file_upload(self, file_path, file_name, remote_proxy):
		"""Used for sending files to a receiver. Sent file will always have the name file_1.txt"""

		new_file_name = file_name + "_" + self.local_port

		with open(file_path, "rb") as handle:
			bin_data = xmlrpclib.Binary(handle.read())

		remote_proxy.mod_file_receive(bin_data, new_file_name)

		return True

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
		print "\tExit              ...[0]"

		input_val = raw_input("\n\n\tEnter option : ")

		if input_val == "1":
			file_name = raw_input("\n\tEnter name of file to be downloaded : ")

			local_node.mod_file_download(file_name, remote_proxy)

			local_node.return_pause()
			
		elif input_val == "2":
			file_name = raw_input("\n\tEnter name of file to be uploaded : ")

			# Creaating path of local file about to be uploaded
			file_path = "./" + file_name
			
			local_node.mod_file_upload(file_path, file_name, remote_proxy)

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