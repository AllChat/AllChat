from flask import Blueprint
from allchat import app

version = Blueprint('version', __name__)

@version.route('/version')
def get_version():
    return "version"
