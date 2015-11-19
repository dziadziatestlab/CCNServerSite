import signal,sys,json
import pyccn as ccn
import threading,time
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer


config_port=8000
config_host=''

#hccn=ccn.CCN()

class callbackInfo():
	def __init__(self):
		self.callback=None
		self.sdpInfo=None #only for tests of first phase


class ccnRegister(threading.Thread):
	def __init__(self,threadId,callback,sdp):
		threading.Thread.__init__(self)
		self.threadId=threadId
		self.callback=callback
		self.sdp=sdp

	def run(self):
		print 'ccnRegister thread started !'
		name=ccn.Name(str(self.threadId))
		print 'Name:',
		print name
		handler=ccn.CCN()


		interest_handler=ProducerClosure()
		interest_handler.callback=self.onInterest
		interest_handler.sdpInfo=self.sdp #only for test first phase
		res=handler.setInterestFilter(name,interest_handler)
		if(res<0):
			print 'Some problems occured !'
		
		handler.run(-1)
		raise SystemError('Exited loop!')
	def onInterest(self,message):
		print message
		self.callback(str(message),None)
	

class makeCCNCall(threading.Thread):
	def __init__(self,IdFrom,IdTo,callback):
		threading.Thread.__init__(self)
		self.threadId=IdFrom		
		self.idFrom=IdFrom
		self.idTo=IdTo
		self.callback=callback
		print 'makeCCNCall thread initialization'
	def run(self):
		print "Sending CCN request to: "+str(self.idTo)
		urlName=self.idTo+'/call'+self.idFrom
		print urlName
		name=ccn.Name(str(urlName))
		ccnHandler=ccn.CCN()
		co=ccnHandler.get(name,timeoutms=2000)
		if(co==None):
			print 'No answer from server'
		else:
			print co.name
			print co.content			
			self.callback()
		



class myThread(threading.Thread):
	def __init__(self,threadId,name,callback,clients):
		threading.Thread.__init__(self)
		self.threadId=threadId
		self.name=name
		self.callback=callback
		self.clients=clients
	def run(self):
		print 'Starting: '+self.name
		for i in range(0,100):
			print 'Counter: '+str(i)
			print 'Number of clients:'+len(self.clients)				
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



class addNewClient(threading.Thread):
	def __init__(self,callback):
		threading.Thread.__init__(self)
		self.callback=callback
		#self.clients=clients
		print 'addNewClient constructor called'
	def run(self):
		#self.clients[data.userId]=data
		self.callback()
		pass


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

	def addNewClientCallback(self):
		print 'addNewClientCallback called'
		print len(self.ccnClients)
		
	def addNewClient(self,data):
		if(not self.ccnClients.has_key(data['userId'])):
			newCCNRegisterThread=ccnRegister(data['userId'],self.sendRequestToIPClient,data['SDP'])
			newCCNRegisterThread.start()
			data['threadRef']=newCCNRegisterThread
		self.ccnClients[data['userId']]=data
		self.showNumberOfClients()

	def sendRequestToIPClient(self,name,callback):
		print 'sendRequestToIPClient called with name: ',
		print name
		self.sendMessage('someone is calling you !')
		
		
	def makeCall(self,data):
		print 'makeCall method called with params:',
		print data['From'],
		print data['To']

		ccnCallThread=makeCCNCall(data['From'],data['To'],self.makeCallCallback)
		ccnCallThread.start()
		


	def makeCallCallback(self):
		print 'makeCallCallback called'	
		self.sendMessage("asdasdasd")
		
	def showNumberOfClients(self):
		print 'Number of CCN Clients:',
		print len(self.ccnClients)


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
					toCCN=sendToCCN(dane['data'],self.callback)
					toCCN.start()
				if dane['type']=='REGISTER':
					print 'REGISTER METHOD PROCESING'
					self.addNewClient(dane)	
				if dane['type']=='CALL':
					print 'CALL CONNECTION '
					self.makeCall(dane)

				if dane['type']=='TEST':
					print 'Test of connection with peer'
					ss=json.dumps(dane,ensure_ascii=False)
					
					self.sendMessage(ss)
					print type(self.data)	
					print type(ss)				
					print ss	
					print self.data				
					print 'Message to client sent.'


		if type(self.data) is bytearray:
			#values=bytearray(self.data)
			print 'Inside loop'
			print self.data.__sizeof__()
			for v in self.data:
				print v
			#print dir(values)
			#print 'Length array: '+str(values.length)
				





class ProducerClosure(ccn.Closure,callbackInfo):
	def __init__(self):
		callbackInfo.__init__(self)
	def upcall(self,kind,upcallInfo):
		if(kind==ccn.UPCALL_FINAL):
			pass
		elif(kind==ccn.UPCALL_INTEREST):
			print 'Interest received !!!'
			name=upcallInfo.Interest.name
			print 'Received request: '+str(name)
			#payload='Hello Client'
			payload=self.sdpInfo
			co=ccn.ContentObject(name)
			co.content=payload
			

			self.callback('Received interest with name')
			self.callback(str(name))

			handler=ccn.CCN()
			key=handler.getDefaultKey()
			kl=ccn.KeyLocator()
			kl.key=key

			si=ccn.SignedInfo()
			si.publisherPublicKeyDigest=key.publicKeyID
			si.type=ccn.CONTENT_DATA
			si.keyLocator=kl
			co.signedInfo=si

			

			co.sign(key)

			if(co.matchesInterest(upcallInfo.Interest)):
				res=handler.put(co)
				if(res>=0):
					print payload
					return ccn.RESULT_INTEREST_CONSUMED
				else:
					raise SystemError('Failed to put ContentObject')
			else:
				sys.stderr.write(payload+' NOT SENT !')
		return ccn.RESULT_OK






















if __name__=="__main__":
	print 'proxy Server is going to start'
	
	server=SimpleWebSocketServer('',8000,SimpleEcho)
	
	#thread1=myThread(1,'Thread-1',None,server.ccnClients)
	#thread2=myThread(2,'Thread-2',None)
	
	#thread1.start()


	def close_sig_handler(signal,frame):
		print 'close port called !'
		server.close()
		sys.exit()
	signal.signal(signal.SIGINT,close_sig_handler)
	#server.clients={}	
	server.serveforever()
	#thread2.start()
	

	

