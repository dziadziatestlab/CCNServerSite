import json
from SimpleWebSocketServer import WebSocket
from server.MediaServer import MediaServer
from protocol.Register import ccnRegister
from utils import logger

LOGGER=logger.Logger().get_logger()

clients=[]
registeredClients={}

def showConnectedClients():
	LOGGER( 'Connected clients:')
	for client in clients:
		LOGGER( client.address)

def showRegisteredClients():
	LOGGER( 'Registered clients:')
	for client in registeredClients:
		LOGGER( client,'  :  ',registeredClients[client]['obj'].address)





class SimpleEcho(WebSocket):
	def attachMediaServer(self,mediaServer):
		LOGGER( 'attachMediaServer called')
		#self.mediaServer=mediaServer
			
	def expressInterest(self,name,onSuccess,onError):
		LOGGER( 'expressInterest called for name: '+name)
	

	def addNewClientCallback(self):
		LOGGER( 'addNewClientCallback called')
		LOGGER( len(self.ccnClients))
		
	def addNewClient(self,data,obj):
		LOGGER( 'Client is registered: ',registeredClients.has_key(data['userId']))
		if not registeredClients.has_key(data['userId']): 
			newCCNRegisterThread=ccnRegister(data['userId'],self.sendRequestToIPClient,data,self.mediaServer)   
			newCCNRegisterThread.start()
			info={}
			info['obj']=obj
			info['threadRef']=newCCNRegisterThread		
			registeredClients[data['userId']]=info
				################################################
			LOGGER( 'Generating answer for REGISTER')
			message={}
			message['ProxyServer']= self.mediaServer.getSocket()
			"""			
			message={'ProxyServer':{
					'host':self.mediaServer['HOST'],
					'port':self.mediaServer['PORT']
									

					}}

			"""
			LOGGER( 'Answer to REGISTER request:',message)
			message=json.dumps(message,ensure_ascii=False)
			registeredClients[data['userId']]['obj'].sendMessage(unicode(message))
		else:
			LOGGER( 'Client data update')
			registeredClients[data['userId']]['threadRef'].updateSDP(data)

			




	def sendRequestToIPClient(self,name,callback):
		LOGGER( 'sendRequestToIPClient called with name: ',name)
		LOGGER( 'ccnClients content :')
		LOGGER( self.ccnClients['/robert'])
		socket=self.ccnClients['/robert']['socket']
		#LOGGER( dir(socket))
		socket.sendMessage('Hello client')
		
		#self.sendMessage('someone is calling you !')
		
		
	def makeCall(self,data):
		LOGGER( 'makeCall method called with params:',data['From'], data['To'])
		registeredClients[data['From']]['threadRef'].onMakeCall(data,self.makeCallCallback,self.makeCallErrorCallback)


	def makeCallCallback(self,calling,message):
		LOGGER( 'makeCallCallback called with message: ',message)	
		#self.sendMessage("asdasdasd")
		registeredClients[calling]['obj'].sendMessage(unicode(message))		

	def makeCallErrorCallback(self,calling,message):
		LOGGER( 'makeCallErrorCallback called with: ',calling,' , ',message)		
		#registeredClients[calling]['obj'].sendMessage(u+message)
		
		# !!!!!!!!!!!!!!!!!!!!		
		#registeredClients[calling]['obj'].sendMessage(unicode(message))


	# retrieving media packets
	def getMedia(self,data):
		LOGGER( 'getMedia called')
		registeredClients[data['From']]['threadRef'].onGetMedia(data,self.getMediaCallback,self.getMediaErrorCallback)


	########################  tutaj poprawic wysylanie do calling -- socket
		
	def getMediaCallback(self,calling,data,message):
		LOGGER( 'getMediaCallback called')
		host='192.168.0.149'
		port=8891
		LOGGER( 'Data to be send: ')
		#LOGGER( data)
		self.sendMessage(unicode(json.dumps(message,ensure_ascii=False)))
		
		# do poprawienia przy wysylaniu
		#self.mediaServer.udpServer.socket.sendto(data,(host,port))

	def getMediaErrorCallback(self,calling,message):
		answerMessage=json.dumps(message,ensure_ascii=False)
		LOGGER( 'getMediaErrorCallback called with: ',calling,' , ',message)
		self.sendMessage(unicode(answerMessage))




	def showNumberOfClients(self):
		LOGGER( 'Number of CCN Clients:',len(self.ccnClients))


	def callback(self,message):
		LOGGER( message)

	def handleConnected(self):
		LOGGER( 'Peer connected. Address: ',self.address)

		if hasattr(self,'mediaServer')==False:
			self.mediaServer=MediaServer()
			self.mediaServer.start()

		clients.append(self)
		LOGGER( 'after append')
		showConnectedClients()
		LOGGER( 'after show')
		self.sendMessage(u'Hello Client')


	def handleClose(self):
		LOGGER( 'Peer disconnected. Address: ',self.address)
		clients.remove(self)
		showConnectedClients()
		if hasattr(self,'mediaServer')==True:
			self.mediaServer.onStop()



	

	def handleMessage(self):
		
		LOGGER( 'Received type: '+str(type(self.data)))
		# DEBUG:
		#LOGGER( 'DEBUG SimpleEcho self: ',self)
		#LOGGER( 'DEBUG: mediaServer ref: ',self.mediaServer)
		#LOGGER( 'DEBUG: mediaServer socket: ',self.mediaServer.getSocket())
		
		if type(self.data) is unicode:
			LOGGER( 'Signaling message')
			LOGGER( self.data)
			dane=json.loads(self.data)
			#if dane:LOGGER( type(dane))
			LOGGER( 'data type is :',type(dane))
			if type(dane)is dict:
				LOGGER( dane['type'])
		
				if dane['type']=='REGISTER':
					LOGGER( 'REGISTER METHOD PROCESING')
					LOGGER( 'message from client: ',dane['userId'])
					
					showRegisteredClients()
					self.addNewClient(dane,self)
					

				if dane['type']=='CALL':
					LOGGER( 'CALL CONNECTION ')
					LOGGER( 'self: ',self)
					#self.clientSocket=self
					#LOGGER( 'self.clientSocket: ',self.clientSocket)
					LOGGER( 'self.client: ',self.client)
					#self.clientSocket.sendMessage('test')
					self.makeCall(dane)

				if dane['type']=='TEST':
					LOGGER( 'Test of connection with peer')
					ss=json.dumps(dane,ensure_ascii=False)
					
					self.sendMessage(ss)
					LOGGER( 'Message to client sent.')
					LOGGER( 'Server socket: ',self)
					LOGGER( 'Client socket: ',self.client)
					LOGGER( 'Client address: ',self.address)
				if dane['type']=='GETMEDIA':
					LOGGER( 'GETMEDIA request arrived')
					self.getMedia(dane)

					

		if type(self.data) is bytearray:
			#values=bytearray(self.data)
			LOGGER( 'Inside loop')
			LOGGER( self.data.__sizeof__())
			for v in self.data:
				LOGGER( v)
			#LOGGER( dir(values))
			#LOGGER( 'Length array: '+str(values.length))
				


