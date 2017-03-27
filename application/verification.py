from google.appengine.ext import ndb
import logging
from pbkdf2 import PBKDF2
from functools import wraps
from flask import g, request, redirect, url_for

from os import urandom
from base64 import b64encode
from flask_httpauth import HTTPBasicAuth
import random, string
from binascii import hexlify
from flask import session
from datastore_account import get_user_verification_data_by_id

auth=HTTPBasicAuth()

def getRandomString(length):
	RNG = random.SystemRandom()
	characters = string.ascii_letters + string.digits
	return "".join(RNG.choice(characters) for n in range(64))

"""Verifies that when you hash the given password with the users salt, the hashes are the same, the third argument is a tuple containing email, salt and salted hashed password"""
def isPasswordCorrect(password, email_salt_saltedpassword):
	# h1=scrypt(password,email_salt_saltedpassword[1])
	h1=PBKDF2( password, email_salt_saltedpassword[1], iterations=1000).read(64)
	logging.info(hexlify(h1))
	logging.info(email_salt_saltedpassword)
	return hexlify(h1)==email_salt_saltedpassword[2]

	
"""Takes a new email and password. Returns a tuple with the email, a random salt and a hash of the password with the salt"""
def get_new_verification_data(email, password):
	logging.info(password)
	salt = getRandomString(64)
	# logging.info(s)
	# salt = sha1(urandom(128)).hexdigest()
	logging.info(salt)
	salted_hashed_password=	PBKDF2( password, salt, iterations=1000).read(64)
	logging.info(salted_hashed_password)
	salted_hashed_password=hexlify(salted_hashed_password)
	logging.info(salted_hashed_password)
	return (email,salt,salted_hashed_password)
    


def login_required(f):
	"""
	Decorator function for views that require a login.
	using the decorator @login_required will call this function
	prior to giving access to the view.
	"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		logging.info('12345678')
		if not verify_user():
			return redirect(url_for('login', next=request.url))
		return f(*args, **kwargs)
	return decorated_function

def verify_user():
	"""
	Checks that the userId and password saved in Flasks
	secure session cookie matches. The userId and password should
	be saved in the cookie on login. 
	"""
	logging.info(session.get('email'))
	logging.info(session.get('password'))
	logging.info(session.get('userId'))
	if('userId' in session):
		user_salt_saltedpassword=get_user_verification_data_by_id(session.get('userId'))
		#if user exists
		logging.info(user_salt_saltedpassword)
		if(user_salt_saltedpassword):
			if isPasswordCorrect(session.get('password'),user_salt_saltedpassword):
				return True
			else:
				return False
	return False
	
# @auth.verify_password
# def verify_password(email, password):
	# logging.info(session.get('email'))
	# logging.info(session.get('password'))
	# logging.info(session.get('userId'))
	# if('userId' in session):
		# user_salt_saltedpassword=get_user_verification_data_by_id(session.get('userId'))
		# #if user exists
		# logging.info(user_salt_saltedpassword)
		# if(user_salt_saltedpassword):
			# if isPasswordCorrect(session.get('password'),user_salt_saltedpassword):
				# return True
			# else:
				# return False
	# return False
		#user=getUser(session.get('email'))
		#if isUser(session):
		#	if isPasswordCorrect(user, session.get('password')):
		#		return True
		#else:
		#	return False


#def isUser(user):
#	if user.count() != 0:
#		return True
#	return False
#def isPasswordCorrect(user,password):
#	logging.info(user.get().password)
#	if(user.get().password==password):
#		return True
#	return False
#def isNewUserValid(user):
#	"""Checks if the new user is valid. F.ex an email address"""
#	return True
#def isUniqueUser(email):
#	return True
#def isNewPasswordValid(password):
#	"""Checks if the password is acceptable"""
#	return True

#def isUserOwnerOfChannel(channel):
#	return True