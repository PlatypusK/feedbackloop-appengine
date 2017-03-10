from flask import Flask, render_template,request, redirect, url_for,current_app, session, abort
from forms import *
import datastore_channel
import logging

ACTION_SEARCH="search"
ACTION_SUBSCRIBE="subscribe"
ACTION_PUBLISH="publish"

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
	