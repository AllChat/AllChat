from flask import Blueprint
from allchat.filestore import fileSave

filestore = Blueprint('filestore', __name__)
saver = fileSave.FileSaver()
