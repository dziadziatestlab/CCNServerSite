import socket
import sys
#from CCNBuffer import CCNBuffer
import Queue
import threading
from utils import logger


LOGGER=logger.Logger(True).get_logger()

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
		LOGGER('#UdpServer initialised')


	def __bindSocket__(self):
		port=self.port
		while(not self.isBinded):
			try:
				self.socket.bind((self.host,port))
				self.port=port
				self.isBinded=True
			except socket.error,msg:
				LOGGER('#UdpServer Socket binding error: '+str(msg[0])+' Message: '+msg[1])
				if msg[0]==99:
					LOGGER('#UdpServer Check ip address of interface')
					sys.exit()
				if msg[0]==98:
					LOGGER('#UdpServer Trying to assign next port')
					port+=1
					if port-self.port>10:
						LOGGER('#UdpServer No possibility to find free port!')
						sys.exit()
					
				#sys.exit()
	def run(self):
		LOGGER('#UdpServer thread starting')
		self._start_()

	def _start_(self):
		try:
			self.socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			LOGGER('#UdpServer Socket created')
		except socket.error:
			LOGGER('#UdpServer Failed to create socket')
			sys.exit()
		
		self.__bindSocket__()		

		LOGGER('#UdpServer started at adress: ',self.host,' port: ',self.port)

		# buffer for CCN packets
		#buf=CCNBuffer(100)
		#buf.showBufferState()
		#self.ccnBuffer=buf

		while(1):
			d=self.socket.recvfrom(1024)
			data=d[0]
			addr=d[1]
			LOGGER('#UdpServer type of data: ',type(data))
			LOGGER('#UdpServer data length: ',data.__sizeof__())
			if self.peerSet==False:
				self.peerSocket=addr
				self.peerSet=True				
			if not data: 
				LOGGER('#UdpServer No data received ')
				#break
			LOGGER('#UdpServer Obtained data from: '+str(addr))
			#buf.addPacket(data)
			#buf.showBufferState()
			#reply='OK ... '+data
			#self.socket.sendto(reply,addr)
			#LOGGER('Message sent')
			if data:
				LOGGER('#UdpServer added data to output_queue.Data:\n',data )
				self.output_queue.put(data)
			if not self.input_queue.empty():
				if hasattr(self,'peerSocket'):
					data_to_send=self.input_queue.get()
					self.sendData(data_to_send,self.peerSocket)
				else:
					LOGGER('#UdpServer No peerSocket set !!! Where to send ???')

			else: LOGGER('#UdpServer Input queue empty !')

	
	def stop(self):
		if self.socket:
			self.socket.close()
			LOGGER('#UdpServer socket closed !')
		else:
			LOGGER('#UdpServer No socket to be closed !')

	def getSocket(self):
		return (self.host,self.port)

	def getPeerSocket(self):
		return self.peerSocket

	def sendData(self,data,socket):
		LOGGER('#UdpServer  sendData called with peer: ',socket)
		self.socket.sendto(data,socket)


if __name__=='__main__':
	LOGGER('#UdpServer started from __main__')
	us=UdpServer('10.0.2.15',8888,Queue.Queue(),Queue.Queue())
	us.start()
	us.stop()
	sys.exit()

