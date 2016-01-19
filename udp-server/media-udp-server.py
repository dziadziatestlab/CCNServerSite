import socket
import sys


# variables to setup socket server
HOST=''
PORT=8888


try:
	s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	print 'Socket created'
except socket.error:
	print 'Failed to create socket'
	sys.exit()	


try:
	s.bind((HOST,PORT))
except socket.error,msg:
	print 'Socket binding error: '+str(msg[0])+' Message: '+msg[1]
	sys.exit()

print 'Socket bind complete.'

while(1):
	d=s.recvfrom(1024)
	data=d[0]
	addr=d[1]
	if not data:
		break
	print 'Obtained: '+data+'From: '+str(addr)
	reply='OK ... '+data
	s.sendto(reply,addr)
	print 'Message sent'


s.close()

