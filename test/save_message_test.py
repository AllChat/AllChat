# -*- coding: cp936 -*-
import time,os,sys

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(
        sys.argv[0]), os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "allchat", "__init__.py")):
    sys.path.insert(0, possible_topdir)
sys.path.insert(0, possible_topdir)

from allchat import filestore
from allchat.filestore.fileSave import FileSaver

if __name__=='__main__':
    saver = FileSaver()
    saver.saveSingleMessage('alex','derake',[
        time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),
        'this is a test message,没有实际含义'])
    saver.saveSingleMessage('derake','alex',[
        time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),
        'this is a test message,没有实际含义'])
    saver.saveGroupMsg('alex','allchat',[
        time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),
        'this is a test message,没有实际含义'])
    saver.saveGroupMsg('derake','allchat',[
        time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),
        'this is a test message,没有实际含义'])
    saver.writeBuffer2File()
    
