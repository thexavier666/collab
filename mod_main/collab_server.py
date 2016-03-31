import thread
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

def mod_example(sample_str):
	"""A sample function"""

	print "This is a function with arguments as : %s" % sample_str

def mod_file_receive(bin_data, file_name):
	"""Used to receive a file"""

	new_file_name = "./" + file_name
	with open(new_file_name, "wb") as handle:
		handle.write(bin_data.data)
		return True

# Declared an XMLRPC server
node = SimpleXMLRPCServer(("localhost", 9000), allow_none=True)
print "Listening on port 9000..."

# Registered a list of functions
node.register_function(mod_example, "mod_example")
node.register_function(mod_file_receive, "mod_file_receive")

# Initialized the XMLRPC server
node.serve_forever()
