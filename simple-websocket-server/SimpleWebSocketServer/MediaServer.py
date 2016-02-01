import threading
from UdpServer import UdpServer



class MediaServer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.HOST='192.168.0.178'
		self.PORT=8888
		self.udpServer=None
		print 'MediaServer thread initialised.'

	def run(self):
		print 'MediaServer thread starting'
		self.udpServer=UdpServer(self.HOST,self.PORT)
		self.udpServer.start()

		
	def onStop(self):
		if self.udpServer:
			self.udpServer.stop()
		




if __name__=='__main__':
	print 'Starting Media Server from script'
	mediaServer=MediaServer()
	mediaServer.start()

