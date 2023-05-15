# -*- coding: utf-8 -*-
#~ Representation of the Ellucian Person Class. Class will be used
#~ to make it easier to pass information between defs and processes.
#~ 
#~ Unlike the google provisioning that uses dictionary to represent a the user

import logging
import xmltodict
import random
import string


# setting module logger

logger = logging.getLogger('pyJMSHTML.PersonRec')


class Person(object):
	#~ primaryRole = 'norole'

	def __init__(self,imsxml):
		self.userid = self.getUserID(imsxml)
		logger.debug('Userid: %s', self.userid)
		self.fname = self.getFname(imsxml)
		logger.debug('Firstname: %s', self.fname)
		self.lname = self.getLname(imsxml)
		logger.debug('Lastname: %s', self.lname)
		self.middle = self.getMiddle(imsxml)
		logger.debug('Middlename: %s', self.middle)
		self.displayName = self.getdisplayName(imsxml)
		logger.debug('DisplayName: %s', self.displayName)
		self.sisplayName2 = self.fname + ' ' + self.lname
		logger.debug('DisplayName2: %s', self.sisplayName2)
		self.primaryRole = self.getPrimaryRole(imsxml)
		logger.debug('Primary Role: %s', self.primaryRole)
		self.email = self.getEmail(imsxml)
		logger.debug('Email: %s', self.email)
		self.knumber = self.getKnumber(imsxml)
		logger.debug('Knumber: %s', self.knumber)
		self.password = self.getPasswd(imsxml)
		logger.debug('Password: %s', "XXXXXX")
		self.sourcedId = self.getSourcedId(imsxml)
		logger.debug('sourcedId: %s', self.sourcedId)
		
		
		
	def getUserID(self,imsxml):
		for uid in imsxml['enterprise']['person']['userid']:
			if 'Logon ID' in uid['@useridtype']:
				return uid['#text']
		raise IndexError('SCTID not found')		 
		

	def getPrimaryRole(self,imsxml):
		if type(imsxml['enterprise']['person']['extension']['luminisperson']['customrole']) is unicode:
			role = imsxml['enterprise']['person']['extension']['luminisperson']['customrole']
			if role.startswith('Primary'):
				logger.debug('Primary Role: %s', role)
				return role
			else:
				logger.debug('Primary Role: none')
				return 'none'
		for role in imsxml['enterprise']['person']['extension']['luminisperson']['customrole']:
			if role.startswith('Primary'): 
				logger.debug('Primary Role: %s', role)
				return role
		logger.debug('Primary Role: none')
		return 'none'
		
	def getFname(self,imsxml):
		return imsxml['enterprise']['person']['name']['n']['given']
		
	def getLname(self,imsxml):
		return imsxml['enterprise']['person']['name']['n']['family']
		
	def getMiddle(self,imsxml):
		try:
			return imsxml['enterprise']['person']['name']['n']['partname']['#text']
		except:
			return ' '
		
	def getdisplayName(self,imsxml):
		return imsxml['enterprise']['person']['name']['fn']
	
	def getEmail(self,imsxml):
		try:
			return imsxml['enterprise']['person']['email']
		except LookupError:
			logger.info('Email address not found, creating pipeline address')
			return self.userid + '@pipeline.sbcc.edu'
			return
		except:
			logger.info('Email Runtime error')
			return 'noemailaddress' 
	
	def getKnumber(self,imsxml):
		for knumber in imsxml['enterprise']['person']['userid']:
			if 'SCTID' in knumber['@useridtype']:
				return knumber['#text']
		raise IndexError('SCTID not found')
		 
	def getPasswd(self,imsxml):
		return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
		#Passwords are no longer send through LMS
		# for passwd in imsxml['enterprise']['person']['userid']:
			# if 'SCTID' in passwd['@useridtype']:
				# return passwd['@password']
		raise IndexError('SCTID not found')		 
	
	def getSourcedId(self,imsxml):
		return imsxml['enterprise']['person']['sourcedid']['id']