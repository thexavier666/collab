import sys
import xmlrpclib
import os
import time
import math

import collab_config as config

from SimpleXMLRPCServer import SimpleXMLRPCServer

# This is the listener part and the backend of the application

class collab_backend:

	def __init__(self, local_ip, local_port):
		self.local_ip = local_ip
		self.local_port = local_port

	def mod_calc_sleep_time(self, ratio):
		"""Calculates the sleep time according to ratio"""

		# Ratio infinite or or greater than 1
		if ratio > 1:
			return 0

		# No download or upload done yet or ratio is exactly 1
		elif ratio == 1:
			return config.DEF_SLEEP_TIME

		# Ratio is less than 1
		elif ratio >= 0.1 and ratio < 1:
			return config.SLEEP_LEVEL_1

		elif ratio >= 0.01 and ratio < 0.1:
			return config.SLEEP_LEVEL_2

		elif ratio >= 0.001 and ratio < 0.01:
			return config.SLEEP_LEVEL_3

		else:
			return config.SLEEP_LEVEL_4

	def mod_download_sleep(self, ratio):
		"""A function which delays the download according to the ratio"""

		print "Sleep Time : %d" % self.mod_calc_sleep_time(ratio)
		time.sleep(self.mod_calc_sleep_time(ratio))

	def mod_file_receive(self, bin_data, file_name):
		"""Used to receive a file upon a request of an upload"""

		print "[mod_file_receive fired]"

		new_file_name = "./" + file_name

		with open(new_file_name, "wb") as handle:
			handle.write(bin_data.data)

	def mod_file_transfer(self, file_name, remote_port, remote_ratio):
		"""Initiating the file transfer"""

		print "[mod_file_transfer fired]"

		self.mod_download_sleep(remote_ratio)

		# Creaating path of local file about to be transferred
		file_path = "./" + file_name

		if os.path.exists(file_path):
			with open(file_path, "rb") as handle:
				bin_data = xmlrpclib.Binary(handle.read())

			# Creating connection object of requestor
			remote_proxy = xmlrpclib.ServerProxy("http://localhost:" + remote_port + "/")
			
			# Connecting to requestor's server
			remote_proxy.mod_file_download_receive(bin_data, file_name)

			sent_file_size = os.stat(file_path).st_size

			return sent_file_size
		else:
			return -1

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
	local_node = SimpleXMLRPCServer((local_ip, int(local_port)), allow_none = True)
	print "[Listening on port : %s]" % local_port

	local_node.register_introspection_functions()
	local_node.register_multicall_functions()
	local_node.register_instance(collab_backend(local_ip, local_port))

	# Initialized the XMLRPC server
	local_node.serve_forever()

if __name__ == '__main__':
	main()
