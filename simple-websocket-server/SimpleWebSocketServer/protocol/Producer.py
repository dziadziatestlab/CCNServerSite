import pyccn as ccn
import json
from utils import logger

LOGGER=logger.Logger().get_logger()
LOGGER2=logger.Logger().get_logger()
LOGGER3=logger.Logger(True).get_logger()

class callbackInfo():
	def __init__(self):
		self.callback=None
		self.sdpInfo=None #only for tests of first phase
		self.nameId=None
		self.mediaServer=None
	

class ProducerClosure(ccn.Closure,callbackInfo):
	def __init__(self):
		LOGGER3('#Producer: Producer init !!!')
		callbackInfo.__init__(self)
		self.payload=''

	def _queue_request_(self):
		pass

	def on_read_result(self,data):
		LOGGER( 'on_read_result called !!!')
		LOGGER3( '#Producer on_read_result called with data length:',len(data))
		if data==None: 
			LOGGER3('#Producer: on_read_result data==NONE !')
			self.payload=''		
		self.payload=data
		self.inProgress=False	

	def upcall(self,kind,upcallInfo):
		LOGGER3('#Producer upcall called !!!!!!')
		if(kind==ccn.UPCALL_FINAL):
			pass
		elif(kind==ccn.UPCALL_INTEREST):
			self.inProgress=True
			self.payload='unknow request'
			LOGGER3('#Producer: User: ',self.nameId)
			LOGGER3( '#Producer: Interest received !!!')
			name=upcallInfo.Interest.name
			#LOGGER( 'Received request: '+str(name))
			#LOGGER2( 'Received request: '+str(name))
			LOGGER3(' #Producer: received request: ',str(name))
			#payload='Hello Client'
			#payload='test hello packet'
			if('/Media/' in str(name)):
				LOGGER3( '#Producer: /Media/ triger found in name')
				if hasattr(self,'mediaServer'):
					LOGGER3( '#Producer: OK. MediaServer exists')


					#payload=self.mediaServer.buffer.readPacket()
						
					'''
					if hasattr(self.mediaServer.udpServer,'ccnBuffer'):
						LOGGER( 'OK. Buffer found !!!')
						payload=self.mediaServer.buffer.readPacket()
					'''
					self.mediaServer.read_queue.put(self.on_read_result)
					# wait for data response	
					while self.inProgress:
						pass

					LOGGER3('#Producer: data from buffer obtained !!!')

				else:
					self.payload='No media server found'
			
			elif('/call/' in str(name)):

				self.payload=json.dumps(self.sdpInfo,ensure_ascii=False)

			'''			
			else:
				self.payload=json.dumps(self.sdpInfo,ensure_ascii=False)
			
			'''
			
			#LOGGER('payload to pack into CO message:\n',self.payload)
			LOGGER3('#Producer: payload length to pack into CO message:',len(self.payload))



			co=ccn.ContentObject(name)
			LOGGER3('#Producer: contentObject name:',co.name)			
			co.content=self.payload
			LOGGER3('#Producer: contentObject payload length:',len(co.content))
			

			#self.callback('Received interest with name')
			#self.callback(str(name))
			
			LOGGER3('#Producer: start to produce response')
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
			LOGGER('#Producer:  response ready !')

			if(co.matchesInterest(upcallInfo.Interest)):
				res=handler.put(co)
				if(res>=0):
					#LOGGER( payload)
					LOGGER3('#Producer: interest consumed !')
					return ccn.RESULT_INTEREST_CONSUMED
				else:
					LOGGER3('#Producer: Failed to put ContentObject !!!')
					raise SystemError('Failed to put ContentObject')
			else:
				LOGGER3('#Producer: problem with Interest sending. Not Sent !')
				sys.stderr.write(payload+' NOT SENT !')
		return ccn.RESULT_OK


