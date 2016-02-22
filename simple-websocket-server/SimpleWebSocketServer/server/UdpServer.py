import socket
import sys
#from CCNBuffer import CCNBuffer
import Queue
import threading

class UdpServer(threading.Thread):
	def __init__(self,host,port,input_queue,output_queue):
		threading.Thread.__init__(self,name='UdpServer-thread')
		self.host=host
		self.port=port
		self.socket=None
		self.isBinded=False
		self.peerSet=False
		self.input_queue=input_queue
		self.output_queue=output_queue
		#self.ccnBuffer=None
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
	def run(self):
		print 'UdpServer thread starting'
		self._start_()

	def _start_(self):
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
		#buf=CCNBuffer(100)
		#buf.showBufferState()
		#self.ccnBuffer=buf

		while(1):
			d=self.socket.recvfrom(1024)
			data=d[0]
			addr=d[1]
			if self.peerSet==False:
				self.peerSocket=addr
				self.peerSet=True				
			if not data: 
				print 'No data received '
				#break
			print 'Obtained data from: '+str(addr)
			#buf.addPacket(data)
			#buf.showBufferState()
			#reply='OK ... '+data
			#self.socket.sendto(reply,addr)
			#print 'Message sent'
			if data:
				self.output_queue.put(data)
			if not self.input_queue.empty():
				data_to_send=self.input_queue.get()
				self.sendData(data_to_send,self.getSocket())

			else: print 'Input queue empty !'

	
	def stop(self):
		if self.socket:
			self.socket.close()
			print 'UdpServer socket closed !'
		else:
			print 'No socket to be closed !'	

	def getSocket(self):
		return (self.host,self.port)

	def getPeerSocket(self):
		return self.peerSocket

	def sendData(self,data,socket):
		print 'sendData called with peer: ',socket
		self.socket.sendto(data,socket)


if __name__=='__main__':
	print 'UdpServer started from __main__'
	us=UdpServer('10.0.2.15',8888,Queue.Queue(),Queue.Queue())
	us.start()
	us.stop()
	sys.exit()
