import pyccn as ccn
import threading,time
from utils import converter
from protocol.Producer import ProducerClosure

class ccnRegister(threading.Thread):
	def __init__(self,threadId,callback,sdp,mediaServer):
		threading.Thread.__init__(self)
		self.threadId=threadId
		self.callback=callback
		self.sdp={}
		self.sdp['SDP']=sdp['SDP']
		self.sdp['ICE']=sdp['ICE']
		self.data=None
		self.mediaCounter=0
		self.mediaServer=mediaServer
		self.isPeerSet=False
		print 'ccnRegister thread constructor called'
		#print 'dir mediaServer: ',dir(self.mediaServer)		
		print 'media server for this thread: ',self.mediaServer.getSocket()
		self.__setPeer__()

	def __setPeer__(self):
		print '__setPeer__ called', self.isPeerSet, len(self.sdp['ICE'])

		
		if not self.isPeerSet:
			if len(self.sdp['ICE'])>0:	
				print self.sdp['ICE'][0]['candidate']
				self.mediaServer.setPeerAddress(converter.ice_offer_parser(self.sdp['ICE'][0]['candidate']))
				print 'PeerAddress after setting: ',self.mediaServer.peerSocket;		
				self.isPeerSet=True
		
		
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
		interest_handler.mediaServer=self.mediaServer
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
		co=ccnHandler.get(name,timeoutms=100)
		if(co==None):
			print 'No answer from server'
			errorCallback(self.data['From'],'No answer from called')
		else:
			print co.name
			callback(self.data['From'],co.content)			

	def updateSDP(self,sdp):
		self.sdp['SDP']=sdp['SDP']
		self.sdp['ICE']=sdp['ICE']
		self.__setPeer__()
		if sdp.has_key('ANSWER'):
			self.sdp['ANSWER']=sdp['ANSWER']
	
	def onGetMedia(self,data,callback,errorCallback):
		self.data=data
		print 'threadId: ',self.threadId,' onGetMedia called'
		print 'sending request to: ',data['To']
		self.mediaCounter+=1		
		urlName=data['To']+'/call'+data['From']+'/Media/'+str(self.mediaCounter)
		print 'Request URL: ',urlName
		name=ccn.Name(str(urlName))
		ccnHandler=ccn.CCN()
		co=ccnHandler.get(name,timeoutms=100)
		if(co==None):
			print 'No answer from server'
			message={"TYPE":"GETMEDIA","RESULT":"NOUSER"}
			
			errorCallback(self.data['From'],message)
		else:
			
			if co.content=='':
				print 'BUFFER EMPTY'
				message={"TYPE":"GETMEDIA","RESULT":"NODATA"}
				errorCallback(self.data['From'],message)		
			else:			
				message={"TYPE":"GETMEDIA","RESULT":"OK",
					"MEDIACOUNTER":self.mediaCounter
					}
				self.mediaServer.input_queue.put(co.content)
				callback(self.data['From'],co.content,message)



