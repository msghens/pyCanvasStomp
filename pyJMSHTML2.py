#!/home/SBCC/msghens/pyADAP-env/bin/python
# -*- coding: utf-8 -*-
#
#  pyJMSHTML2.py
#  
#  


#~ Python ADAP replacement. This uses Glassfish STOMP for connections

import sys
import signal
import logging
import logging.handlers
from stompy.simple import Client
import xmltodict
from pprint import pprint
import base64,zlib
import time
import requests
import json
import random
import StringIO
import csv
import hashlib
import os
from person import Person
from pyJMSHTML2_config import apikey,stomp_password,stomp_username





BASE_URL = 'https://sbcc.instructure.com/api/v1/accounts/1/sis_imports.json'

headers = {'Authorization' : 'Bearer ' + apikey()}
payloadCSV = {'import_type' : 'instructure_csv', 'extension' : 'csv', 'override_sis_stickiness' : 'true'}
payloadXML = {'import_type' : 'ims_xml', 'extension' : 'xml', 'override_sis_stickiness' : 'true'}


class GracefulKiller():
	#http://stackoverflow.com/questions/3850261/doing-something-before-program-exit
	kill_now = False
	def __init__(self):
		signal.signal(signal.SIGINT, self.exit_gracefully)
		signal.signal(signal.SIGTERM, self.exit_gracefully)

	def exit_gracefully(self,signum, frame):
		self.kill_now = True

def isPersonRecord(imsxml):
	if 'person' in imsxml['enterprise']:
		return True
	else:
		return False
		
def make_secret(password):
    """
    Encodes the given password as a base64 SSHA hash+salt buffer
    From: https://gist.github.com/rca/7217540
    """
    salt = os.urandom(4)

    # hash the password and append the salt
    sha = hashlib.sha1(password)
    sha.update(salt)

    # create a base64 encoded string of the concatenated digest + salt
    digest_salt_b64 = '{}{}'.format(sha.digest(), salt).encode('base64').strip()

    # now tag the digest above with the {SSHA} tag
    tagged_digest_salt = '{{SSHA}}{}'.format(digest_salt_b64)

    return digest_salt_b64



def isMemberRecord(imsxml):
	#~ Is member record, but not cross list
	if 'membership' in imsxml['enterprise'] :
		if '@roletype' in imsxml['enterprise']['membership']['member']['role']:
			return True
		else:
			return False
	else:
		return False
		
def send_record(data,payload = payloadXML):
	for n in range(0, 6):
		if n > 5:
			sys.exit("API problems, failed to complete")
		try:
			r = requests.post(BASE_URL, headers=headers, params=payload, data=data)
			#~ print r.text
			break
		except requests.exceptions.RequestException as e:
			logger.info(str(e))
			break
		except (KeyboardInterrupt, SystemExit):
			sys.exit("User keyboard termination")
		except:
			#backoff
			time.sleep((2 ** n) + random.randint(0, 1000) / 1000)
			pass
	#fix UnboundLocalError: local variable 'r' referenced before assignment error
	try:
		return r
	except:
		return "Network Error"

def run_stomp():
	username = stomp_username()
	password = stomp_password()
	#~ Does connection and loops the stomp connection
	stomp = Client(host='127.0.0.1', port=7672)
	
	try:
		stomp.connect(username=username,password=password, clientid='pyCanvasPROD2'  )
	except:
		sys.exit("Cannot connect to STOMP Server")
	
	stomp.subscribe('/topic/com_sct_ldi_sis_Sync')

	while True:
		killer = GracefulKiller()
		
			
		try:
			message = stomp.get()
			imsrecord = xmltodict.parse(message.body)
		except Exception, e:
			logger.error("Stomp/XML: " + str(e))
			continue
		
		#pprint(imsrecord)
		if isMemberRecord(imsrecord):
			memberRecord = dict()
			memberRecord['course_id'] = None
			memberRecord['section_id'] = imsrecord['enterprise']['membership']['sourcedid']['id']
			memberRecord['user_id'] = imsrecord['enterprise']['membership']['member']['sourcedid']['id']
			#~ pprint(imsrecord['enterprise']['membership']['member']['role'])
			if imsrecord['enterprise']['membership']['member']['role']['@roletype'] == '02':
				memberRecord[u'role'] = 'teacher'
			else:
				memberRecord['role'] = 'student'
			if imsrecord['enterprise']['membership']['member']['role']['status'] == '1':
				memberRecord['status'] = 'active'
			else:
				memberRecord['status'] = 'deleted'
			
			output = None
			output = StringIO.StringIO()
			#~ pprint(memberRecord)
			#~ print memberRecord.keys()
			#~ writer = csv.DictWriter(output,dialect='excel',fieldnames=['sis_user_id','role','sis_section_id','status'])
			writer = csv.DictWriter(output,dialect='excel',fieldnames=memberRecord.keys(),lineterminator='\n')
			writer.writeheader()
			writer.writerow(memberRecord)
			
			#~ r = send_record(message.body)
			r = send_record(output.getvalue(),payloadCSV)
			logger.info(output.getvalue())
			output.close()
			#~ pprint(imsrecord)
			logger.info(message.body)
			try:
				logger.info(r.text)
			except:
				logger.error(r)
				pass
		elif isPersonRecord(imsrecord):
			try:
				imsperson = Person(imsrecord)
			except:
				logger.info('Person Error: %s', sys.exc_info()[0])
				continue
			
			personRecord = dict()
			personRecord['user_id'] = imsperson.sourcedId
			personRecord['login_id'] = imsperson.userid
			personRecord['first_name'] = imsperson.fname
			personRecord['last_name'] = imsperson.lname
			personRecord['short_name'] = imsperson.sisplayName2
			personRecord['email'] = imsperson.email
			personRecord['status'] = 'active'
			
			output = None
			output = StringIO.StringIO()
			writer = csv.DictWriter(output,dialect='excel',fieldnames=personRecord.keys(),lineterminator='\n')
			writer.writeheader()
			writer.writerow(personRecord)
			
			#~ r = send_record(message.body)
			r = send_record(output.getvalue(),payloadCSV)
			logger.info(output.getvalue())
			output.close()
			#~ pprint(imsrecord)
			logger.info(message.body)
			try:
				logger.info(r.text)
			except:
				logger.error(r)
				pass

		else:
			try:
				r = send_record(message.body,payloadXML)
				logger.info(message.body)
				logger.info(r.text)
				#~ pprint(imsrecord)
			except:
				logger.error("Network Issues")
				pass
			
			
		#Return
		try:
			#~ print r.text
			logger.info(r.text)
		except:
			logger.error("Live feed fail")
		
		if killer.kill_now:
			logger.info("Shutting Down")
			stomp.unsubscribe('/topic/com_sct_ldi_sis_Sync')
			stomp.disconnect()
			return



def initLogging():
	global logger
	#Initialize logging
	LOG_FILENAME = 'logs/pyJMSHTML.log'
	logger = logging.getLogger('pyJMSHTML')
	logger.setLevel(logging.DEBUG)
	
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	#Log file handler
	handler = logging.handlers.RotatingFileHandler(
					LOG_FILENAME, maxBytes=1024*1024, backupCount=10)

						
	#Console gets debug
	#~ console = logging.StreamHandler()
	#~ console.setFormatter(formatter)
	# create formatter and add it to the handlers
	#~ formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)				
	logger.addHandler(handler)
	#~ logger.addHandler(console)


def main():
	
	initLogging()
	
	logger.info('Starting pyJMSHTML')
	run_stomp()
	logger.info('Stopping pyJMSHTML')
	
	return 0

if __name__ == '__main__':
	main()

