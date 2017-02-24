from google.appengine.ext import ndb

class Account(ndb.Model):
	username = ndb.StringProperty(indexed=False)
	email = ndb.StringProperty(indexed=True)
	password = ndb.StringProperty(indexed=False)
	subscribed_to=ndb.StringProperty(repeated=True, indexed=False)
	owns_channels=ndb.KeyProperty(repeated=True, indexed=False)
	published_loops=ndb.KeyProperty(repeated=True, indexed=False)
	received_loops=ndb.KeyProperty(repeated=True, indexed=False)
		

def getUser(userEmail):
	q=Account.query(Account.email==userEmail)
	return q


def storeNewUser(newEmail, newPassword):
	account=Account(email=newEmail,password=newPassword, username=None) #create entity
	key=account.put ()  #store entity
	return key