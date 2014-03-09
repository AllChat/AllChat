from flask import Blueprint
from allchat.accounts import views
import allchat

account = Blueprint('accounts', __name__)
account_view = views.accounts_view.as_view('accounts_view')
account.add_url_rule('/accounts/', defaults={'name': None}, view_func = account_view, methods = ['GET', ])
account.add_url_rule('/accounts/', view_func = account_view, methods = ['POST', ])
account.add_url_rule('/accounts/<string:name>', view_func = account_view, methods = ['GET', 'PUT', 'DELETE'])
