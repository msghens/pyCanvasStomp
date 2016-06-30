#Not secure. (could used keyzar). Just want to prevent shoulder surfing

#Modules used separate passwords from program

import base64,zlib



zd_b64d = lambda s: zlib.decompress(base64.decodestring(s))


def apikey:
	return zd_b64d('Replace with encoded apikey')
	
def stomp_username:
	return zd_b64d('Replace with encoded stomp username')
	
def stomp_password:
	return zd_b64d('Replace with encoded stomp password')
	
