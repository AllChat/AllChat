from flask import Blueprint
from allchat import app
from flask import jsonify

version = Blueprint('version', __name__)

@version.route('/version')
def get_version():
    data = {}
    data['version'] = []
    v1 = {}
    v1['id'] = 'v1'
    v1['links'] = []
    tmp = {}
    tmp['href'] = 'https://www.allchat.com/v1/'
    tmp['rel'] = 'self'
    v1['links'].append(tmp)
    v1['status'] = 'CURRENT'
    v1['updated'] = '2014-02-26T14:32:00Z'
    data['version'].append(v1)
    return jsonify(data)

