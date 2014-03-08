from flask import Flask

app = Flask(__name__)

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

app.register_blueprint(versions.version)
