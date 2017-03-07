import logging

from flask import Flask, request, redirect, url_for,current_app, session
from flask_httpauth import HTTPBasicAuth
import json
import os
from flask_wtf import Form
from forms import LoginForm, NewChannelForm, RegistrationForm
from flask_wtf.csrf import CSRFProtect
from datastore_channel import Channel, getChannel
from hashlib import algorithms_available


app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or \
    'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'
app.debug=True

csrf = CSRFProtect(app)
csrf.init_app(app)
application_title='Feedback Loop'

import views
import verification

@app.before_request
def log_request_info():
	logging.info('Headers: %s', request.headers)
	logging.info('Body: %s', request.get_data())
	logging.info('------ {0}'.format(request.form))


