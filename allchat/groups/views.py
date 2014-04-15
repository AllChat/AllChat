from flask.views import MethodView
from flask import request, make_response, g, session
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupList, FriendList, GroupInfo
from sqlalchemy import and_
from allchat.amqp.Impl_kombu import RPC, cast


class groups_view(MethodView):
    def get(self):
        pass
    def post(self):
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            try:
                para = request.get_json()
            except Exception as e:
                resp = make_response(("The json data can't be parsed", 403, ))
                return resp
            # parse the json data and handle the request
            
        else:
            return ("Please upload a json data", 403)

    def put(self,group_id):
        if group_id is None:
            return ("Error in the URL. Please contain proper group id in the URL.", 403)
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            pass
        else:
            return ("Please upload a json data", 403)

    def delete(self, group_id):
        pass
