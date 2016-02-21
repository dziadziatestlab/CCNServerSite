import threading
from UdpServer import UdpServer
from utils.converter import ice_offer_parser
from utils.usocket import get_ip_address
from CCNBuffer import CCNBuffer
import Queue,time

class MediaServer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.HOST=''
		self.PORT=8888
		self.udpServer=None
		self.peerSocket=None #(ipaddress,port)
		self.input_queue=Queue.Queue()
		self.output_queue=Queue.Queue()
		self.read_queue=Queue.Queue()
		self.answer_queue=None
		self.buffer=CCNBuffer(1000)
		self.isRunning=True
		print 'MediaServer thread initialised.'

	def run(self):
		self.HOST=get_ip_address()
		print 'MediaServer thread starting'
		self.udpServer=UdpServer(self.HOST,self.PORT,self.input_queue,self.output_queue)
		self.udpServer.start()
		self._start_()
		

	def _start_(self):
		print 'MediaServer _start_ method called'
		while self.isRunning:
			if not self.output_queue.empty():
				self.buffer.addPacket(self.output_queue.get())
				print 'Data into buffer saved'

	'''
	def onStop(self):
		if self.udpServer:
			self.udpServer.stop()
	'''


	
	def getSocket(self):
		return self.udpServer.getSocket()
	
	

	
	def setPeerAddress(self, socket):
		print 'MediaServer setPeerAddress called with: ',socket
		self.peerSocket=socket
	

	
	def sendData(self,data):
		print 'MediaServer sendData called'
		self.udpServer.sendData(data,self.peerSocket)
	


if __name__=='__main__':
	print 'Starting Media Server from script'
	mediaServer=MediaServer()
	# for test 
	#print ice_offer_parser('candidate:0 2 UDP 23234 192.10.1.1 234234 typ host')
	mediaServer.start()

