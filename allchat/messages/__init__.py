from flask import Blueprint
from allchat.messages import views

message = Blueprint('messages', __name__)
message_view = views.messages_view.as_view('messages_view')
message.add_url_rule('/messages', view_func = message_view, methods = ['GET', ])
message.add_url_rule('/messages/<string:type>', view_func = message_view, methods = ['POST', ])
