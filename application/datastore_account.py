from google.appengine.ext import ndb
import logging
import json
import util_notify
from pbkdf2 import PBKDF2


class Account(ndb.Model):
	"""
	Appengine entity for user data
	"""
	username = ndb.StringProperty(indexed=False)
	email = ndb.StringProperty(indexed=False)
	email_lower = ndb.ComputedProperty(lambda self: self.email.lower(),indexed=True)
	salt = ndb.StringProperty(indexed=False)
	salted_password = ndb.StringProperty(indexed=False)
	subscribed_to=ndb.IntegerProperty(repeated=True, indexed=False)
	owns_channels=ndb.KeyProperty(repeated=True, indexed=False)
	published_loops=ndb.KeyProperty(repeated=True, indexed=False)
	received_loops=ndb.KeyProperty(repeated=True, indexed=False)
	answeredLoops=ndb.IntegerProperty(repeated=True, indexed=False)
	oneSignalUid=ndb.StringProperty(repeated=True,indexed=False)


@ndb.transactional(retries=10)
def storeNewUser(verification_data):
	"""
	Returns True if new user was successfully created, 
	False otherwise, 
	verification_data should be a tuple with email, salt and a salted hashed password in that order
	"""
	account=Account(email=verification_data[0],salt=verification_data[1], salted_password=verification_data[2]) #create entity
	key=account.put ()  #store entity
	if key:
		return True
	else:
		return False


@ndb.transactional(retries=10)
def setOneSignalId(userId, oneSignalUid):
	"""Sets the id for sending signals to OneSignal, returns the user key if successfully saved"""

	user=Account.get_by_id(long(userId))
	if user.oneSignalUid is None:
		user.oneSignalUid=[]
	if oneSignalUid not in user.oneSignalUid:
		user.oneSignalUid.append(oneSignalUid)
		return user.put()
	return False
	# if(user.oneSignalUid==oneSignalUid):
		# return False
	# user.oneSignalUid=oneSignalUid
	# return user.put()
def getOneSignalId(userId):
	"""Returns The ids for sending notifications to oneSignal or an empty list if none is registered"""
	user=Account.get_by_id(long(userId))
	if(user.oneSignalUid != None):
		return user.oneSignalUid
	else:
		return []
def get_user_verification_data_by_email(email):
	"""
	Returns a tuple containing the users id, salt and salted hashed password
	if the user exists and is unique, otherwise returns false. Use get_user_verification_data_by_id instead if possible
	as this uses a query and is therefore expensive and slow comparatively
	"""

	query=Account.query(Account.email_lower==email.lower())
	user=query.get()
	if user==None:
		return False
	if query.count() == 1:
		return(user.key.id(),user.salt,user.salted_password)
	else:
		return False
def get_user_verification_data_by_id(user_id):
	"""
	Returns a tuple containing the users id, salted and hashed password and the randomly generated salt 
	if the user exists and is unique, otherwise returns false. Faster than by email as it does not run a query.
	"""
	user=Account.get_by_id(long(user_id))
	if user==None:
		return False
	return (user.key.id(),user.salt, user.salted_password)

def addChannelToSubscribed(userId,channelId):
	"""Adds the channelId to the list of subscribed channels"""
	user=Account.get_by_id(long(userId))
	if user==None:
		return False
	if not long(channelId) in user.subscribed_to:
		user.subscribed_to.append(long(channelId))
		user.put()
		return True
	return False
def getSubscribedChannels(userId):
	user=Account.get_by_id(long(userId))
	return user.subscribed_to
def removeAnsweredLoops(userId, loops):
	"""
	loops should be a tuple of (channelId,channelName, channelDescription, activeLoopId, loopItems), loads the users account
	Compares the loop id component to the list of answered loops.
	It then removes answered loops from the list
	"""
	activeLoopIdPosition=3;
	acc=Account.get_by_id(long(userId));
	return [loop for loop in loops if loop[activeLoopIdPosition] not in acc.answeredLoops]
def setAnsweredLoop(userId, loopId):
	acc=Account.get_by_id(long(userId));
	acc.answeredLoops.append(long(loopId));
	acc.put()
def notifyAllSubscribers(subscriberList):
	"""
	Takes in a list of subscriber ids
	Returns a list of the OneSignal user ids from the list of subscribers for testing purposes
	"""
	uidList=[]
	logging.info(subscriberList)
	for sub in subscriberList:
		logging.info(sub)
		acc=Account.get_by_id(sub)
		if acc:
			if acc.oneSignalUid:
				logging.info('subscriber onesignal id: ')
				logging.info(acc.oneSignalUid)
				uidList.extend(acc.oneSignalUid)
	if len(uidList)!=0:
		util_notify.sendMessageToOneSignalUsers(uidList,"New content published on Feedback Loop")
	return uidList

	