from flask import Blueprint
from allchat.filestore import fileSave,fileExtract

filestore = Blueprint('filestore', __name__)
