from flask import Blueprint
from allchat.filestore import fileSave,fileExtract

filestore = Blueprint('filestore', __name__)
saver = fileSave.FileSaver()
extractor = fileExtract.FileExtractor()
