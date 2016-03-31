import os
import xmlrpclib

def return_pause():
	"""Used for creating a pause during input"""

	raw_input("\n\tPress enter to continue")

def mod_file_send(file_path, file_name, proxy):
	"""Used for sending files to a receiver. Sent file will always have the name file_1.txt"""

	new_file_name = "file_1.txt"
	with open(file_path, "rb") as handle:
		bin_data = xmlrpclib.Binary(handle.read())

	proxy.mod_file_receive(bin_data, new_file_name)

##MAIN MODULE STARTS HERE##

# Connection details of remote node
proxy = xmlrpclib.ServerProxy("http://localhost:9000/")

while True:
	os.system('clear')

	print "\t. : Collab Menu : ."
	print "\tSearch & download ...[1]"
	print "\tUpload            ...[2]"
	print "\tExit              ...[0]"

	input_val = raw_input("\n\n\tEnter option : ")

	if input_val == "1":
		print "\tCurrently, it's not doing anything"

		proxy.mod_example("Some input")

		return_pause()
		
	elif input_val == "2":
		file_name = raw_input("\n\tEnter name of file to be uploaded : ")
		file_path = "./" + file_name
		
		mod_file_send(file_path, file_name, proxy)

		return_pause()

	elif input_val == "0":
		print "\tExiting"
		break

	else:
		print "\tIncorrect option value"
		print "\tTry again..."
		return_pause()

os.system('clear')
