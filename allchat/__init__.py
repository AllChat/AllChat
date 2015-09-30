from flask import Flask, render_template, url_for, redirect, session, request, make_response
from flask.ext.sqlalchemy import SQLAlchemy
import os
import base64
from .path import get_project_root

app = Flask(__name__, template_folder='../templates', static_folder='../static')
config_file = os.path.join(get_project_root(), 'conf/allchat.cfg')
app.config.from_pyfile(config_file, silent = True)
sk_file = os.path.join(get_project_root(), 'conf/seckey')
if not os.path.exists(sk_file):
    raw_key = os.urandom(32)
    with open(sk_file, 'wb') as f:
        f.write(raw_key)
else:
    with open(sk_file, 'rb') as f:
        raw_key = f.read()
app.secret_key = base64.b64encode(raw_key).decode()

db = SQLAlchemy(app, session_options={'autoflush':False, 'expire_on_commit':False, \
                                      'autocommit':True})
user_states = dict()

# from allchat.database.sql import get_session
from allchat.database import init_db
from allchat.database.models import UserAuth, UserInfo
from allchat.authentication import authorized
from allchat.administrator import views
from allchat import messages
from allchat.amqp import init_rpc
from allchat import accounts
from allchat import filestore
from allchat import friends
from allchat import groups
from allchat import login
from allchat import records
from allchat import versions

app.register_blueprint(versions.version)
app.register_blueprint(accounts.account, url_prefix = '/v1')
app.register_blueprint(login.login, url_prefix = '/v1')
app.register_blueprint(friends.friend, url_prefix = '/v1')
app.register_blueprint(groups.group, url_prefix = '/v1')
app.register_blueprint(messages.message, url_prefix = '/v1')
app.register_blueprint(filestore.filestore, url_prefix = '/v1')
app.register_blueprint(records.record, url_prefix = '/v1')

def init_admin():
    user = db.session.query(UserInfo).filter_by(username='root').first()
    if user is None:
        admin = UserInfo("root", "XXX@XXX.XXX")
        auth = UserAuth("root", "passw0rd")
        db.session.begin()
        try:
            db.session.add(admin)
            db.session.add(auth)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
#@app.before_first_request
def init():
    init_db()
    init_admin()
    init_rpc()
    
# @app.teardown_request
# def shutdown_session(exception=None):
#     db_session = get_session()
#     if db_session is not None:
#         db_session.remove()

@app.route('/', methods = ['GET'])
@app.route('/index.html', methods = ['GET'])
def index():
    # db_session = db.session
    try:
        account = session['account']
        # token = request.headers['token']
        # auth = db_session.query(UserAuth).filter(db.and_(UserAuth.account == account, \
        #                                                     UserAuth.deleted == False)).one()
    except Exception as e:
        return redirect(url_for('login'))
    else:
        # if not auth.is_token(token) or auth.is_token_timeout():
        #     return redirect(url_for('login'))
        # else:
        resp = make_response(render_template('index.html'))
        return resp

@app.route('/login.html', methods = ['GET'])
def login():
    return render_template('login.html')

@app.route('/register.html', methods = ['GET'])
def signup():
    return render_template('register.html')
