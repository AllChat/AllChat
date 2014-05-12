from flask import Blueprint
from allchat.messages import views

message = Blueprint('messages', __name__)
message_view = views.messages_view.as_view('messages_view')
message.add_url_rule('/messages/<string:type>/<string:user>/', defaults= {'file' : None},
                     view_func = message_view, methods = ['GET', ])
message.add_url_rule('/messages/<string:type>/<string:user>/<string:file>' ,view_func = message_view,
                     methods = ['GET', ])
message.add_url_rule('/messages/<string:type>', view_func = message_view, methods = ['POST', ])
