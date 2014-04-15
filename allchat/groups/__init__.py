from flask import Blueprint
from allchat.groups import views

group = Blueprint('groups', __name__)
group_view = views.groups_view.as_view('groups_view')
group.add_url_rule('/groups/', view_func = group_view, methods = ['GET', 'POST'])
group.add_url_rule('/groups/<int:group_id>', view_func = group_view, methods = ['PUT', 'DELETE'])
