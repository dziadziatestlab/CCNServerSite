import signal,sys,json
import pyccn as ccn
import threading,time
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer


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



class callbackRef():
	def __init__(self,callback):
		self.callback
	def showReference(self):
		print 'Callback reference object: ',
		print self.callback
	def getReference(self):
		return self.callback

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
			#self.callback()
			#self.errorCallback()
	






class ccnConnector(threading.Thread):
	def __init__(self,ipHandler):
		threading.Thread.__init__(self)
		self.ccnHandler=None
		self.ipHandler=ipHandler
		self.interestHandlers={}
		print '#ccnConnector created'
	def run(self):
		print '#ccnConnector thread started !'
		self.ccnHandler=ccn.CCN()
		#self.interestHandler=ProducerClosure()
		self.ipHandler.sendMessage(unicode('Hello my client!!!'))
		print 'ipHandler: ',
		print self.ipHandler
		print 'sendMessage ref: ',
		print self.ipHandler.sendMessage
		self.ccnHandler.run(-1)
		raise SystemError('Exited loop!')
	def addClient(self,clientId):
		print '#addClient called '
		name=ccn.Name(str(clientId))
		print '#Registering with name :',
		print name
		self.interestHandlers[name]=ProducerClosure()				
		self.ccnHandler.setInterestFilter(name,self.interestHandlers[name])

		


		



class makeCCNCall(threading.Thread):
	def __init__(self,IdFrom,IdTo,callback,errorCallback):
		threading.Thread.__init__(self)
		self.threadId=IdFrom		
		self.idFrom=IdFrom
		self.idTo=IdTo
		self.callback=callback
		self.errorCallback=errorCallback
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
			self.errorCallback()
		else:
			print co.name
			print co.content			
			#self.callback()
			self.errorCallback()
		

			
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

	'''
	################### Utils for tests  ################
	'''

	'''
	################### End of utils #################
	'''	



		
	def expressInterest(self,name,onSuccess,onError):
		print 'expressInterest called for name: '+name
	

	def addNewClientCallback(self):
		print 'addNewClientCallback called'
		print len(self.ccnClients)
		
	def addNewClient(self,data,obj):
		print 'Client is registered: ',registeredClients.has_key(data['userId'])
		if not registeredClients.has_key(data['userId']): 
			newCCNRegisterThread=ccnRegister(data['userId'],self.sendRequestToIPClient,data['SDP'])
			newCCNRegisterThread.start()
			info={}
			info['obj']=obj
			info['threadRef']=newCCNRegisterThread		
			registeredClients[data['userId']]=info


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
				if dane['type']=='Interest':
					self.expressInterest(dane['data'],onSuccess,onError)
					toCCN=sendToCCN(dane['data'],self.callback)
					toCCN.start()


				if dane['type']=='REGISTER':
					print 'REGISTER METHOD PROCESING'
					'''					
					print 'Client socket: ',
					print self.client
					print 'Server socket: ',
					print self
					dane['socket']=self
					#self.addNewClient(dane)
					#self.ccnThreadId.addClient(dane['userId'])	
					'''
					
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
			print 'Interest received !!!'
			name=upcallInfo.Interest.name
			print 'Received request: '+str(name)
			#payload='Hello Client'
			payload=self.sdpInfo
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
	
	def close_sig_handler(signal,frame):
		print 'close port called !'
		server.close()
		sys.exit()
	signal.signal(signal.SIGINT,close_sig_handler)
	server.serveforever()
	

	

