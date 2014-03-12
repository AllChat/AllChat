from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('../conf/allchat.cfg', silent = True)

from allchat import accounts
#from allchat import database
#from allchat import filestore
#from allchat import friends
#from allchat import groups
#from allchat import heatbeat
#from allchat import login
#from allchat import messages
#from allchat import records
from allchat import versions
from allchat.database.sql import db_session
from allchat.database import init_db

app.register_blueprint(versions.version)
app.register_blueprint(accounts.account, url_prefix = '/v1')


@app.before_first_request
def init():
    init_db()
    
@app.teardown_request
def shutdown_session(exception=None):
    if db_session is not None:
        db_session.remove()