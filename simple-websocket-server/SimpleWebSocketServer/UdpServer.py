import socket
import sys


class UdpServer():
	def __init__(self,host,port):
		self.host=host
		self.port=port
		self.socket=None
		print 'UdpServer initialised'
	def start(self):
		try:
			self.socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			print 'Socket created'
		except socket.error:
			print 'Failed to create socket'
			sys.exit()
		try:
			self.socket.bind((self.host,self.port))
		except socket.error,msg:
			print 'Socket binding error: '+str(msg[0])+' Message: '+msg[1]
			sys.exit()


		print 'UdpServer started at adress: ',
		print self.host,
		print ' port: ',
		print self.port

		while(1):
			d=self.socket.recvfrom(1024)
			data=d[0]
			addr=d[1]
			if not data:
				break
			print 'Obtained: '+data+'From: '+str(addr)
			reply='OK ... '+data
			self.socket.sendto(reply,addr)
			print 'Message sent'

	
	def stop(self):
		if self.socket:
			self.socket.close()
			print 'UdpServer socket closed !'
		else:
			print 'No socket to be closed !'	




if __name__=='__main__':
	print 'UdpServer started from __main__'
	us=UdpServer('192.168.0.116',8888)
	us.start()
	us.stop()
	sys.exit()

