from flask import Blueprint
from allchat.friends import views

friend = Blueprint('friends', __name__)
friend_view = views.friends_view.as_view('friends_view')
friend.add_url_rule('/friends/', view_func = friend_view, methods = ['GET', ])
friend.add_url_rule('/friends/<string:name>', view_func = friend_view, methods = ['POST', 'DELETE'])

