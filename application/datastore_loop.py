from google.appengine.ext import ndb
import logging
from datastore_channel import verify_channel_owner
from datetime import datetime, timedelta
import json
import datastore_account
import datastore_channel

	
	
class Loop(ndb.Model):
	"""
	Note that I have chosen to use static functions instead of class member functions to keep transactions less complex
	i.e functional paradigm. If I had used class methods instead, the instances would be mutable for far longer. This means
	that transactions would take longer and concurrency might suffer. I have also avoided the usage of datastore classes outside of the
	modules they are defined. This should reduce the risk of transaction difficulties.
	"""
	onChannel=ndb.IntegerProperty(indexed=True)
	loopItems=ndb.StringProperty(indexed=False)#1 json string on the form (generalized for more qustions and answers [{"question":"Question 1","answers":["Answer 1a","Answer 1b"]},{"question":"Question 2","answers":["Answer 2a","Answer 2b","Answer 2c"]}]
	replies=ndb.StringProperty(indexed=False, repeated=True)#1 json string per reply
	createdDate=ndb.DateTimeProperty(indexed=True, auto_now_add=True)#When was the loop created
	expiresOn=ndb.DateTimeProperty(indexed=True)#What is the deadline for answering

class LoopItem:
	def __init__(self, jsonString):
		self.loaded=json.loads(jsonString)
		self.messagePos=0
		self.questionPos=1
		self.questionPos2=0;
	def getMessage(self):
		return self.loaded[self.messagePos].get('message')
	def getItems(self):
		items=self.loaded[self.questionPos]
		return items

		

def publish_loop(user_id, channel_id, jsonString):
	logging.info(user_id)
	logging.info(channel_id)
	logging.info(jsonString)
	logging.info(json.loads(jsonString))
	if not verify_channel_owner(user_id,channel_id):
		return False
	newLoop = Loop(onChannel=long(channel_id),loopItems=jsonString,\
		expiresOn=datetime.now()+timedelta(hours=24))
	key=newLoop.put()
	if(key):
		logging.info('published')
		datastore_channel.notifyAllSubscribers(channel_id)
	return key
def getActiveLoops(channels):
	"""Expects a list of tuples of channelId, name, description), returns a list of tuples of (channelId,channelName, channelDescription, activeLoopId, loopItems)"""
	loops=[]
	for channel in channels:
		logging.info(channel[0])
		query=Loop.query(Loop.onChannel==channel[0],Loop.expiresOn>datetime.now())
		activeLoopsOnChannel=query.fetch(100)
		logging.info(activeLoopsOnChannel)
		for loop in activeLoopsOnChannel:
			loops.append((channel[0],channel[1],channel[2],loop.key.id(),loop.loopItems))
	return loops
	
@ndb.transactional(retries=10,xg=True)
def storeLoopReply(userId,replyString, replyObject):
	logging.info(userId)
	logging.info(replyString)
	logging.info(replyObject)
	loopId=replyObject['loopId']
	loop=Loop.get_by_id(long(loopId))
	loop.replies.append(json.dumps(replyObject['replies']))
	loop.put()
	datastore_account.setAnsweredLoop(userId,loopId)
def getRecentExpiredLoops(fromDaysBack, channelId):
	recentLoops=Loop.query(Loop.onChannel==long(channelId), Loop.expiresOn>(datetime.now()-timedelta(days=fromDaysBack))).fetch(1000)
	logging.info("Answers:")
	return [(loop.key.id(),loop.expiresOn.date(), LoopItem(loop.loopItems).getMessage()) for loop in recentLoops];
def getResultJson(loopId):
	loop=Loop.get_by_id(long(loopId))
	return json.dumps([loop.loopItems,loop.replies])
def countQuestions(loopId):
	loop=Loop.get_by_id(long(loopId))
	return len(LoopItem(loop.loopItems).getItems());
	