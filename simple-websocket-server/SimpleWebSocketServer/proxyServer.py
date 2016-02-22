#!/usr/bin/env python

import signal,sys,json


from SimpleWebSocketServer import SimpleWebSocketServer
from server.SimpleEcho import SimpleEcho
#from MediaServer import MediaServer




config_port=8000
config_host=''

#clients=[]
#registeredClients={}



if __name__=="__main__":
	print 'proxy Server is going to start'
	server=SimpleWebSocketServer('',8000,SimpleEcho)
	def close_sig_handler(signal,frame):
		print 'close port called !'
		server.close()
		sys.exit()
	signal.signal(signal.SIGINT,close_sig_handler)
	server.serveforever()
	

	

