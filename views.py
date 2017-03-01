import logging

from flask import Flask, render_template,request, redirect, url_for,current_app, session, abort
from flask_httpauth import HTTPBasicAuth
from datastore_account import Account, storeNewUser,  get_user_verification_data
from verification import  isPasswordCorrect,  get_new_verification_data
import json
import os
from flask_wtf import Form
from forms import LoginForm, NewChannelForm, RegistrationForm, ForgotPasswordForm, OwnedChannelsForm
from flask_wtf.csrf import CSRFProtect
from datastore_channel import Channel, getChannel
from main import app, csrf, application_title
from verification import auth
from datastore_channel import get_owned_channel_identifiers, verify_channel_owner







@app.route('/')
def hello():
    return redirect(url_for('login'))
	



@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm() if request.method == 'POST' else LoginForm(request.args)
	if form.validate_on_submit():
		verification_data=get_user_verification_data(request.form['email'])
		if verification_data:
			if isPasswordCorrect(request.form['password'], verification_data):
				session['email']=request.form['email']
				session['password']=request.form['password']
				logging.info('+-+-+-+-+-+'+str(verification_data[0]))
				session['userId']=str(verification_data[0])
				return redirect(url_for('user_main'))
			return render_template('login_page.html', form=form)
	return render_template('login_page.html', form=form)		
			
		# user=getUser(request.form['email'])
		# if isUser(user):
			# if isPasswordCorrect(user, request.form['password']):
				# session['email']=request.form['email']
				# session['password']=request.form['password']
				# logging.info('+-+-+-+-+-+'+str(user.get().key.id()))
				# session['userId']=str(user.get().key.id())
				# return redirect(url_for('user_main'))
		# return render_template('login_page.html', form=form)
		# logging.info("validate password here")
		# logging.info(form.password.data)
	# logging.info(form.errors.items())
	# return render_template('login_page.html', form=form)
	
@app.route('/new_user', methods=['GET','POST'])
def new_user():
	form = RegistrationForm() if request.method == 'POST' else RegistrationForm(request.args)
	if form.validate_on_submit():
		logging.info('+/+/+/+/+')
		user_exists=get_user_verification_data(form.email.data)
		if not user_exists: #Check that the user does not exist
			verification_data=get_new_verification_data(form.email.data, form.password.data)
			stored=storeNewUser(verification_data)
			if stored:
				return redirect(url_for('login',code=302))
			return redirect(url_for('new_user',code=307))
	return render_template('new_user.html', form=form)
	
@app.route('/forgot_password')
def forgot_password():
	form=ForgotPasswordForm(request.args)
	return render_template('forgot_password.html', form=form)
	
@app.route('/about')
def about():
	message="Information about this Application: "
	return render_template('about.html', title=application_title, message=message)	

	
@app.route('/create_loop', methods=['GET','POST'])
@auth.login_required
def create_loop():
	logging.info('*+*+*+*+*+*')
	return render_template('create_loop.html', channel_name="name of channel")
	
@app.route('/owned_channel', methods=['GET','POST'])
@auth.login_required
def owned_channel():
	channelId=request.args.get('channelid')
	channel=getChannel(long(channelId))
	logging.info('++++++++')
	return render_template('owned_channel.html', channel_name=channel.name)

@app.route('/view_owned_channels', methods=['GET','POST'])
@auth.login_required
def view_owned_channels():
	form = OwnedChannelsForm() if request.method == 'POST' else OwnedChannelsForm(request.args)
	if request.method=='POST':
		logging.info('-*/-*/-*/')
		logging.info(request.form)
		id=request.form['channel_id']
		logging.info(id)
		if(verify_channel_owner(session.get('userId'),id)):
			return redirect(url_for('owned_channel', channelid=id))
		abort(401)
	channel_list=get_owned_channel_identifiers(session.get('userId'))
	print channel_list
	return render_template('owned_channels.html', form=form, channel_list=channel_list)

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
		return redirect(url_for('owned_channel', channelid=id))
	logging.info(form.errors.items())
	return render_template('create_channel.html', form=form)

"""This is the view method for the first screen you see upon login"""
@app.route('/user_main', methods=['GET','POST'])
@auth.login_required
def user_main():
	# email=request.form['email']
	# password=request.form['password']
	#Populate these lists with na mes from datastore. Then in user_main.html make them link to Channel viewer, no link, survey fillout page
	#l1=[1,'/.','/', ""]
	#l2=[4,5,6, ""]
	#l3=[7,8,9,10]
    #table_rows=zip(l1,l2,l3)
	return render_template('user_main.html', email=session.get('email'), password=session.get('password'), title=application_title)

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
