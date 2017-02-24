from google.appengine.ext import ndb


class LoopQuestion(ndb.model):
	question=ndb.StringProperty(indexed=False)
	possibleAnswers=ndb.IntegerProperty(indexed=False, repeated=True)
	
class LoopReply(ndb.model):
	replyFrom=ndb.KeyProperty(Account, indexed=False)
	replies=ndb.IntegerProperty(indexed=False, repeated=True)
class Loop(ndb.model):
	onChannel=ndb.KeyProperty(indexed=True)
	questions=ndb.StringProperty(indexed=False, repeated=True)
	questions=ndb.StructuredProperty(LoopQuestion,indexed=False,repeated=True)
	replies=ndb.StructuredProperty(LoopReply, repeated=True)
