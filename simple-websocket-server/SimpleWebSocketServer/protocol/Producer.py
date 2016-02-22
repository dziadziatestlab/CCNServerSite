import pyccn as ccn
import json

class callbackInfo():
	def __init__(self):
		self.callback=None
		self.sdpInfo=None #only for tests of first phase
		self.nameId=None
		self.mediaServer=None
	

class ProducerClosure(ccn.Closure,callbackInfo):
	def __init__(self):
		callbackInfo.__init__(self)

	def _queue_request_(self):
		pass

	def on_read_result(self,data):
		self.payload=data
		self.inProgress=False	

	def upcall(self,kind,upcallInfo):
		if(kind==ccn.UPCALL_FINAL):
			pass
		elif(kind==ccn.UPCALL_INTEREST):
			self.inProgress=True
			self.payload='test hello packet'
			print 'User: ',self.nameId
			print 'Interest received !!!'
			name=upcallInfo.Interest.name
			print 'Received request: '+str(name)
			#payload='Hello Client'
			#payload='test hello packet'
			if('/Media/' in str(name)):
				print ' /Media/ triger found in name'
				if hasattr(self,'mediaServer'):
					print 'OK. MediaServer exists'


					#payload=self.mediaServer.buffer.readPacket()
						
					'''
					if hasattr(self.mediaServer.udpServer,'ccnBuffer'):
						print 'OK. Buffer found !!!'
						payload=self.mediaServer.buffer.readPacket()
					'''
					self.mediaServer.read_queue.put(self.on_read_result)
					# wait for data response	
					while self.inProgress:
						pass

				else:
					self.payload='No media server found'
			else:
				self.payload=json.dumps(self.sdpInfo,ensure_ascii=False)
			

			






			co=ccn.ContentObject(name)
			co.content=self.payload
			

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
					#print payload
					return ccn.RESULT_INTEREST_CONSUMED
				else:
					raise SystemError('Failed to put ContentObject')
			else:
				sys.stderr.write(payload+' NOT SENT !')
		return ccn.RESULT_OK


