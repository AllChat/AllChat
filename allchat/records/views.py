from flask.views import MethodView
from flask import request, make_response, g, session, jsonify
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupMember, FriendList, GroupInfo
from sqlalchemy import and_
from allchat.filestore.fileExtract import FileExtractor
import json

class records_view(MethodView):
	def get(self):
		header = request.headers
		for item in ['account', 'starttime', 'endtime', 'chattype', 'chatname']:
			if item not in header:
				return make_response(("Missing critical information.", 403))
		account = header['account']
		starttime = header['starttime']
		endtime = header['endtime']
		chattype = header['chattype']
		chatname = header['chatname']
		db_session = get_session()
		try:
		    db_user = db_session.query(UserInfo).filter_by(username = account).one()
		except:
		    return make_response(("Invalid user.", 404))
		# if account!=session['account']:
		# 	return make_response(("Username not match to currently logged in user.", 404))

		starttime = starttime.replace('-','').replace('/','')
		endtime = endtime.replace('-','').replace('/','')

		if chattype == 'group':
			try:
				db_user = db_session.query(GroupMember).filter(and_(GroupMember.group_name == chatname, GroupMember.member_account == account)).one()
			except:
				return make_response(('User not in the group!',404))
		elif chattype == 'user':
			try:
				##search database if the friend relationship exist
				db_user = db_session.query(UserInfo).join(FriendList).filter(and_(UserInfo.username == account, FriendList.username == chatname, FriendList.confirmed == True )).one()
			except:
				return make_response(('Requested users are not friends.',404))
		else:
			return make_response(('Chattype wrong.',403))

		## revised by dongzai on 2014-07-27, use segment records result to response
		response_chunk_size = 20
		extractor = FileExtractor()
		if chattype == 'group':
			option = {'type':'group','groupName':chatname,'userName':account}
		elif chattype == 'user':
			option = {'type':'user','chatFrom':account,'chatTo':chatname}
		record = extractor.getChatRecord(starttime,endtime,option)
		if 'offset' not in header:
			offsets = 0
		elif int(header['offset'])*response_chunk_size > len(record):
			return ('offset exceed length of search result.', 501)
		else:
			offsets = int(header['offset'])*response_chunk_size
		result = record[offsets:min(offsets+response_chunk_size,len(record))]
		chat_record = dict()
		chat_record['records'] = [list(item) for item in result]
		chat_record['result_size'] = len(record)
		chat_record['current_offset'] = offsets
		return jsonify(chat_record)
