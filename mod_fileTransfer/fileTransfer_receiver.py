# The files accepts the incoming file, renames it to "file_x"
# Where x is the current number of downloads

import socket
import sys

server = socket.socket()

server.bind(("localhost",9999))

# Accept 10 simultaneous connections
server.listen(10)

# Incrementer
i = 1

while True:

	# Accepts a single connection
	client, address = server.accept()

	print address

	# File open in binary mode
	f = open('file_' + str(i), 'wb')

	i = i + 1

    	print "File downloading..."

	# Receiving a byte of data
       	l = client.recv(1024)

	# Combining the files till we get 0 byte
       	while l:
               	f.write(l)
               	l = client.recv(1024)
	f.close()
	
	print "File downloading complete!"
    	client.close()

server.close()
