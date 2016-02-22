import json
from SimpleWebSocketServer import WebSocket
from server.MediaServer import MediaServer
from protocol.Register import ccnRegister

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





class SimpleEcho(WebSocket):
	def attachMediaServer(self,mediaServer):
		print 'attachMediaServer called'
		#self.mediaServer=mediaServer
			
	def expressInterest(self,name,onSuccess,onError):
		print 'expressInterest called for name: '+name
	

	def addNewClientCallback(self):
		print 'addNewClientCallback called'
		print len(self.ccnClients)
		
	def addNewClient(self,data,obj):
		print 'Client is registered: ',registeredClients.has_key(data['userId'])
		if not registeredClients.has_key(data['userId']): 
			newCCNRegisterThread=ccnRegister(data['userId'],self.sendRequestToIPClient,data,self.mediaServer)   
			newCCNRegisterThread.start()
			info={}
			info['obj']=obj
			info['threadRef']=newCCNRegisterThread		
			registeredClients[data['userId']]=info
				################################################
			print 'Generating answer for REGISTER'
			message={}
			message['ProxyServer']= self.mediaServer.getSocket()
			"""			
			message={'ProxyServer':{
					'host':self.mediaServer['HOST'],
					'port':self.mediaServer['PORT']
									

					}}

			"""
			print 'Answer to REGISTER request:',
			print message
			message=json.dumps(message,ensure_ascii=False)
			registeredClients[data['userId']]['obj'].sendMessage(unicode(message))
		else:
			print 'Client data update'
			registeredClients[data['userId']]['threadRef'].updateSDP(data)

			




	def sendRequestToIPClient(self,name,callback):
		print 'sendRequestToIPClient called with name: ',
		print name
		print 'ccnClients content :'
		print self.ccnClients['/robert']
		socket=self.ccnClients['/robert']['socket']
		#print dir(socket)
		socket.sendMessage('Hello client')
		
		#self.sendMessage('someone is calling you !')
		
		
	def makeCall(self,data):
		print 'makeCall method called with params:',
		print data['From'],
		print data['To']
		registeredClients[data['From']]['threadRef'].onMakeCall(data,self.makeCallCallback,self.makeCallErrorCallback)


	def makeCallCallback(self,calling,message):
		print 'makeCallCallback called with message: ',message	
		#self.sendMessage("asdasdasd")
		registeredClients[calling]['obj'].sendMessage(unicode(message))		

	def makeCallErrorCallback(self,calling,message):
		print 'makeCallErrorCallback called with: ',calling,' , ',message		
		#registeredClients[calling]['obj'].sendMessage(u+message)
		
		# !!!!!!!!!!!!!!!!!!!!		
		#registeredClients[calling]['obj'].sendMessage(unicode(message))


	# retrieving media packets
	def getMedia(self,data):
		print 'getMedia called'
		registeredClients[data['From']]['threadRef'].onGetMedia(data,self.getMediaCallback,self.getMediaErrorCallback)


	########################  tutaj poprawic wysylanie do calling -- socket
		
	def getMediaCallback(self,calling,data,message):
		print 'getMediaCallback called'
		host='192.168.0.149'
		port=8891
		print 'Data to be send: ',
		#print data
		self.sendMessage(unicode(json.dumps(message,ensure_ascii=False)))
		
		# do poprawienia przy wysylaniu
		#self.mediaServer.udpServer.socket.sendto(data,(host,port))

	def getMediaErrorCallback(self,calling,message):
		answerMessage=json.dumps(message,ensure_ascii=False)
		print 'getMediaErrorCallback called with: ',calling,' , ',message
		self.sendMessage(unicode(answerMessage))




	def showNumberOfClients(self):
		print 'Number of CCN Clients:',
		print len(self.ccnClients)


	def callback(self,message):
		print message

	def handleConnected(self):
		print 'Peer connected. Address: ',self.address

		if hasattr(self,'mediaServer')==False:
			self.mediaServer=MediaServer()
			self.mediaServer.start()

		clients.append(self)
		print 'after append'
		showConnectedClients()
		print 'after show'
		self.sendMessage(u'Hello Client')


	def handleClose(self):
		print 'Peer disconnected. Address: ',self.address
		clients.remove(self)
		showConnectedClients()
		if hasattr(self,'mediaServer')==True:
			self.mediaServer.onStop()



	

	def handleMessage(self):
		
		print 'Received type: '+str(type(self.data))
		# DEBUG:
		#print 'DEBUG SimpleEcho self: ',self
		#print 'DEBUG: mediaServer ref: ',self.mediaServer
		#print 'DEBUG: mediaServer socket: ',self.mediaServer.getSocket()
		
		if type(self.data) is unicode:
			print 'Signaling message'
			print self.data
			dane=json.loads(self.data)
			#if dane:print type(dane)
			print 'data type is :',type(dane)
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
				if dane['type']=='GETMEDIA':
					print 'GETMEDIA request arrived'
					self.getMedia(dane)

					

		if type(self.data) is bytearray:
			#values=bytearray(self.data)
			print 'Inside loop'
			print self.data.__sizeof__()
			for v in self.data:
				print v
			#print dir(values)
			#print 'Length array: '+str(values.length)
				


