import socket
import sys

server = socket.socket()

server.bind(("localhost",9999))

server.listen(10) # Accept 10 simultaneous connections

i = 1

while True:

	# Accepts a single connection
	sc, address = server.accept()

	print address

	# File open in binary mode
	f = open('file_' + str(i), 'wb')

	i = i + 1

    	print "Started Receiving"

	# Receiving a byte of data
       	l = sc.recv(1024)

	# Combining the files till we get 0 byte
       	while l:
               	f.write(l)
               	l = sc.recv(1024)
	f.close()
	
	print "A file has been received"
    	sc.close()

server.close()
