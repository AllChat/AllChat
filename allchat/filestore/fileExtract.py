# --*-- coding:utf-8 --*--
import os
from encrypt import Encryptor

class FileExtractor(object):
    def __init__(self):
        pass
        
    def getFileContent(self, startTime, endTime, option):
        ''' get the file content of required users in the specific time duration.
            option(dict) contains user/group information, 'type'=user/group;
            in case of user, there shall include 'chatFrom'=... and 'chatTo'=...
            in case of group, there shall include 'groupName'=...
            if no files can be found according to the params, returns None
        '''
        pass
        
