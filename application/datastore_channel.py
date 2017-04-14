from google.appengine.ext import ndb
import datastore_account


class Channel(ndb.Model):
	"""Appengine entity for publishing channels"""
	owner=ndb.IntegerProperty(indexed=True) #id of the Account entity that owns this channel
	name=ndb.StringProperty(indexed=False)
	name_lower = ndb.ComputedProperty(lambda self: self.name.lower(), indexed=True)
	subscribers=ndb.IntegerProperty(repeated=True) #ids of the Accounts that subscribe to this channel
	description=ndb.StringProperty(indexed=False)

	
def writeChannel(userId, name, description):
	c=Channel(owner=long(userId),name=name,description=description)
	cKey=c.put()
	return cKey
def getChannel(id):
	c=Channel.get_by_id(id)
	return c
def get_owned_channel_identifiers(user_id):
	"""
	Returns a list of tuples in the form 
	(channelid,name,description) 
	for all channels owned by the user_id user"""
	query=Channel.query(Channel.owner==long(user_id))
	if query.count()>0:
		c_list=query.fetch(1000)#fetch at most 1000 channels
		parameter_list=[(x.key.id(),x.name,x.description) for x in c_list]
		return parameter_list
	else:
		return []
def verify_channel_owner(ownerid,channelid):
	"""
	Checks that the ownerid given is the actual owner of the channel. 
	Use this to test that the logged in user is the actual owner of the channel
	"""
	c=Channel.get_by_id(long(channelid))
	if c is not None:
		return c.owner==long(ownerid)
	else:
		return False
def get_owned_channel_data(ownerid,channelid):
	if not verify_channel_owner(ownerid,channelid):
		return None
	channel=Channel.get_by_id(long(channelid))
	return channel
def searchChannel(channelName):
	query=Channel.query(Channel.name_lower==channelName.lower())
	channels=query.fetch(1000)
	channelInfo=[]
	for x in channels:
		channelInfo.append((x.key.id(),x.name,x.description))
	return channelInfo
def subscribeChannel(userId,channelId):
	channel=Channel.get_by_id(long(channelId))
	if not long(userId) in channel.subscribers:#add only once
		channel.subscribers.append(long(userId))
		datastore_account.addChannelToSubscribed(userId,channelId)
		channel.put()
def getSubscribedChannelIdentifiers(user_id):
	"""Returns a list of tuples in the form (channelid,name,description) for all channels subsribed by the user_id user"""
	subChannels=datastore_account.getSubscribedChannels(user_id)
	identifiers=[]
	for channelId in subChannels:
		c=Channel.get_by_id(channelId)
		if c:
			identifiers.append((channelId, c.name,c.description))
	return identifiers
def notifyAllSubscribers(channelId):
	"""
	Takes in a channelId.
	Returns a list of OneSignalIds on the notification list for testing purposes
	"""
	channel=Channel.get_by_id(long(channelId))
	if channel:
		if channel.subscribers:
			return datastore_account.notifyAllSubscribers(channel.subscribers)
			
