import os
import unittest
import tempfile
from application import main
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

class FeedbackloopTestCase(unittest.TestCase):

	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		self.app = main.app.test_client()
		ndb.get_context().clear_cache()
	def tearDown(self):
		self.testbed.deactivate()
	def test_redirect(self):
		rv = self.app.get('/')
		print rv

if __name__ == '__main__':
	unittest.main()