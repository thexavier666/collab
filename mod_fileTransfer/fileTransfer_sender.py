# The arguments are 
# 1st argument : Name of file in current directory
# 2nd argument : Sleep time in milisecond

# Example "python fileTransfer_uploader.py somefile 10"
# The sleep time is 10 milisecond
# Higher the value, slower the speed
# A sleeptime of 1 milisecond	~ 100 KBps
# A sleeptime of 0.1 milisecond ~ 1000 Kbps

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
