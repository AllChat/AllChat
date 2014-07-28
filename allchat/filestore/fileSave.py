# --*-- coding:utf-8 --*--
import time
import os
import allchat
from threading import Timer
from encrypt import Encryptor

class FileSaver(object):
    def __init__(self):
        self.msgBuffer = dict()
        self.writeInterval = 600.0 
        self.writeBuffer2File()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
    def saveSingleMessage(self, Sender, Receiver, msgStruct):
        ## msgStruct consist of [time,content],one msg at a time
        message = '&:'.join(msgStruct)
        if '::'.join([Sender,Receiver]) in self.msgBuffer:
            self.msgBuffer['::'.join([Sender,Receiver])].append('&:'.join([Sender,message]))
        elif '::'.join([Receiver,Sender]) in self.msgBuffer:
            self.msgBuffer['::'.join([Receiver,Sender])].append('&:'.join([Sender,message]))
        else:
            self.msgBuffer['::'.join([Sender,Receiver])] = ['&:'.join([Sender,message])]

    def saveGroupMsg(self, Sender, GroupName, msgStruct):
        ## msgStruct consist of [time,content],one msg at a time
        message = '&:'.join(msgStruct)
        if GroupName in self.msgBuffer:
            self.msgBuffer[GroupName].append('&:'.join([Sender,message]))
        else:
            self.msgBuffer[GroupName] = ['&:'.join([Sender,message])]    
        
    def savePicture(self, pic, pic_format, sender):
        file_name = ''.join([time.strftime("%Y%m%d%H%M%S",time.localtime()),
                            sender,'.',pic_format])
        pic_dir = os.path.abspath(self.current_dir + '/../../Data/picture')
        self.makedir(pic_dir)
        f=open(os.path.join(pic_dir,file_name),'wb')
        f.write(pic)
        f.close()
        return os.path.join('/Data/picture',file_name)

    def writeBuffer2File(self):
        timer = Timer(self.writeInterval,self.writeBuffer2File)
        timer.start()
        if self.msgBuffer:
            #write msg to files according to the sender and receiver
            #before write to files, call Encryptor to commit encryption
            encryptor = Encryptor()
            for key in self.msgBuffer:
                ## get the messages encrypted before saving to files
                msg_list = self.msgBuffer[key]
                messages = '&*'.join([msg for msg in msg_list])
                encrypted_msg = encryptor.EncryptStr(messages)
                ## use time to build the file saving path
                date = time.strftime("%Y%m%d",time.localtime())
                hour = time.strftime("%H",time.localtime())
                minute = time.strftime("%M",time.localtime())
                if '::' in key: ## this is a single chat msg
                    (sender,receiver) = key.split('::')
                    msg_dir = os.path.abspath(self.current_dir + '/../../Data/messages')
                    sender_path = os.path.join(msg_dir,sender,receiver,date,hour)
                    receiver_path = os.path.join(msg_dir,receiver,sender,date,hour)
                    self.makedir(sender_path)
                    self.makedir(receiver_path)
                    self.writeFile(os.path.join(sender_path,minute+'.bin'),encrypted_msg)
                    self.writeFile(os.path.join(receiver_path,minute+'.bin'),encrypted_msg)
                else: ## this is a group msg
                    group_name = key
                    msg_dir = os.path.abspath(self.current_dir + '/../../Data/Group messages')
                    group_path = os.path.join(msg_dir,group_name,date,hour)
                    self.makedir(group_path)
                    self.writeFile(os.path.join(group_path,minute+'.bin'),encrypted_msg)
            self.msgBuffer = dict()

    def makedir(self,target_dir):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

    def writeFile(self,target_path,content):
        output_file = open(target_path,'wb')
        output_file.write(content)
        output_file.close()

    def getMsgBuffer(self):
        return self.msgBuffer
