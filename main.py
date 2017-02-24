import logging

from flask import Flask, render_template,request, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from datastore_account import Account, getUser, storeNewUser
from verification import isUser, isPasswordCorrect, isNewUserValid, isNewPasswordValid,isUniqueUser
import json
from flask import redirect, render_template, url_for
from flask import session
import os
from flask import request, current_app
from flask_wtf import Form
from forms import LoginForm, NewChannelForm, RegistrationForm
from flask_wtf.csrf import CSRFProtect
from datastore_channel import Channel








app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or \
    'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'
app.debug=True
auth=HTTPBasicAuth()
csrf = CSRFProtect(app)
csrf.init_app(app)

@auth.verify_password
def verify_password(email, password):
	logging.info(session.get('email'))
	logging.info(session.get('password'))
	if('email' in session):
		user=getUser(session.get('email'))
		if isUser(user):
			if isPasswordCorrect(user, session.get('password')):
				return True
		else:
			return False
	logging.info("here")
	logging.info(request.get_data())
	logging.info (request.form['email'])
	logging.info (request.form['password'])

	
@app.before_request
def log_request_info():
	logging.info('Headers: %s', request.headers)
	logging.info('Body: %s', request.get_data())
	logging.info('------ {0}'.format(request.form))

   

@app.route('/')
def hello():
    return redirect(url_for('login'))
	
@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm() if request.method == 'POST' else LoginForm(request.args)
	if form.validate_on_submit():
		user=getUser(request.form['email'])
		if isUser(user):
			if isPasswordCorrect(user, request.form['password']):
				session['email']=request.form['email']
				session['password']=request.form['password']
				logging.info('+-+-+-+-+-+'+str(user.get().key.id()))
				session['userId']=str(user.get().key.id())
				return redirect(url_for('user_main'))
		return render_template('login_page.html', form=form)
		logging.info("validate password here")
		logging.info(form.password.data)
	logging.info(form.errors.items())
	return render_template('login_page.html', form=form)
	
@app.route('/new_user', methods=['GET','POST'])
def new_user():
	form = RegistrationForm() if request.method == 'POST' else RegistrationForm(request.args)
	if form.validate_on_submit():
		logging.info('+/+/+/+/+')
		if isUniqueUser(form.email.data):
			key=storeNewUser(form.email.data, form.password.data)
			if key:
				return redirect(url_for('login',code=302))
			return redirect(url_for('new_user',code=307))
	return render_template('new_user.html', form=form)
	
@app.route('/forgot_password')
def forgot_password():
	return render_template('forgot_password.html')

@app.route('/create_loop', methods=['GET','POST'])
@auth.login_required
def create_loop():
	logging.info('*+*+*+*+*+*')
	return render_template('create_loop.html', channel_name="name of channel")	
	
@app.route('/owned_channel', methods=['GET','POST'])
@auth.login_required
def owned_channel():
	logging.info('++++++++')
	return render_template('owned_channel.html', channel_name="name of channel")
	


@app.route('/new_channel', methods=['GET','POST'])
@auth.login_required
def new_channel():
	form = NewChannelForm() if request.method == 'POST' else NewChannelForm(request.args)
	if form.validate_on_submit():
		logging.info('validated------new_channel-------'+
			request.form['channelname']+'-------'+request.form['description'])
		logging.info(session.get('userId'))
		c=Channel(owner=int(session.get('userId')),name=request.form['channelname'],description=request.form['description'])
		id=c.put().id()
		
		return redirect(url_for('owned_channel'))
		
	logging.info(form.errors.items())
	return render_template('create_channel.html', form=form)

	
@app.route('/user_main', methods=['GET','POST'])
@auth.login_required
def user_main():
	# email=request.form['email']
	# password=request.form['password']
	#Populate these lists with na mes from datastore. Then in user_main.html make them link to Channel viewer, no link, survey fillout page
	l1=[1,'/.','/', ""]
	l2=[4,5,6, ""]
	l3=[7,8,9,10]
	
	return render_template('user_main.html', email=session.get('email'), password=session.get('password'), table_rows=zip(l1,l2,l3))

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500