'''
    buffer for CCN packets

'''
from utils import logger
from collections import deque


LOGGER=logger.Logger(True).get_logger()


class CCNBuffer():
    def __init__(self,size):
        self._bufferLoad_=0
        self._size_=size
        self._deq_=deque(maxlen=size)

    def cleanBuffer(self):
        self._deq_.clear()
        
    def addPacket(self,data):
	LOGGER('write packet to buffer ')
        self._deq_.append(data)
        self._bufferLoad_=self._deq_.__len__()
        
        #to test
        self.showBufferState()
        
    def readPacket(self):
	LOGGER('read packet from buffer')
        try:
            data=self._deq_.popleft()
        except IndexError: #exceptions.IndexError:
            LOGGER( "Buffer empty !!!")
            data=None
        return data

    def showBufferState(self):
        LOGGER("----------------")
        LOGGER( "Size:  ",self._size_)
        LOGGER( "Buffer Load: ",self._bufferLoad_)
        if self._bufferLoad_>=self._size_:
            LOGGER( "Buffer is FULL")
        #LOGGER( self._deq_)
        
