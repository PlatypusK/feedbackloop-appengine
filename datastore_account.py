from google.appengine.ext import ndb

class Account(ndb.Model):
	username = ndb.StringProperty(indexed=False)
	email = ndb.StringProperty(indexed=True)
	salt = ndb.StringProperty(indexed=False)
	salted_password = ndb.StringProperty(indexed=False)
	subscribed_to=ndb.StringProperty(repeated=True, indexed=False)
	owns_channels=ndb.KeyProperty(repeated=True, indexed=False)
	published_loops=ndb.KeyProperty(repeated=True, indexed=False)
	received_loops=ndb.KeyProperty(repeated=True, indexed=False)
    
		


"""Returns True if new user was successfully created, False otherwise, expects a tuple with email, salt and a salted hashed password in that order"""
def storeNewUser(verification_data):
	account=Account(email=verification_data[0],salt=verification_data[1], salted_password=verification_data[2]) #create entity
	key=account.put ()  #store entity
	if key:
		return True
	else:
		return False

def isOwnerOfChannel(channelId):
	return True

"""Returns a tuple containing the users id, salted and hashed password and the randomly generated salt if the user exists and is unique, otherwise returns false"""
def get_user_verification_data_by_email(email):
	query=Account.query(Account.email==email)
	user=query.get()
	if user==None:
		return False
	if query.count() == 1:
		return (user.key.id(),user.salt, user.salted_password)
	return False
def get_user_verification_data_by_id(user_id):
	user=Account.get_by_id(long(user_id))
	if user==None:
		return False
	return (user.key.id(),user.salt, user.salted_password)

    