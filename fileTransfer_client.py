import socket
import sys
import time

s = socket.socket()

s.connect(("localhost",9999))

fileSend = open (sys.argv[1], "rb") 

fileByte = fileSend.read(1024)

while (fileByte):

	s.send(fileByte)

	time.sleep(float(sys.argv[2])/100.00)

	fileByte = fileSend.read(1024)

s.close()
