




def ice_offer_parser(ice):
	host=ice.split(" ")[-4].encode('ascii','ignore') #ip address
	port=int(ice.split(" ")[-3].encode('ascii','ignore')) #port	

	return (host,port)
