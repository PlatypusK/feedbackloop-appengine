from google.appengine.ext import ndb
import logging


def isUser(user):
	if user.count() != 0:
		return True
	return False
def isPasswordCorrect(user,password):
	logging.info(user.get().password)
	if(user.get().password==password):
		return True
	return False
def isNewUserValid(user):
	"""Checks if the new user is valid. F.ex an email address"""
	return True
def isUniqueUser(email):
	return True
def isNewPasswordValid(password):
	"""Checks if the password is acceptable"""
	return True

	