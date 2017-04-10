from flask import Flask, render_template,request, redirect, url_for,current_app, session, abort
from forms import *
import datastore_channel
import datastore_loop
import datastore_account
import logging
import json

ACTION_SEARCH="search"
ACTION_SUBSCRIBE="subscribe"
ACTION_PUBLISH="publish"
ACTION_DETAILS="details"
ACTION_SUBMIT_REPLY="Submit survey reply"
ACTION_SHOW_SURVEY='Show survey';
ACTION_SHOW_LOOP_RESULTS='Show loop results'
ACTION_CREATE_LOOP='create_loop'
ACTION_VIEW_LOOP_RESULTS='view loop results'
ACTION_SAVE_ONE_SIGNAL='save one signal uid'
ACTION_RESET_PASSWORD='reset password'

"""payLoad parameter in request.form should be set to the search request prior to invoking this function"""
def actionSearchChannel():
	form=ChannelSearchResults()
	logging.info('search')
	searchResult=datastore_channel.searchChannel(request.form['payLoad'])
	return render_template('channel_search_results.html',form=form, channel_list=searchResult)
"""payLoad parameter in request.form should be set to the channed id that the user wants to subscribe to prior to invoking this function"""	
def actionSubscribe():
	datastore_channel.subscribeChannel(session.get('userId'), request.form['payLoad'])
	return redirect(url_for('user_main'))
def actionPublish():
	logging.debug("publish")
	if datastore_loop.publish_loop(session.get('userId'), request.form['channel_id'], request.form['jsonString']):
		return redirect(url_for('view_owned_channels'),code=302)
	abort(401)
def actionViewDetails():
	return redirect(url_for('subscribed_channel_info'), code=307)
def actionShowSubscribedChannels():
	channel_list=datastore_channel.getSubscribedChannelIdentifiers(session.get('userId'))
	form=SubscribedChannelsForm()
	return render_template('subscribed_channels.html', form=form, channel_list=channel_list)
def actionSearchRedirect():
	return redirect(url_for('channel_search_results'), code=307)
def actionShowWelcomeScreen():
	form=UserMainForm()
	logging.info('-*+-*/+9/-+*/-*/-98566+18478+*4+8+984984')
	channels=datastore_channel.getSubscribedChannelIdentifiers( session.get('userId'))
	activeLoops=datastore_loop.getActiveLoops(channels)
	logging.info(activeLoops)
	activeLoops=datastore_account.removeAnsweredLoops(session.get('userId'),activeLoops);
	form.payLoad.data=json.dumps(activeLoops)
	logging.info(activeLoops)
	return render_template('user_main.html', form=form, loop_list=activeLoops)
def actionShowSurvey():
	form=ShowSurveyForm()
	return render_template('show_survey.html', form=form)
def actionSubmitSurvey():
	"""This saves a submitted reply to disk and redirects the user back to main screen"""
	reply=request.form['payLoad'];
	logging.info('198419841984')
	logging.info(reply);
	try:
		replyObject=json.loads(reply);
	except ValueError as e:
		abort(400)
	if datastore_loop.storeLoopReply(session.get('userId'),reply, replyObject):
		return redirect(url_for('user_main'),code=302)
	abort(400)
def actionCreateLoop():
	return redirect(url_for('create_loop'),code=307)
def actionRedirectToLoopResults():
	return redirect(url_for('show_loop_results'), code=307)
def actionShowSurveyResults():
	form=ShowSurveyResultsForm()
	replies=datastore_loop.getResultJson(request.form['payLoad'])
	nrOfQuestions=datastore_loop.countQuestions(request.form['payLoad'])
	index=[x for x in range(0,nrOfQuestions)]
	if len(replies)==0:
		form.payLoad.data="no data"
	else:
		form.payLoad.data=replies
	return render_template('show_loop_results.html', form=form, index=index);
def actionLogOut():
	session.clear()
	return redirect(url_for('login'))
def actionSaveOneSignalUid():
	"""Expects form payload to be a string containing the new OneSignalUid"""
	datastore_account.setOneSignalId(session.get('userId'), request.form['payLoad'])
	return ""
def actionResetPassword():
	return redirect(url_for('login'))