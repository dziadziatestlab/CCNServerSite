#!/usr/bin/env python

import signal,sys,json
from utils import logger


from SimpleWebSocketServer import SimpleWebSocketServer
from server.SimpleEcho import SimpleEcho
#from MediaServer import MediaServer


LOGGER=logger.Logger().get_logger()

config_port=8000
config_host=''

#clients=[]
#registeredClients={}



if __name__=="__main__":
	LOGGER( 'proxy Server is going to start')
	server=SimpleWebSocketServer('',8000,SimpleEcho)
	def close_sig_handler(signal,frame):
		LOGGER( 'close port called !')
		server.close()
		sys.exit()
	signal.signal(signal.SIGINT,close_sig_handler)
	server.serveforever()
	

	

