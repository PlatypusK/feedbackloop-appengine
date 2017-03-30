import os
import unittest
import tempfile
import flask
import sys
import logging
from application import main
from application import actions
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed



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
	
		
	def test_redirect(self):
		rv = self.client.get('/')
		self.assertEqual(rv.status_code, 301)
	def test_login(self):
		rv=self.client.get('/login');
		self.assertEqual(rv.status_code, 200)
		wrongEmail="incorrect@email.com"
		badPassword="badPassword"
		rv1=self.login(wrongEmail, badPassword,False)
		self.assertEqual(rv1.status_code,200)
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
	
	def replyToSurvey(self):
		pass
		
	def test_show_survey(self):
		view_url='/show_survey'
		self.doUnverifiedGet(view_url)
		self.doGoodLogin()
	def test_forgot_password(self):
		view_url='/forgot_password'
	def test_about(self):
		view_url='/about'
	def test_channel_search_results(self):
		view_url='/channel_search_results'
		self.doUnverifiedGet(view_url)
		self.doGoodLogin()
	def test_subscribed_channels(self):
		view_url='/subscribed_channels'
		self.doUnverifiedGet(view_url)
		self.doGoodLogin()

	def test_owned_channel(self):
		view_url='/owned_channel'
		self.doUnverifiedGet(view_url)
		self.doGoodLogin()
	def show_loop_results(self):
		view_url='/loop_results'
		self.doUnverifiedGet(view_url)
		self.doGoodLogin()
	def test_user_main(self):
		self.doUnverifiedGet('/user_main')
		self.login(self.goodUser,self.goodPass,True)
		rv2=self.client.get('/user_main')
		self.assertEqual(rv2.status_code,200)
		assert '<h1 class="display-3">Welcome</h1>' in rv2.data
		assert '<p>See below for active loops</p>' in rv2.data
		assert 'Create new Channel' in rv2.data
		
	def login(self, email, password, follow_red):
		with self.getContext():
			return self.client.post('/login', data=dict(
				email=email,
				password=password,
				csrf_token=self.client.csrf_token
			), follow_redirects=follow_red)
	def logout(self):
		return self.client.get('/logout', follow_redirects=True)
	def doUnverifiedGet(self, url):
		rv1=self.client.get(url)
		self.assertEqual(rv1.status_code,302)#unauthorized, redirect to login
	def doGoodLogin(self):
		rv=self.login(self.goodUser,self.goodPass,False)
		self.assertEqual(rv.status_code,302)
if __name__ == '__main__':
	unittest.main()