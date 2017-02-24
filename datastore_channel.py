from google.appengine.ext import ndb

class Channel(ndb.Model):
	owner=ndb.IntegerProperty(indexed=True) #id of the Account entity that owns this channel
	name=ndb.StringProperty(indexed=True) 
	subscribers=ndb.IntegerProperty(repeated=True) #ids of the Accounts that subscribe to this channel
	description=ndb.StringProperty(indexed=False)
	active_loops=ndb.KeyProperty(indexed=False, repeated=True) #Keeps track of currently active loops
	old_loops=ndb.KeyProperty(indexed=False, repeated=True)
	
