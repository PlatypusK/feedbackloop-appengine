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
	
	def getContext(self,url):
		return main.app.test_request_context(url)
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
		with self.getContext('/new_user'):
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
	def test_login_get(self):
		rv=self.client.get('/login');
		self.assertEqual(rv.status_code, 200)
			
	def test_login_post(self):
		wrongEmail="incorrect@email.com"
		badPassword="badPassword"
		rv1=self.login(wrongEmail, badPassword,False)
		self.assertEqual(rv1.status_code,200)
		self.doGoodLogin()
	def test_create_channel(self):
		self.doUnverifiedGet('new_channel')
		self.login(self.goodUser, self.goodPass, True)
		rv1=self.client.get('/new_channel')
		self.assertEqual(rv1.status_code,200)
		logging.info('6543')
		with self.getContext('/'):
			rv2=self.client.post('/new_channel', data={"channelname":self.channelName,
			"description":self.channelDescription,
			"csrf_token":self.client.csrf_token}, follow_redirects=False)
			self.assertEqual(rv2.status_code, 302)
	def test_owned_channels(self):
		view_url='view_owned_channels'
		self.doUnverifiedGet(view_url)
		self.doGoodLogin()
	def test_submit_reply(self):
		view_url='show_survey'
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
		with self.getContext('/login'):
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