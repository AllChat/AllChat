from flask import Blueprint

filestore = Blueprint('filestore', __name__)

from allchat.filestore import storage
saver = storage.MessageSaver()