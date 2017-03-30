from google.appengine.ext import ndb
import logging
from datastore_channel import verify_channel_owner
from datetime import datetime, timedelta
import json
import datastore_account
import datastore_channel
import random

	
	
class Loop(ndb.Model):
	"""Appengine entity definition for surveys"""
	onChannel=ndb.IntegerProperty(indexed=True)
	loopItems=ndb.StringProperty(indexed=False)#1 json string on the form (generalized for more qustions and answers [{"question":"Question 1","answers":["Answer 1a","Answer 1b"]},{"question":"Question 2","answers":["Answer 2a","Answer 2b","Answer 2c"]}]
	replies=ndb.StringProperty(indexed=False, repeated=True)#1 json string per reply
	createdDate=ndb.DateTimeProperty(indexed=True, auto_now_add=True)#When was the loop created
	expiresOn=ndb.DateTimeProperty(indexed=True)#What is the deadline for answering

class LoopItem:
	"""Utility class to load certain properties of a survey from the stored json string"""
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

class ReplyShard(ndb.Model):
	"""
	Shards a loop reply to avoid congestion in cases of a lot of subscribers replying
	simultaneously
	"""
	replies=ndb.StringProperty(indexed=False,repeated=True)
	nrShards=ndb.IntegerProperty(indexed=False,repeated=False)#Store the number of shards in the first shard
	def __getAllReplyShards(self,loopId):
		stringLoop=str(loopId)
		replies=[]
		logging.info(self.nrShards)
		i=1
		while i<self.nrShards:
			shard=ReplyShard.get_by_id(stringLoop+"_"+str(i))
			if shard is not None:
				replies.extend(shard.replies)
			i+=1
		return replies
	def __putShard(self, loopId, replyString):
		index=random.randint(1, self.nrShards)
		shardStringId=str(loopId)+"_"+str(index)
		shard=ReplyShard.get_by_id(shardStringId)
		if(shard is None):
			shard=ReplyShard(id=shardStringId)
			shard.replies=[]
		shard.replies.append(replyString)
		shard.put()
	@staticmethod
	def getAllReplies(loopId):
		replyZeroIndex=str(loopId)+'_'+str(0)
		shardZero=ReplyShard.get_by_id(replyZeroIndex)
		return shardZero.__getAllReplyShards(loopId)
	@staticmethod
	@ndb.transactional(retries=10,xg=True)
	def putReply(loopId, replyString):
		replyZeroIndex=str(loopId)+'_'+str(0)
		shardZero=ReplyShard.get_by_id(replyZeroIndex)
		if(shardZero is None):
			raise ValueError('loop reply not initialized, zero indexed reply does not exist')
		shardZero.__putShard(loopId,replyString)
	@staticmethod
	@ndb.transactional(retries=10)
	def initShard(loopId, nrShard):
		"""
		Should be called when loop is created. Stores the number of shards
		in the 0-indexed shard
		"""
		replyZeroIndex=str(loopId)+'_'+str(0)
		shard=ReplyShard(id=(replyZeroIndex))
		shard.nrShards=nrShard
		shard.put()
		
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
	ReplyShard.initShard(key.id(),20) #creates index 0 of replyshards
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
	
def storeLoopReply(userId,replyString, replyObject):
	# logging.info(userId)
	# logging.info(replyString)
	# logging.info(replyObject)
	loopId=replyObject['loopId']
	# loop=Loop.get_by_id(long(loopId))
	# loop.replies.append(json.dumps(replyObject['replies']))
	# loop.put()
	ReplyShard.putReply(loopId,json.dumps(replyObject['replies']))
	datastore_account.setAnsweredLoop(userId,loopId)
def getRecentExpiredLoops(fromDaysBack=7, channelId="0"):
	recentLoops=Loop.query(Loop.onChannel==long(channelId), Loop.expiresOn>(datetime.now()-timedelta(days=fromDaysBack))).fetch(1000)
	logging.info("Answers:")
	return [(loop.key.id(),loop.expiresOn.date(), LoopItem(loop.loopItems).getMessage()) for loop in recentLoops];
def getResultJson(loopId):
	loop=Loop.get_by_id(long(loopId))
	repliesFromShards=ReplyShard.getAllReplies(loopId)
	return json.dumps([loop.loopItems,repliesFromShards])
def countQuestions(loopId):
	loop=Loop.get_by_id(long(loopId))
	return len(LoopItem(loop.loopItems).getItems());
	