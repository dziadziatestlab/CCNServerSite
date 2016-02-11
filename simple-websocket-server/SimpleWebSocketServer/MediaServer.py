import threading
from UdpServer import UdpServer
from utils.converter import ice_offer_parser
from utils.usocket import get_ip_address

class MediaServer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.HOST=''
		self.PORT=8888
		self.udpServer=None
		self.peerSocket=None #(ipaddress,port)
		print 'MediaServer thread initialised.'

	def run(self):
		self.HOST=get_ip_address()
		print 'MediaServer thread starting'
		self.udpServer=UdpServer(self.HOST,self.PORT)
		self.udpServer.start()
		
	def onStop(self):
		if self.udpServer:
			self.udpServer.stop()

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

