from flask import Blueprint
from allchat.login import views
import allchat

login = Blueprint('login',__name__)
login_view = views.login_view.as_view('login_view')
login.add_url_rule('/login/<string:name>/',view_func = login_view, methods = ['POST', 'GET'])
