import pyccn as ccn

name=ccn.Name('/robert/ping')
print 'Request created: '+str(name)

h=ccn.CCN()
print 'Handler created.'

for i in range(2):
	co=h.get(name,timeoutms=2000)
	if(co==None):
		print 'No aswer from server'
	else:	
		print co.name	
		print co.content

