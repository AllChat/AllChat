from flask import Flask, render_template, url_for, redirect, session, request

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config.from_pyfile('../conf/allchat.cfg', silent = True)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


from allchat.database.sql import get_session
from allchat.database import init_db
from allchat import messages
from allchat.amqp import init_rpc
from allchat import accounts
#from allchat import database
from allchat import filestore
from allchat import friends
from allchat import groups
#from allchat import heatbeat
from allchat import login
#from allchat import records
from allchat import versions

app.register_blueprint(versions.version)
app.register_blueprint(accounts.account, url_prefix = '/v1')
app.register_blueprint(login.login, url_prefix = '/v1')
app.register_blueprint(friends.friend, url_prefix = '/v1')
app.register_blueprint(groups.group, url_prefix = '/v1')
app.register_blueprint(messages.message, url_prefix = '/v1')
app.register_blueprint(filestore.filestore, url_prefix = '/v1')


def init():
    init_db()
    init_rpc()
    
@app.teardown_request
def shutdown_session(exception=None):
    db_session = get_session()
    if db_session is not None:
        db_session.remove()

@app.route('/', methods = ['GET'])
@app.route('/index.html', methods = ['GET'])
def index():
    if 'account' in request.cookies and 'account' in session \
            and session['account'] == request.cookies['account']:
        return render_template('index.html')
    else:
        return render_template('login.html')

@app.route('/login.html', methods = ['GET'])
def login():
    return redirect(url_for('index'))

    #return redirect(url_for('login.login_view'))
@app.route('/register.html', methods = ['GET'])
def signup():
    return render_template('register.html')
