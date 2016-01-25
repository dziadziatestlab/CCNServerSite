import signal,sys,json
import pyccn as ccn
import threading,time
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer
from MediaServer import MediaServer

config_port=8000
config_host=''

clients=[]
registeredClients={}

def showConnectedClients():
	print 'Connected clients:'
	for client in clients:
		print client.address
def showRegisteredClients():
	print 'Registered clients:'
	for client in registeredClients:
		print client,'  :  ',registeredClients[client]['obj'].address


class callbackInfo():
	def __init__(self):
		self.callback=None
		self.sdpInfo=None #only for tests of first phase
		self.nameId=None
	


class ccnRegister(threading.Thread):
	def __init__(self,threadId,callback,sdp):
		threading.Thread.__init__(self)
		self.threadId=threadId
		self.callback=callback
		self.sdp={}
		self.sdp['SDP']=sdp['SDP']
		self.sdp['ICE']=sdp['ICE']
		self.data=None
		print 'ccnRegister thread constructor called'

	def run(self):
		print 'ccnRegister thread started !'
		name=ccn.Name(str(self.threadId))
		print 'Name:',
		print name
		handler=ccn.CCN()


		interest_handler=ProducerClosure()
		interest_handler.callback=self.onInterest
		interest_handler.sdpInfo=self.sdp #only for test first phase
		interest_handler.nameId=name
		res=handler.setInterestFilter(name,interest_handler)
		if(res<0):
			print 'Some problems occured !'
		
		handler.run(-1)
		raise SystemError('Exited loop!')
	def onInterest(self,message):
		print 'threadId: ',self.threadId,' onInterest called'
		print message
		self.callback(str(message),None)
	
	def onMakeCall(self,data,callback,errorCallback):
		self.data=data
		print 'threadId: ',self.threadId,' onMakeCall called'
		print 'sending request to: ',data['To']
		
	
		
		urlName=data['To']+'/call'+data['From']
		print 'Request URL: ',urlName
		
		name=ccn.Name(str(urlName))
		ccnHandler=ccn.CCN()
		co=ccnHandler.get(name,timeoutms=2000)
		if(co==None):
			print 'No answer from server'
			#self.onMakeCallError()
			errorCallback(self.data['From'],'No answer from called')
		else:
			print co.name
			print co.content			
			callback(self.data['From'],co.content)			

	def updateSDP(self,sdp):
		self.sdp['SDP']=sdp['SDP']
		self.sdp['ICE']=sdp['ICE']
		if sdp.has_key('ANSWER'):
			self.sdp['ANSWER']=sdp['ANSWER']
					



class SimpleEcho(WebSocket):		
	def expressInterest(self,name,onSuccess,onError):
		print 'expressInterest called for name: '+name
	

	def addNewClientCallback(self):
		print 'addNewClientCallback called'
		print len(self.ccnClients)
		
	def addNewClient(self,data,obj):
		print 'Client is registered: ',registeredClients.has_key(data['userId'])
		if not registeredClients.has_key(data['userId']): 
			newCCNRegisterThread=ccnRegister(data['userId'],self.sendRequestToIPClient,data)
			newCCNRegisterThread.start()
			info={}
			info['obj']=obj
			info['threadRef']=newCCNRegisterThread		
			registeredClients[data['userId']]=info
		else:
			print 'Client data update'
			registeredClients[data['userId']]['threadRef'].updateSDP(data)


	def sendRequestToIPClient(self,name,callback):
		print 'sendRequestToIPClient called with name: ',
		print name
		print 'ccnClients content :'
		print self.ccnClients['/robert']
		socket=self.ccnClients['/robert']['socket']
		print dir(socket)
		socket.sendMessage('Hello client')
		
		#self.sendMessage('someone is calling you !')
		
		
	def makeCall(self,data):
		print 'makeCall method called with params:',
		print data['From'],
		print data['To']
		registeredClients[data['From']]['threadRef'].onMakeCall(data,self.makeCallErrorCallback,self.makeCallErrorCallback)


	def makeCallCallback(self):
		print 'makeCallCallback called'	
		self.sendMessage("asdasdasd")

	def makeCallErrorCallback(self,calling,message):
		print 'makeCallErrorCallback called with: ',calling,' , ',message		
		#registeredClients[calling]['obj'].sendMessage(u+message)
		registeredClients[calling]['obj'].sendMessage(unicode(message))

	def showNumberOfClients(self):
		print 'Number of CCN Clients:',
		print len(self.ccnClients)


	def callback(self,message):
		print message

	def handleConnected(self):
		print 'Peer connected. Address: ',self.address
		clients.append(self)
		showConnectedClients()
		self.sendMessage(u'Hello Client')


	def handleClose(self):
		print 'Peer disconnected. Address: ',self.address
		clients.remove(self)
		showConnectedClients()



	

	def handleMessage(self):
		
		print 'Received type: '+str(type(self.data))

		
		if type(self.data) is unicode:
			print 'Signaling message'
			print self.data
			dane=json.loads(self.data)
			#if dane:print type(dane)
			if type(dane)is dict:
				print dane['type']
		
				if dane['type']=='REGISTER':
					print 'REGISTER METHOD PROCESING'
					print 'message from client: ',dane['userId']
					
					showRegisteredClients()
					self.addNewClient(dane,self)
					

				if dane['type']=='CALL':
					print 'CALL CONNECTION '
					print 'self: ',self
					#self.clientSocket=self
					#print 'self.clientSocket: ',self.clientSocket
					print 'self.client: ',self.client
					#self.clientSocket.sendMessage('test')
					self.makeCall(dane)

				if dane['type']=='TEST':
					print 'Test of connection with peer'
					ss=json.dumps(dane,ensure_ascii=False)
					
					self.sendMessage(ss)
					print 'Message to client sent.'
					print 'Server socket: ',
					print self
					print 'Client socket: ',
					print self.client
					print 'Client address: ',self.address
					

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
			print 'User: ',self.nameId
			print 'Interest received !!!'
			name=upcallInfo.Interest.name
			print 'Received request: '+str(name)
			#payload='Hello Client'
			payload=json.dumps(self.sdpInfo,ensure_ascii=False)
			co=ccn.ContentObject(name)
			co.content=payload
			

			#self.callback('Received interest with name')
			#self.callback(str(name))

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

	mediaServer=MediaServer()
	mediaServer.start()
	
	def close_sig_handler(signal,frame):
		print 'close port called !'
		server.close()
		sys.exit()
	signal.signal(signal.SIGINT,close_sig_handler)
	server.serveforever()
	

	

