import os
import unittest
import tempfile
import flask
import sys
import logging
import json
from datetime import timedelta
from time import sleep
from application import datastore_loop
from application import datastore_account
from application import datastore_channel
from application import main
from application import actions
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

SALTED_HASHED_PASSWORD='salted_hashed_password'
SALT='salt'
MOCK_ONE_SIGNAL_ID='mock one signal'
TEST_USER='testUser@user.user'
TEST_CHANNEL='Test channel'
TEST_DESCRIPTION='test description'

class FeedbackloopTestCase(unittest.TestCase):
	
	def getContext(self):
		return main.app.test_request_context('/')
	def showServerLog(self):
		logger = logging.getLogger()
		logger.level = logging.DEBUG
		stream_handler = logging.StreamHandler(sys.stdout)
		logger.addHandler(stream_handler)
	def setUp(self):
		# self.showServerLog();
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		self.client = main.app.test_client()
		ndb.get_context().clear_cache()
		self.goodUser='gooduser@user.com'
		self.goodPass='goodPass123'
		self.channelName='Test Channel'
		self.channelDescription='Test description'
		self.create_user(self.goodUser,self.goodPass)
	def tearDown(self):
		print 'tearDown'
		self.testbed.deactivate()
	def create_user(self, email, passw):
		with self.getContext():
			rv=self.client.get('/new_user')
			self.assertEqual(rv.status_code,200)
			data={'email':email,'password':passw}
			rv=self.client.post('/new_user', data,follow_redirects=True)
			assert(' <li>Passwords must match</li>') not in rv.data
			data={'email':email,'password':passw,'confirm':passw}
			rv=self.client.post('/new_user', data={
					"email":email,
					"password":passw, 
					"confirm":passw,
					"csrf_token":self.client.csrf_token
					},follow_redirects=False)
			assert(' <li>Passwords must match</li>') not in rv.data
			self.assertEqual(rv.status_code, 302)
			#Check that we are not redirected if we try to create an already existing user
			rv=self.client.post('/new_user', data={
					"email":email,
					"password":passw, 
					"confirm":passw,
					"csrf_token":self.client.csrf_token
					},follow_redirects=False)
			assert(' <li>Passwords must match</li>') not in rv.data
			self.assertEqual(rv.status_code, 200)
		
	def test_redirect(self):
		rv = self.client.get('/')
		self.assertEqual(rv.status_code, 301)
	def test_login(self):
		rv=self.client.get('/login');
		self.assertEqual(rv.status_code, 200)
		wrongEmail="incorrect@email.com"
		badPassword="badPassword"
		rv1=self.login(wrongEmail, badPassword,False)
		self.assertEqual(rv1.status_code,200) #check that we are not redirected away from login
		rv2=self.login(self.goodUser,badPassword,False)
		self.assertEqual(rv2.status_code,200) #check that we are not redirected away from login
		self.doGoodLogin()
	def test_new_channel(self):
		view_url='/new_channel'
		self.doUnverifiedGet(view_url)
		self.new_channel()
	def new_channel(self):
		self.doGoodLogin()
		rv1=self.client.get('/new_channel')
		self.assertEqual(rv1.status_code,200)
		logging.info('6543')
		with self.getContext():
			rv2=self.client.post('/new_channel', data={"channelname":self.channelName,
			"description":self.channelDescription,
			"csrf_token":self.client.csrf_token}, follow_redirects=False)
			self.assertEqual(rv2.status_code, 302)
			assert 'You should be redirected automatically to target URL: <a href="/view_owned_channels">' in rv2.data
	def test_view_owned_channels(self):
		view_url='/view_owned_channels'
		self.doUnverifiedGet(view_url)
		self.doGoodLogin()
		rv1=self.client.get(view_url)
		self.new_channel()
		rv2=self.client.get(view_url)
		self.assertEqual(rv1.status_code,200)
		self.assertEqual(rv1.status_code,200)
		assert '<div class="col-md-4">' in rv2.data
		assert '<h2>Test Channel</h2>' in rv2.data
		assert '<p>Test description</p>' in rv2.data
		assert '<p><button type="submit" formmethod="post" class="btn btn-secondary" value=2' in rv2.data
		with self.getContext():
			rv3=self.client.post('/view_owned_channels', data={
			"channelid":'2',#correct channelid
			"csrf_token":self.client.csrf_token
			},follow_redirects=False)
			self.assertEqual(rv3.status_code,307)
			rv4=self.client.post('/view_owned_channels',data={
			"channelid":'3',#incorrect channelid
			"csrf_token":self.client.csrf_token
			},follow_redirects=False)
			self.assertEqual(rv4.status_code,401)
		
	def test_create_loop(self):
		view_url='/create_loop'
		self.doUnverifiedGet(view_url)
		self.new_channel()
		rv1=self.client.get(view_url)
		self.assertEqual(rv1.status_code,400)#
		with self.getContext():
			rv2=self.client.post(view_url, data={
			"action":'publish',
			"channel_id":'2',
			"jsonString":'[{"message":"M"},[{"question":"Q1","answers":["A1","A2","A3","A4"]},{"question":"Q2","answers":["A1","A2","A3"]}]]',
			"csrf_token":self.client.csrf_token}, follow_redirects=False)
			self.assertEqual(rv2.status_code, 302)
			assert '<p>You should be redirected automatically to target URL: <a href="/view_owned_channels">/view_owned_channels</a>' in rv2.data
		loops=datastore_loop.getActiveLoops([(2,self.channelName, self.channelDescription)])
		print loops
		assert """[(2, 'Test Channel', 'Test description', 3L, u'[{"message":"M"},[{"question":"Q1","answers":["A1","A2","A3","A4"]},{"question":"Q2","answers":["A1","A2","A3"]}]]', u'M')]""" in str(loops)
	
		
	def test_show_survey(self):
		view_url='/show_survey'
		self.doUnverifiedGet(view_url)
		self.test_create_loop()
		with self.getContext():
			data={
			"action":actions.ACTION_SHOW_SURVEY,
			"csrf_token":self.client.csrf_token,
			"payLoad":"""[2,"Testing Channel","Channel for unittest",3,"[{\\"message\\":\\"M\\"},[{\\"question\\":\\"Q1\\",\\"answers\\":[\\"A1\\",\\"A2\\",\\"A3\\",\\"A4\\"]},{\\"question\\":\\"Q2\\",\\"answers\\":[\\"A1\\",\\"A2\\",\\"A3\\"]}]]"]"""}
			rv1=self.client.post(view_url, data=data,follow_redirects=False)
			self.assertEqual(rv1.status_code,200)
			data['action']=actions.ACTION_SUBMIT_REPLY
			rv2=self.client.post(view_url, data=data,follow_redirects=False)
			self.assertEqual( rv2.status_code,400) #bad payload
			assert """<p>The browser (or proxy) sent a request that this server could not understand.</p>""" in rv2.data
			data['payLoad']=''
			rv3=self.client.post(view_url, data=data,follow_redirects=False)
			self.assertEqual( rv3.status_code,400) #no payload
			assert """<p>The browser (or proxy) sent a request that this server could not understand.</p>""" in rv3.data
			data['payLoad']='{"channelId":5883589799444480,"channelName":"Testing Channel","channelDescription":"Channel for unittest","loopId":5307720584396800,"message":"M","questions":["Q1","Q2"],"answers":[["A1","A2","A3","A4"],["A1","A2","A3"]],"replies":[[true,false,false,false],[false,true,false]]}'
			rv4=self.client.post(view_url, data=data,follow_redirects=False)
			self.assertEqual( rv4.status_code,400) #nonexisting loopid
			assert """<p>The browser (or proxy) sent a request that this server could not understand.</p>""" in rv4.data
			data['payLoad']='{"channelId":2,"channelName":"Testing Channel","channelDescription":"Channel for unittest","loopId":3,"message":"M","questions":["Q1","Q2"],"answers":[["A1","A2","A3","A4"],["A1","A2","A3"]],"replies":[[true,false,false,false],[false,true,false]]}'
			rv5=self.client.post(view_url, data=data,follow_redirects=False)
			self.assertEqual( rv5.status_code,302) #sucessfully replied. redirect to /user_main
			assert """<p>You should be redirected automatically to target URL: <a href="/user_main">/user_main</a>""" in rv5.data
	def test_forgot_password(self):
		view_url='/forgot_password'
		rv1=self.client.get(view_url)
		self.assertEqual(rv1.status_code,200) #login should not be required
		assert """<form method='POST' action="/forgot_password">""" in rv1.data
	def test_about(self):
		view_url='/about'
		rv1=self.client.get(view_url)
		self.assertEqual(rv1.status_code,200) #login should not be required
		assert """Information about this Application""" in rv1.data
	def test_channel_search_results(self):
		view_url='/channel_search_results'
		self.doUnverifiedGet(view_url)
		self.new_channel()
		with self.getContext():
			data={
			'action':actions.ACTION_SEARCH,
			'csrf_token':self.client.csrf_token}
			rv1=self.client.post(view_url, data=data,follow_redirects=False)
			self.assertEqual(rv1.status_code,400) #no payLoad parameter
			assert """<p>The browser (or proxy) sent a request that this server could not understand.</p>""" in rv1.data
			data['payLoad']='Testing Channel'
			rv2=self.client.post(view_url, data=data,follow_redirects=False)
			self.assertEqual(rv2.status_code,200)
			assert """Testing Channel""" in rv2.data
			data['action']=actions.ACTION_SUBSCRIBE
			data['payLoad']=2
			rv3=self.client.post(view_url, data=data,follow_redirects=False)
			self.assertEqual(rv3.status_code,302)
			assert """<p>You should be redirected automatically to target URL: <a href="/user_main">/user_main</a>""" in rv3.data
	def test_subscribed_channels(self):
		view_url='/subscribed_channels'
		self.doUnverifiedGet(view_url)
		self.test_channel_search_results()
		with self.getContext():
			rv1=self.client.get(view_url)
			self.assertEqual(rv1.status_code,200)#should GET all subscribed channels
			assert """<p><button type="button" class="btn btn-secondary" value=2  name="channelid""" in rv1.data
			data={'action':actions.ACTION_SEARCH,
			'csrf_token':self.client.csrf_token}
			rv2=self.client.post(view_url,data=data,follow_redirects=False)
			self.assertEqual(rv2.status_code, 307)
	def test_owned_channel(self):
		view_url='/owned_channel'
		self.doUnverifiedGet(view_url)
		self.test_new_channel()
		with self.getContext():
			data={'channelid': 2,'csrf_token':self.client.csrf_token}
			rv1=self.client.post(view_url, data=data, follow_redirects=False)
			self.assertEqual(rv1. status_code,200)
			assert """input id="channel_id_for_new_loop" name="channel_id_for_new_loop" type="hidden" value="2""" in rv1.data
			data['channel_id_for_new_loop']=2
			data['action']=actions.ACTION_CREATE_LOOP
			rv2=self.client.post(view_url,data=data, follow_redirects=False)
			self.assertEqual(rv2.status_code,307)
			assert '/create_loop' in rv2.data
			data['action']=actions.ACTION_VIEW_LOOP_RESULTS
			data['payLoad']=3
			rv3=self.client.post(view_url,data=data,follow_redirects=False)
			self.assertEqual(rv3.status_code,307)
			assert '/show_loop_results' in rv3.data
			
	def test_show_loop_results(self):
		view_url='/show_loop_results'
		self.doUnverifiedGet(view_url)
		self.test_create_loop()
		with self.getContext():
			data={
			'action':actions.ACTION_VIEW_LOOP_RESULTS,
			'csrf_token':self.client.csrf_token}
			rv1=self.client.post(view_url,data=data,follow_redirects=False)
			self.assertEqual(rv1.status_code, 400)#missing payLoad
			data['payLoad']=3 #give loopId of the loop you want to look at
			rv2=self.client.post(view_url,data=data,follow_redirects=False)
			self.assertEqual(rv2.status_code,200)
			assert """See results for your survey below""" in rv2.data
			assert """<div class="col-md-6">""" in rv2.data
	def test_log_off(self):
		view_url='/user_main'
		self.doUnverifiedGet(view_url)
		self.doGoodLogin()
		rv2=self.client.get(view_url) #test that we can access a protected view 
		self.assertEqual(rv2.status_code,200)
		assert '<h1 class="display-3">Welcome</h1>' in rv2.data
		assert 'Create new Channel' in rv2.data
		self.logout()
		rv2=self.client.get(view_url) #test that we can not access a protected view 
		self.assertEqual(rv2.status_code,302) 
		assert '/login' in rv2.data #check that we are redirected to /login
	def test_user_main(self):
		self.doUnverifiedGet('/user_main')
		self.doGoodLogin()
		rv2=self.client.get('/user_main')
		self.assertEqual(rv2.status_code,200)
		assert '<h1 class="display-3">Welcome</h1>' in rv2.data
		assert 'Create new Channel' in rv2.data
	def test_save_one_signal(self):
		view_url='/save_one_signal'
		self.doGoodLogin()
		with self.getContext():
			data={
			'action':actions.ACTION_SAVE_ONE_SIGNAL,
			'payLoad':'dummy_uid',
			'csrf_token':self.client.csrf_token}
			rv1 = self.client.post(view_url, data=data,follow_redirects=False)
			self.assertEqual(rv1.status_code, 200)
			#Test that we get a 400 error if we use the wrong action
			data['action']=''
			rv2 = self.client.post(view_url, data=data,follow_redirects=False)
			self.assertEqual(rv2.status_code, 400)
	def login(self, email, password, follow_red):
		with self.getContext():
			return self.client.post('/login', data=dict(
				email=email,
				password=password,
				csrf_token=self.client.csrf_token
			), follow_redirects=follow_red)
	def logout(self):
		return self.client.get('/log_out', follow_redirects=True)
	def doUnverifiedGet(self, url):
		rv1=self.client.get(url)
		self.assertEqual(rv1.status_code,302)#unauthorized, redirect to login
	def doGoodLogin(self):
		rv=self.login(self.goodUser,self.goodPass,False)
		self.assertEqual(rv.status_code,302)
	def storeNewUser(self):
		response=datastore_account.storeNewUser((TEST_USER, SALT,SALTED_HASHED_PASSWORD))
		self.assertEqual(response,True)
		query=datastore_account.Account.query()
		accounts=query.fetch(5)
		acc=accounts[1]
		self.assertEqual(acc.email,TEST_USER)
		self.assertEqual(acc.salt,SALT)
		self.assertEqual(acc.salted_password,SALTED_HASHED_PASSWORD)
		return acc
	def setGetOneSignalId(self, account):
		accKey=datastore_account.setOneSignalId(account.key.id(),MOCK_ONE_SIGNAL_ID)
		self.assertEqual(datastore_account.getOneSignalId(account.key.id()),[MOCK_ONE_SIGNAL_ID])
	def getUserVerDataByEmail(self,account):
		dat=datastore_account.get_user_verification_data_by_email(TEST_USER)
		self.assertEqual((account.key.id(),SALT,SALTED_HASHED_PASSWORD),dat)
	def getUserVerDataById(self,account):
		dat=datastore_account.get_user_verification_data_by_id(account.key.id())
		self.assertEquals((acc.key.id(),SALT,SALTED_HASHED_PASSWORD),dat)
	def getSetSubscribeAccount(self,account):
		assert datastore_account.addChannelToSubscribed('45','0')==False
		assert datastore_account.addChannelToSubscribed(account.key.id(),5)==True
		assert datastore_account.Account.get_by_id(account.key.id()).subscribed_to==[5]
		assert datastore_account.getSubscribedChannels(account.key.id())==[5]
	def setRemoveAnsweredLoop(self, account):
		da=datastore_account
		da.setAnsweredLoop(account.key.id(),5)
		assert 5 in da.Account.get_by_id(account.key.id()).answeredLoops
		l=da.removeAnsweredLoops(account.key.id(),[('','','',1,''),('','','',2,''),('','','',5,'')])
		assert l==[('','','',1,''),('','','',2,'')]
	def notifyAllSubscribedDevices(self,account):
		da=datastore_account
		a=da.notifyAllSubscribers(['d','b','c',account.key.id(),'f','e'])
		assert 'mock one signal' in a
	def emailToId(self,account):
		da=datastore_account
		# print da.emailToId(TEST_USER)
	def test_datastore_account(self):
		acc=self.storeNewUser()
		self.setGetOneSignalId(acc)
		acc=datastore_account.Account.get_by_id(acc.key.id())
		self.getUserVerDataByEmail(acc)
		self.getUserVerDataByEmail(acc)
		self.getSetSubscribeAccount(acc)
		self.setRemoveAnsweredLoop(acc)
		self.notifyAllSubscribedDevices(acc)
		self.emailToId(acc)
	def writeGetChannel(self, userId):
		dc=datastore_channel
		cKey=dc.writeChannel(userId,TEST_CHANNEL, TEST_DESCRIPTION)
		assert cKey is not None
		channel=dc.getChannel(cKey.id())
		assert channel.owner==userId
		assert channel.name==TEST_CHANNEL
		assert channel.description==TEST_DESCRIPTION
		cTup=dc.get_owned_channel_identifiers(userId)
		assert cTup==[(cKey.id(),channel.name,channel.description)]
		return cKey.id()
	def verifyChannelOwner(self, userId,channelId):
		dc=datastore_channel
		isOwner=dc.verify_channel_owner(userId,channelId)
		assert isOwner==True #is the owner of the channel
		isOwner=dc.verify_channel_owner(100,channelId)
		assert isOwner==False #not the owner
		isOwner=dc.verify_channel_owner(userId,100)
		assert isOwner==False #no such channel
	def getOwnedChannelData(self,userId,channelId):
		dc=datastore_channel
		c=dc.get_owned_channel_data(userId,channelId)
		assert c is not None
		assert c.owner==userId
	def searchChannel(self, cId):
		dc=datastore_channel
		cInfo=dc.searchChannel(TEST_CHANNEL)
		assert (cId, TEST_CHANNEL,TEST_DESCRIPTION) in cInfo
		cInfo=dc.searchChannel(TEST_CHANNEL.upper())
		assert (cId, TEST_CHANNEL,TEST_DESCRIPTION) in cInfo
		cInfo=dc.searchChannel('channel that does not exist')
		assert cInfo==[]
	def subscribeChannel(self,userId,cId):
		dc=datastore_channel
		da=datastore_account
		dc.subscribeChannel(userId,cId)
		assert [(cId,TEST_CHANNEL,TEST_DESCRIPTION)] == dc.getSubscribedChannelIdentifiers(userId)
		da.addChannelToSubscribed(userId,999) #add nonexistent channel
		#test that nonexistent channel is not in the list of return tuples
		assert [(cId,TEST_CHANNEL,TEST_DESCRIPTION)]== dc.getSubscribedChannelIdentifiers(userId)
	def notifySubscribersForChannel(self,userId,cId):
		dc=datastore_channel
		da=datastore_account
		datastore_account.setOneSignalId(userId,MOCK_ONE_SIGNAL_ID)
		assert MOCK_ONE_SIGNAL_ID in dc.notifyAllSubscribers(cId)
		
	def test_datastore_channel(self):	
		acc=self.storeNewUser()
		userId=acc.key.id()
		cId=self.writeGetChannel(userId)
		self.verifyChannelOwner(userId, cId)
		self.getOwnedChannelData(userId,cId)
		self.searchChannel(cId)
		self.subscribeChannel(userId,cId)
		self.notifySubscribersForChannel(userId,cId)
	def writeGetLoop(self,uid,cid):
		dl=datastore_loop
		jsonString="""[{"message":"M"},[{"question":"Q1","answers":["A1A","A2A","A3A"]},{"question":"Q2","answers":["A1B","A2B","A3B"]}]]"""
		lKey=dl.publish_loop(uid,cid,jsonString)
		lKeyBadUid=dl.publish_loop(66,cid,jsonString)
		assert not lKeyBadUid
		assert lKey
		assert dl.Loop.get_by_id(lKey.id())
		assert dl.ReplyShard.get_by_id(str(lKey.id())+'_0')
		return lKey.id()
	def verifyActiveLoops(self,cid):
		dl=datastore_loop
		l=[(cid,TEST_CHANNEL,TEST_DESCRIPTION)]
		l2=dl.getActiveLoops(l)
		assert l2==[(3L, 'Test channel', 'test description', 4L, u'[{"message":"M"},[{"question":"Q1","answers":["A1A","A2A","A3A"]},{"question":"Q2","answers":["A1B","A2B","A3B"]}]]', u'M')]
		
	def verifyStoreGetReply(self,uid):
		dl=datastore_loop
		da=datastore_account
		replyString='[[false, false, true], [true, false,false]]'
		replyObject={'loopId':4,'replies':'[[false, false, true], [true, false,false]]'}
		stored=dl.storeLoopReply(uid,replyString,replyObject)
		assert stored
		assert 4 in da.Account.get_by_id(uid).answeredLoops
		results=dl.getResultJson(4)
		assert "[{\"message\":\"M\"},[{\"question\":\"Q1\",\"answers\":[\"A1A\",\"A2A\",\"A3A\"]},{\"question\":\"Q2\",\"answers\":[\"A1B\",\"A2B\",\"A3B\"]}]]", ["\"[[false, false, true], [true, false,false]]\""] in results
	def verifyCountQuestions(self,lid):
		dl=datastore_loop
		nr=dl.countQuestions(lid)
		assert nr==2
	def verifyRecentLoops(self,cid,lid):
		dl=datastore_loop
		survey=dl.Loop.get_by_id(lid)
		recent=dl.getRecentLoops(channelId=cid)
		assert recent
		assert recent[0][0]==survey.key.id()
	def verifyLoopItem(self,lid):
		dl=datastore_loop
		survey=dl.Loop.get_by_id(lid)
		
		li=dl.LoopItem(survey.loopItems)
		m=li.getMessage()
		assert m=='M'
		items=li.getItems()
		assert {u'question': u'Q1', u'answers': [u'A1A', u'A2A', u'A3A']}, {u'question': u'Q2', u'answers': [u'A1B', u'A2B', u'A3B']} in items
	def verifyReplyShard(self):
		"""
		Tests only public methods, not class private methods
		As is common for unittesting. The private methods will be tested indirectly as they are used by the tested functions.
		"""
		dl=datastore_loop
		dl.ReplyShard.initShard(99,20)
		initShard=dl.ReplyShard.get_by_id(str(99)+'_'+str(0))
		assert initShard
		for x in range(0,50):
			dl.ReplyShard.putReply(99,'replyString')
		allReplies=dl.ReplyShard.getAllReplies(99)
		assert 'replyString' in allReplies
		assert len(allReplies)==50
	
	def test_datastore_loop(self):
		acc=self.storeNewUser()
		uid=acc.key.id()
		cId=self.writeGetChannel(uid)
		lId=self.writeGetLoop(uid,cId)
		self.verifyActiveLoops(cId)
		self.verifyStoreGetReply(uid)
		self.verifyCountQuestions(lId)
		self.verifyRecentLoops(cId,lId)
		self.verifyLoopItem(lId)
		self.verifyReplyShard()
		
		
		
if __name__ == '__main__':
	unittest.main()