import pyccn as ccn
import threading,time
from utils import converter,logger
from protocol.Producer import ProducerClosure
from server.MediaServer import MediaServer


LOGGER=logger.Logger().get_logger()
LOGGER2=logger.Logger().get_logger()
LOGGER3=logger.Logger().get_logger()

class ccnRegister(threading.Thread):
	def __init__(self,threadId,callback,sdp,peerAddress):
		threading.Thread.__init__(self)
		self.threadId=threadId
		self.callback=callback
		self.sdp={}
		#self.sdp['SDP']=sdp['SDP']
		#self.sdp['ICE']=sdp['ICE']
		self.data=None
		self.mediaCounter=0
		self.mediaServer=MediaServer() #mediaServer
		self.mediaServer.setThreadName(self.threadId)
		self.isPeerSet=False
		LOGGER( 'ccnRegister thread constructor called')
		#LOGGER( 'dir mediaServer: ',dir(self.mediaServer))		
		
		#self.__setPeer__()

	def __setPeer__(self):
		LOGGER( '__setPeer__ called', self.isPeerSet, len(self.sdp['ICE']))

		
		if not self.isPeerSet:
			if len(self.sdp['ICE'])>0:	
				LOGGER( self.sdp['ICE'][0]['candidate'])
				self.mediaServer.setPeerAddress(converter.ice_offer_parser(self.sdp['ICE'][0]['candidate']))
				LOGGER( 'PeerAddress after setting: ',self.mediaServer.peerSocket)		
				self.isPeerSet=True
		
		
	def run(self):
		LOGGER( 'ccnRegister thread started !')
		self.mediaServer.start()
		LOGGER( 'media server for this thread: ',self.mediaServer.getSocket())
		name=ccn.Name(str(self.threadId))
		LOGGER( 'Name:',name)
		self.handler=ccn.CCN()


		interest_handler=ProducerClosure()
		interest_handler.callback=self.onInterest
		interest_handler.sdpInfo=self.sdp #only for test first phase
		interest_handler.nameId=name
		interest_handler.mediaServer=self.mediaServer
		res=self.handler.setInterestFilter(name,interest_handler)
		if(res<0):
			LOGGER( 'Some problems occured !')
		
		self.handler.run(-1)
		raise SystemError('Exited loop!')
	def onInterest(self,message):
		LOGGER( 'threadId: ',self.threadId,' onInterest called')
		LOGGER( message)
		self.callback(str(message),None)
	
	def onMakeCall(self,data,callback,errorCallback):
		self.data=data
		LOGGER( 'threadId: ',self.threadId,' onMakeCall called')
		LOGGER( 'sending request to: ',data['To'])
		LOGGER2( 'threadId: ',self.threadId,' onMakeCall called')
	
		
		urlName=data['To']+'/call'+data['From']
		LOGGER( 'Request URL: ',urlName)
		
		name=ccn.Name(str(urlName))
		ccnHandler=ccn.CCN()
		LOGGER('Before GET request to CCN')
		if 'co' in locals(): LOGGER2('ContentObject  exists in locals')
		if 'co' in globals(): LOGGER2('ContentObject  exists in globals') 
		if 'name' in locals(): 
			LOGGER2('name  exists in locals')
			LOGGER2(' request name is: ',name)
		if 'name' in globals(): LOGGER2('name  exists in globals')
		
					
		co=ccnHandler.get(name,timeoutms=500)
		LOGGER2('thread onMakeCall after co get !!!')
		LOGGER('onMakeCall called !!!!')
		
		
		
		LOGGER('After GET request to CCN')
		if 'co' in locals(): LOGGER('ContentObject  exists in locals')
		if 'co' in globals(): LOGGER('ContentObject  exists in globals') 
		if(co==None):
			LOGGER( 'No answer from server')
			LOGGER2( 'No answer from server')
			errorCallback(self.data['From'],'No answer from called')
		else:
			LOGGER( co.name)
			LOGGER2('co name: ',co.name)
			###################
			callback(self.data['From'],co.content)			
		

	def updateSDP(self,sdp):
		self.sdp['SDP']=sdp['SDP']
		self.sdp['ICE']=sdp['ICE']
		self.__setPeer__()
		if sdp.has_key('ANSWER'):
			self.sdp['ANSWER']=sdp['ANSWER']
	
	def onGetMedia(self,data,callback,errorCallback):
		self.data=data
		LOGGER( 'threadId: ',self.threadId,' onGetMedia called')
		LOGGER( 'sending request to: ',data['To'])
		self.mediaCounter+=1		
		urlName=data['To']+'/call'+data['From']+'/Media/'+str(self.mediaCounter)
		LOGGER( 'Request URL: ',urlName)
		name=ccn.Name(str(urlName))
		ccnHandler=ccn.CCN()
		co=ccnHandler.get(name,timeoutms=500)
		if(co==None):
			LOGGER( 'No answer from server')
			message={"TYPE":"GETMEDIA","RESULT":"NOUSER"}
			LOGGER3('# Register threadId: ',self.threadId,'message:\n',message)
			errorCallback(self.data['From'],message)
		else:
			
			if co.content=='':
				LOGGER( 'BUFFER EMPTY')
				message={"TYPE":"GETMEDIA","RESULT":"NODATA"}
				LOGGER3('# Register threadId: ',self.threadId,'message:\n',message)
				errorCallback(self.data['From'],message)		
			else:			
				message={"TYPE":"GETMEDIA","RESULT":"OK",
					"MEDIACOUNTER":self.mediaCounter
					}
				LOGGER3('# Register threadId: ',self.threadId,'message:\n',message)
				#self.mediaServer.input_queue.put(co.content)
				callback(self.data['From'],co.content,message)

	def onPutMedia(self,data):
		LOGGER( '#Register threadId: ',self.threadId,' onPutMedia called')
		self.mediaServer.output_queue.put(data)
		



