import threading
from UdpServer import UdpServer
from utils.converter import ice_offer_parser
from utils.usocket import get_ip_address
from utils import logger
from server.CCNBuffer import CCNBuffer
import Queue,time

LOGGER=logger.Logger().get_logger()
LOGGER2=logger.Logger().get_logger()
LOGGER3=logger.Logger(True).get_logger()

#from collections import deque

class MediaServer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.threadName=''
		self.HOST=get_ip_address()
		self.PORT=8000
		self.udpServer=None
		self.peerSocket=None #(ipaddress,port)
		self.input_queue=Queue.Queue()
		self.output_queue=Queue.Queue()
		#self.read_queue=deque(maxlen=1000)
		self.read_queue=Queue.Queue()
		self.answer_queue=None
		self.buffer=CCNBuffer(10000)
		self.isRunning=True
		LOGGER3( 'MediaServer thread initialised.')
	
	def setThreadName(self,threadId):
		self.threadName=threadId
		self.buffer.threadName=threadId

	def run(self):
		#self.HOST=get_ip_address()
		LOGGER3( 'MediaServer thread starting')
		#self.udpServer=UdpServer					 (self.HOST,self.PORT,self.input_queue,self.output_queue)		
		#self.udpServer.start()
		self._start_()
		

	def _start_(self):
		LOGGER3( 'MediaServer _start_ method called')
		while self.isRunning:
			if not self.output_queue.empty():
				LOGGER3('#MediaServer output_queue -- data to buffer')				
				LOGGER('data in the output_queue to buffer')
				data_from_output_queue=self.output_queue.get()
				self.buffer.addPacket(data_from_output_queue)
				LOGGER( 'Data into buffer saved')
				LOGGER2('MediaServer write to buffer: \n',data_from_output_queue)
				
			if not self.read_queue.empty():
				LOGGER3('#MediaServer read_queue -- data from buffer')
				data_to_send=self.buffer.readPacket()
				LOGGER3('#MediaServer data from buffer readed.')
				LOGGER('data from buffer to packaging: \n',data_to_send)
				self.read_queue.get()(data_to_send)
				LOGGER( 'Data from buffer consumed')
				LOGGER2('MediaServer data from buffer to packaging: \n',data_to_send)
						
			if not self.input_queue.empty():
				LOGGER3('#MediaServer input_queue -- data to send')
				LOGGER('Data in the queue to be send')
				data=self.input_queue.get()
				LOGGER('PeerSocket to which should send:',self.peerSocket)
				self.sendData(data)
			


	'''
	def onStop(self):
		if self.udpServer:
			self.udpServer.stop()
	'''


	
	def getSocket(self):
		#return self.udpServer.getSocket()
		return (self.HOST,self.PORT)
	
	

	
	def setPeerAddress(self, socket):
		LOGGER( 'MediaServer setPeerAddress called with: ',socket)
		self.peerSocket=socket
	

	
	def sendData(self,data):
		LOGGER( 'MediaServer sendData called')
		#self.udpServer.sendData(data,self.peerSocket)
	


if __name__=='__main__':
	LOGGER( 'Starting Media Server from script')
	mediaServer=MediaServer()
	# for test 
	#LOGGER( ice_offer_parser('candidate:0 2 UDP 23234 192.10.1.1 234234 typ host'))
	mediaServer.start()

