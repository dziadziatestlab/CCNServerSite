import socket
import sys
from CCNBuffer import CCNBuffer


class UdpServer():
	def __init__(self,host,port):
		self.host=host
		self.port=port
		self.socket=None
		self.isBinded=False
		self.ccnBuffer=None
		print 'UdpServer initialised'


	def __bindSocket__(self):
		port=self.port
		while(not self.isBinded):
			try:
				self.socket.bind((self.host,port))
				self.port=port
				self.isBinded=True
			except socket.error,msg:
				print 'Socket binding error: '+str(msg[0])+' Message: '+msg[1]
				if msg[0]==99:
					print 'Check ip address of interface'
					sys.exit()
				if msg[0]==98:
					print 'Trying to assign next port'
					port+=1
					if port-self.port>10:
						print 'No possibility to find free port!'
						sys.exit()
					
				#sys.exit()
	

	def start(self):
		try:
			self.socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			print 'Socket created'
		except socket.error:
			print 'Failed to create socket'
			sys.exit()
		
		self.__bindSocket__()		

		print 'UdpServer started at adress: ',
		print self.host,
		print ' port: ',
		print self.port

		# buffer for CCN packets
		buf=CCNBuffer(100)
		buf.showBufferState()
		self.ccnBuffer=buf

		while(1):
			d=self.socket.recvfrom(1024)
			data=d[0]
			addr=d[1]
			if not data:
				break
			print 'Obtained: '+data+'From: '+str(addr)
			buf.addPacket(data)
			buf.showBufferState()
			reply='OK ... '+data
			#self.socket.sendto(reply,addr)
			#print 'Message sent'

	
	def stop(self):
		if self.socket:
			self.socket.close()
			print 'UdpServer socket closed !'
		else:
			print 'No socket to be closed !'	

	def getSocket(self):
		return (self.host,self.port)



if __name__=='__main__':
	print 'UdpServer started from __main__'
	us=UdpServer('192.168.0.116',8888)
	us.start()
	us.stop()
	sys.exit()

