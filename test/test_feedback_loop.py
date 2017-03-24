import os
import unittest
import tempfile
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

class FeedbackloopTestCase(unittest.TestCase):

    def setUp(self):
        flaskr.app.config['TESTING'] = True
        self.app = main.app.test_client()
	def test_redirect(self):
		rv = self.app.get('/')


if __name__ == '__main__':
    unittest.main()