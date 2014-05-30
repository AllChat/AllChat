# -*- coding: cp936 -*-
import time,os,sys
from pprint import pprint

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(
        sys.argv[0]), os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "allchat", "__init__.py")):
    sys.path.insert(0, possible_topdir)
sys.path.insert(0, possible_topdir)

from allchat import filestore
from allchat.filestore.fileExtract import FileExtractor

if __name__=='__main__':
    extractor = FileExtractor()
    pprint(extractor.getChatRecord('20140204','20140601',
                            {'type':'user','chatFrom':'alex','chatTo':'derake'}))
    pprint(extractor.getChatRecord('20140204','20140601',
                            {'type':'group','groupName':'allchat','userName':'derake'}))
    
