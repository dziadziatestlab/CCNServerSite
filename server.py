import pyccn as ccn
import sys


name=ccn.Name('/robert/ping')
print 'Name created: '+str(name)

h=ccn.CCN()
print 'Handler created.'
key=h.getDefaultKey()
kl=ccn.KeyLocator()
kl.key=key


class ProducerClosure(ccn.Closure):
	def upcall(self,kind,upcallInfo):
		if(kind==ccn.UPCALL_FINAL):
			pass
		elif(kind==ccn.UPCALL_INTEREST):
			print 'Interest received !!!'
			name=upcallInfo.Interest.name
			print 'Received request: '+str(name)
			payload='Hello Client'
			co=ccn.ContentObject(name)
			co.content=payload
			
			si=ccn.SignedInfo()
			si.publisherPublicKeyDigest=key.publicKeyID
			si.type=ccn.CONTENT_DATA
			si.keyLocator=kl
			co.signedInfo=si

			co.sign(key)

			if(co.matchesInterest(upcallInfo.Interest)):
				res=h.put(co)
				if(res>=0):
					print payload
					return ccn.RESULT_INTEREST_CONSUMED
				else:
					raise SystemError('Failed to put ContentObject')
			else:
				sys.stderr.write(payload+' NOT SENT !')
		return ccn.RESULT_OK

			


interest_handler=ProducerClosure()
res=h.setInterestFilter(name,interest_handler)
if(res<0):
	print 'Some problems occured !'

h.run(-1)
raise SystemError('Exited loop!')







