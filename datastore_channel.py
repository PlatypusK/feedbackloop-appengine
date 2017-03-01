from google.appengine.ext import ndb
from datastore_account import isOwnerOfChannel


class Channel(ndb.Model):
	owner=ndb.IntegerProperty(indexed=True) #id of the Account entity that owns this channel
	name=ndb.StringProperty(indexed=True) 
	subscribers=ndb.IntegerProperty(repeated=True) #ids of the Accounts that subscribe to this channel
	description=ndb.StringProperty(indexed=False)
	active_loops=ndb.KeyProperty(indexed=False, repeated=True) #Keeps track of currently active loops
	old_loops=ndb.KeyProperty(indexed=False, repeated=True)
	
def getChannel(id):
	c=Channel.get_by_id(id)
	if isOwnerOfChannel(c):
		return c
	return None
def get_owned_channel_identifiers(user_id):
	"""Returns a list of tuples in the form (channelid,name,description)"""
	query=Channel.query(Channel.owner==long(user_id))
	if query.count()>0:
		c_list=query.fetch(1000)#fetch at most 1000 channels
		parameter_list=[(x.key.id(),x.name,x.description) for x in c_list]
		return parameter_list
	else:
		return []
def verify_channel_owner(ownerid,channelid):
	"""Checks that the ownerid given is the actual owner of the channel. 
	Use this to test that the logged in user is the actual owner of the channel"""
	return Channel.get_by_id(long(channelid)).owner==long(ownerid)
	