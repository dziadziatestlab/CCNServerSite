'''
    buffer for CCN packets

'''

from collections import deque

class CCNBuffer():
    def __init__(self,size):
        self._bufferLoad_=0
        self._size_=size
        self._deq_=deque(maxlen=size)

    def cleanBuffer(self):
        self._deq_.clear()
        
    def addPacket(self,data):
        self._deq_.append(data)
        self._bufferLoad_=self._deq_.__len__()
        
        #to test
        self.showBufferState()
        
    def readPacket(self):
        try:
            data=self._deq_.popleft()
        except IndexError: #exceptions.IndexError:
            # print "Buffer empty !!!"
            data=None
        return data

    def showBufferState(self):
		pass
        # print"----------------"
        # print "Size:  ",self._size_
        # print "Buffer Load: ",self._bufferLoad_
        if self._bufferLoad_>=self._size_:
            pass
			# print "Buffer is FULL"
        #print self._deq_
        
