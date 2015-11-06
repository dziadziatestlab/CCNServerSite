import signal,sys,json
import pyccn as ccn
import threading,time
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer


config_port=8000
config_host=''

#hccn=ccn.CCN()



class myThread(threading.Thread):
	def __init__(self,threadId,name,callback):
		threading.Thread.__init__(self)
		self.threadId=threadId
		self.name=name
		self.callback=callback
	def run(self):
		print 'Starting: '+self.name
		for i in range(0,10):
			print 'Counter: '+str(i)
			time.sleep(5)
		self.callback('Thread finished !!!')

			
class sendToCCN(threading.Thread):
	def __init__(self,name,callback):
		threading.Thread.__init__(self)
		self.name=name
		self.callback=callback
	def run(self):
		hccn=ccn.CCN()
		nameStr=ccn.Name(self.name)
		co=hccn.get(nameStr,timeoutms=9000)
		print nameStr
		self.callback('Thread finished')


def onSuccess(event):
	print 'onSuccess called.'

def onError(message):
	print 'onError called.'

class SimpleEcho(WebSocket):

	
	

	def expressInterest(self,name,onSuccess,onError):
		print 'expressInterest called for name: '+name
	
		#self.hccn=ccn.CCN()
		
		#self.nameStr=ccn.Name(name)
		#print self.nameStr
		#print str(nameStr)
		
		#self.co=self.hccn.get(self.nameStr)
		'''	
		print 'content object '
		if co==None:
			onError('No answer from server')
		else:
			onSuccess(co)

		'''

	def callback(self,message):
		print message

	def handleConnected(self):
		print 'Peer connected !'

	def handleClose(self):
		print 'Peer disconnected'

	def handleMessage(self):
		print 'Received type: '+str(type(self.data))
		#print dir(self.data)
		if type(self.data) is unicode:
			print 'Signaling message'
			print self.data
			dane=json.loads(self.data)
			#if dane:print type(dane)
			if type(dane)is dict:
				print dane['type']
				if dane['type']=='Interest':
					self.expressInterest(dane['data'],onSuccess,onError)
					#thread5=myThread(1,'Message thread',self.callback)
					#thread5.start()
					toCCN=sendToCCN(dane['data'],self.callback)
					toCCN.start()
					
					print 'After expressInterest'					
					#hccn=ccn.CCN()
					#name=ccn.Name(dane['data'])
					#print name
					#co=hccn.get(name,timeoutms=2000)
			
		if type(self.data) is bytearray:
			#values=bytearray(self.data)
			print 'Inside loop'
			print self.data.__sizeof__()
			for v in self.data:
				print v
			#print dir(values)
			#print 'Length array: '+str(values.length)
				


if __name__=="__main__":
	print 'proxy Server is going to start'
	server=SimpleWebSocketServer('',8000,SimpleEcho)
	
	thread1=myThread(1,'Thread-1',None)
	thread2=myThread(2,'Thread-2',None)
	
	thread1.start()


	def close_sig_handler(signal,frame):
		print 'close port called !'
		server.close()
		sys.exit()
	signal.signal(signal.SIGINT,close_sig_handler)
	server.serveforever()
	thread2.start()
	

	

