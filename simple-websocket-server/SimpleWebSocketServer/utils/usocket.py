import socket

def get_ip_address():
	url='www.orange.pl'
	s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	s.connect((url,0))
	local_address=s.getsockname()[0]
	return local_address


if __name__=='__main__':
	print 'Starting get_ip_address from script'
	print get_ip_address()

