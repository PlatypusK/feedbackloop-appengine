import logging
import traceback
import urllib2


def buildJsonForOneSigIds(oneSigUidList):
	jsonString="\"include_player_ids\": ["
	for sig in oneSigUidList:
		jsonString+="\""+sig+"\","
	jsonString=jsonString[:-1]
	jsonString+="]"
	return jsonString
def getOneSigToUsersHeader():
	return {"Content-Type": "application/json; charset=utf-8",
          "Authorization": "Basic YjQ0MjI3ODAtNjJkNC00MzkzLWE2MmYtYjNkYjUwMjgzNjU3"}
def getOneSigToUsersPayload(oneSigUidList,message):
	return "{\"app_id\": \"b3baf272-6679-4697-99bb-63d2b2c37b0e\","+\
	"\"contents\": {\"en\": \""+message+"\"},"+\
	buildJsonForOneSigIds(oneSigUidList)+\
	"}"
def sendMessageToOneSignalUsers(oneSigUidList,message):
	"""Sends a message to the One Signal devices specified by the list of ids in oneSigUidList"""
	logging.info(oneSigUidList)
	header=getOneSigToUsersHeader()
	payload = getOneSigToUsersPayload(oneSigUidList,message)
	req = urllib2.Request('https://onesignal.com/api/v1/notifications',payload,header)
	try:
		response = urllib2.urlopen(req)
	except urllib2.URLError as e:
		if hasattr(e, 'reason'):
			logging.error('Failed to reach a server.')
			logging.error(e)
		elif hasattr(e, 'code'):
			logging.error('The server couldn\'t fulfill the request.')
			logging.error('Error code: ', e.code)
	else:
		# everything is fine
		the_page = response.read()
		