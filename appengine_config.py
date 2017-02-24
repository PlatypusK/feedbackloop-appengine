# appengine_config.py
from google.appengine.ext import vendor
import os
import sys

# Add any libraries install in the "lib" folder.
vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))

on_appengine = os.environ.get('SERVER_SOFTWARE','').startswith('Development')
if on_appengine and os.name == 'nt':
  sys.platform = "Not Windows"

