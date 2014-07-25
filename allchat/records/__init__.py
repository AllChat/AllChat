from flask import Blueprint
from allchat.records import views

record = Blueprint('records', __name__)
record_view = views.records_view.as_view('records_view')
record.add_url_rule('/records/', view_func = record_view, methods = ['GET' ,])