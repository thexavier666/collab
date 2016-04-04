import sys
import xmlrpclib
import os
from SimpleXMLRPCServer import SimpleXMLRPCServer

class Collab_system:

	def __init__(self, local_ip, local_port):
		self.local_ip = local_ip
		self.local_port = local_port

	def mod_file_receive(self, bin_data, file_name):
		"""Used to receive a file upon a request of an upload"""

		print "[mod_file_receive fired]"

		new_file_name = "./" + file_name

		with open(new_file_name, "wb") as handle:
			handle.write(bin_data.data)

	def mod_file_transfer(self, file_name, remote_port):
		"""Initiating the file transfer"""

		print "[mod_file_transfer fired]"

		# Creaating path of local file about to be transferred
		file_path = "./" + file_name

		with open(file_path, "rb") as handle:
			bin_data = xmlrpclib.Binary(handle.read())

		# Creating connection object of requestor
		remote_proxy = xmlrpclib.ServerProxy("http://localhost:" + remote_port + "/")
		
		# Connecting to requestor's server
		remote_proxy.mod_file_download_receive(bin_data, file_name)

		sent_file_size = os.stat(file_path).st_size

		return sent_file_size

	def mod_file_download_receive(self, bin_data, file_name):
		"""Used to receive a file upon request of a download"""

		print "[mod_file_download_receive fired]"

		new_file_name = "./" + file_name + "_" + self.local_port

		with open(new_file_name, "wb") as handle:
			handle.write(bin_data.data)

		return True

def main():
	local_ip = "localhost"
	local_port = sys.argv[1]

	# Declared an XMLRPC server
	Collab_node = SimpleXMLRPCServer((local_ip, int(local_port)), allow_none = True)
	print "[Listening on port : %s]" % local_port

	Collab_node.register_introspection_functions()
	Collab_node.register_multicall_functions()
	Collab_node.register_instance(Collab_system(local_ip, local_port))

	# Initialized the XMLRPC server
	Collab_node.serve_forever()

if __name__ == '__main__':
	main()