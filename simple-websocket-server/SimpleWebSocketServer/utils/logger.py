


class Logger():
	def __init__(self,isAllowed=False):
		self.isAllowed=isAllowed
	
	def __logger__(self,*msgs):
		if self.isAllowed:
			for msg in msgs:
				print msg,
			print ' '

	def get_logger(self):
		return self.__logger__
		
