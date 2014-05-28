# --*-- coding:utf-8 --*--
import win32com.client
import time
import os
from threading import Timer

class FileSave(object):
    def __init__(self):
        self.key = '0x1cd59c152bL'
        self.msgBuffer = dict()
        self.writePeriod = 900.0 
        self.writeBuffer2File(self.writePeriod)
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
    def saveMessage(self, Sender, Receiver, msgDict):
        message = '\r\n'.join(['\t'.join((key,msgDict[key])) for key in msgDict])
        if '::'.join(Sender,Receiver) in self.msgBuffer:
            self.msgBuffer['::'.join(Sender,Receiver)].append({Sender:message})
        elif '::'.join(Receiver,Sender) in self.msgBuffer:
            self.msgBuffer['::'.join(Receiver,Sender)].append({Sender:message})
        else:
            self.msgBuffer['::'.join(Sender,Receiver)] = [{Sender:message}]
        
    def savePicture(self, pic, pic_format, sender):
        file_name = ''.join(time.strftime("%Y%m%d%H%M%S",time.localtime()),
                            sender,'.',pic_format)
        pic_dir = os.path.abspath(self.current_dir + '/../../Data/picture')
        if not os.path.exists(pic_dir):
            os.makedirs(pic_dir)
        f=open(os.path.join(pic_dir,file_name),'wb')
        f.write(pic)
        f.close()
        return os.path.join('/Data/picture',file_name)

    def writeBuffer2File(self,period):
        timer = Timer(period,writeBuffer2File)
        timer.start()
        if self.msgBuffer:
            #write msg to files according to the sender and receiver
            #before write to files, call self.encrypt to commit encryption
            # ....to be finished
            self.msgBuffer = dict()
            
        
    def encrypt(self,content): # key:密钥,content:明文 
        EncryptedData = win32com.client.Dispatch('CAPICOM.EncryptedData') 
        EncryptedData.Algorithm.KeyLength = 5 
        EncryptedData.Algorithm.Name = 2 
        EncryptedData.SetSecret(self.key) 
        EncryptedData.Content = content 
        return EncryptedData.Encrypt() 
        
