import logging

from flask import Flask, render_template,request, redirect, url_for,current_app, session, abort
from flask_httpauth import HTTPBasicAuth
from datastore_account import Account, storeNewUser,  get_user_verification_data_by_email
import datastore_account
from verification import  isPasswordCorrect,  get_new_verification_data
import json
import os
from flask_wtf import Form
from forms import *
from flask_wtf.csrf import CSRFProtect
from datastore_channel import Channel, getChannel
from main import app, csrf, application_title
from verification import auth, login_required
import verification
from datastore_channel import get_owned_channel_identifiers, verify_channel_owner, get_owned_channel_data, searchChannel
import datastore_channel
from datastore_loop import publish_loop
from actions import *





@app.route('/')
def hello():
    return redirect(url_for('login'),301)
	
@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm() if request.method == 'POST' else LoginForm(request.args)
	if form.validate_on_submit():
		verification_data=get_user_verification_data_by_email(request.form['email'])
		if verification_data:
			if isPasswordCorrect(request.form['password'], verification_data):
				session['email']=request.form['email']
				session['password']=request.form['password']
				logging.debug('+-+-+-+-+-+'+str(verification_data[0]))
				session['userId']=str(verification_data[0])
				return redirect(url_for('user_main'))
			return render_template('login_page.html', form=form)
	return render_template('login_page.html', form=form)
	
@app.route('/new_user', methods=['GET','POST'])
def new_user():
	form = RegistrationForm() if request.method == 'POST' else RegistrationForm(request.args)
	if form.validate_on_submit():
		logging.debug('+/+/+/+/+')
		user_exists=datastore_account.get_user_verification_data_by_email(form.email.data)
		if not user_exists: #Check that the user does not exist
			logging.debug('user does not exist')
			verification_data=verification.get_new_verification_data(form.email.data, form.password.data)
			stored=storeNewUser(verification_data)
			if stored:
				logging.debug('user stored')
				return redirect(url_for('login',code=302))
			return redirect(url_for('new_user',code=307))
		logging.debug('tried to create existing user')
	logging.debug("here")
	return render_template('new_user.html', form=form)
	
@app.route('/forgot_password')
def forgot_password():
	form=ForgotPasswordForm(request.args)
	return render_template('forgot_password.html', form=form)
	
@app.route('/about')
def about():
	message="Information about this Application: "
	return render_template('about.html', title=application_title, message=message)	

@app.route('/channel_search_results', methods=['GET','POST'])
def channel_search_results():
	if request.form.has_key('action'):
		if request.form['action'] == ACTION_SEARCH:
			return actionSearchChannel()
		if request.form['action'] == ACTION_SUBSCRIBE:
			return actionSubscribe()
	else:
		abort(400)
	# logging.debug(request.args)
	
	# logging.debug(searchResult)
	# form=ChannelSearchResults()
	# return render_template('channel_search_results.html',form=form, channel_list=searchResult)
	
@app.route('/subscribed_channels', methods=['GET','POST'])
def subscribed_channels():
	form=SubscribedChannelsForm()
	if request.form.has_key('action'):
		if request.form['action']==ACTION_SEARCH:
			return actionSearchRedirect()
		if request.form['action']==ACTION_DETAILS:
			return actionViewDetails()
	return actionShowSubscribedChannels()
		
	
@app.route('/create_loop', methods=['GET','POST'])
@login_required
def create_loop():
	form=NewLoopForm()
	logging.debug('*+*+*+*+*+*')
	if request.form.has_key('action'):
		if request.form['action']==ACTION_PUBLISH:
			return actionPublish()
	form.channel_id.data=request.form['channel_id_for_new_loop']
	return render_template('create_loop.html', form=form)

	
@app.route('/owned_channel', methods=['GET','POST'])
@login_required
def owned_channel():
	if request.form.has_key('action'):
		if request.form['action']==ACTION_CREATE_LOOP:
			return actionCreateLoop()
		if request.form['action']==ACTION_VIEW_LOOP_RESULTS:
			return actionRedirectToLoopResults();
	form=OwnedChannelForm()
	channelId=request.form['channelid']
	loopList=datastore_loop.getRecentExpiredLoops(7, channelId)
	logging.debug(loopList)
	form.channel_id_for_new_loop.data=channelId
	channel=get_owned_channel_data(session.get('userId'),channelId);
	form.channel_name=channel.name
	logging.debug('++++++++')
	return render_template('owned_channel.html', form=form, loop_list=loopList)

@app.route('/view_owned_channels', methods=['GET','POST'])
@login_required
def view_owned_channels():
	form = OwnedChannelsForm() if request.method == 'POST' else OwnedChannelsForm(request.args)
	if request.method=='POST':
		logging.debug('-*/-*/-*/')
		logging.debug(request.form)
		id=request.form['channelid']
		logging.debug(id)
		if(verify_channel_owner(session.get('userId'),id)):
			logging.debug("Redirect to owned channel")
			return redirect(url_for('owned_channel'),code=307)
		abort(401)
	channel_list=get_owned_channel_identifiers(session.get('userId'))
	print channel_list
	return render_template('owned_channels.html', form=form, channel_list=channel_list)

@app.route('/new_channel', methods=['GET','POST'])
@login_required
def new_channel():
	form = NewChannelForm() if request.method == 'POST' else NewChannelForm(request.args)
	if form.validate_on_submit():
		logging.info('validated------new_channel-------'+
			request.form['channelname']+'-------'+request.form['description'])
		logging.info(session.get('userId'))
		datastore_channel.writeChannel(int(session.get('userId')),request.form['channelname'],request.form['description'])
		return redirect(url_for('view_owned_channels'))
	logging.info(form.errors.items())
	return render_template('create_channel.html', form=form)

"""This is the view method for the first screen you see upon login"""
@app.route('/user_main', methods=['GET','POST'])
@login_required
def user_main():
	if request.form.has_key('action'):
		if request.form['action']==ACTION_SHOW_SURVEY:
			return actionRedirectToSurvey()
	return actionShowWelcomeScreen()
	
"""This is the view method for showing plots and statistics from loops"""
@app.route('/show_loop_results', methods=['GET','POST'])
@login_required
def show_loop_results():
	if request.form.has_key('action'):
		if request.form['action']==ACTION_VIEW_LOOP_RESULTS:
			return actionShowSurveyResults()
	pass
	
	
"""This is the view method for users to reply to posted surveys"""
@app.route('/show_survey', methods=['GET','POST'])
@login_required
def show_survey():
	if request.form.has_key('action'):
		if request.form['action']==ACTION_SUBMIT_REPLY:
			return actionSubmitSurvey();
		if request.form['action']==ACTION_SHOW_SURVEY:
			return actionShowSurvey()
	abort(400)

"""This is the view method for users to log out"""
@app.route('/log_out', methods=['GET'])
@login_required
def log_out():
	return actionLogOut();


@app.route('/save_one_signal', methods=['POST'])
@login_required
def save_one_signal():
	"""
	This is the view method for users to give the userid for one signal to the server.
	We need this to send notifications. Flow is user subscribes to OneSignal through javascript,
	user gives OneSignal id to server. Server stores OneSignal id in account, Server loads the 
	OneSignal id from the subscribed accounts when a loop is published and sends a notification
	to all subscribers. 
	"""
	logging.debug("save one signal user id")
	if request.form.has_key('action'):
		if request.form['action']==ACTION_SAVE_ONE_SIGNAL:
			return actionSaveOneSignalUid();
	abort(400)

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
