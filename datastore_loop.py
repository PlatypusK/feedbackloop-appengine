from google.appengine.ext import ndb
import logging
from datastore_channel import verify_channel_owner
from datetime import datetime, timedelta
import json

	
	
class Loop(ndb.Model):
	onChannel=ndb.IntegerProperty(indexed=True)
	loopItems=ndb.StringProperty(indexed=False)#1 json string on the form (generalized for more qustions and answers [{"question":"Question 1","answers":["Answer 1a","Answer 1b"]},{"question":"Question 2","answers":["Answer 2a","Answer 2b","Answer 2c"]}]
	replies=ndb.StringProperty(indexed=False, repeated=True)#1 json string per reply
	createdDate=ndb.DateTimeProperty(indexed=False, auto_now_add=True)#When was the loop created
	expiresOn=ndb.DateTimeProperty(indexed=False)#What is the deadline for answering

	
def publish_loop(user_id, channel_id, jsonString):
	logging.info(user_id)
	logging.info(channel_id)
	logging.info(jsonString)
	logging.info(json.loads(jsonString))
	if not verify_channel_owner(user_id,channel_id):
		return False
	newLoop = Loop(onChannel=long(channel_id),loopItems=jsonString,\
		expiresOn=datetime.now()+timedelta(hours=24))
	return True