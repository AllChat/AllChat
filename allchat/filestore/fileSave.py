# --*-- coding:utf-8 --*--
import time
import os
from threading import Timer
from encrypt import Encryptor

class FileSaver(object):
    def __init__(self):
        self.msgBuffer = dict()
        self.writeInterval = 900.0 
        self.writeBuffer2File()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
    def saveMessage(self, Sender, Receiver, msgDict):
        message = '\r\n'.join(['\t'.join((time,msgDict[time])) for time in msgDict])
        if '::'.join([Sender,Receiver]) in self.msgBuffer:
            self.msgBuffer['::'.join([Sender,Receiver])].append({Sender:message})
        elif '::'.join([Receiver,Sender]) in self.msgBuffer:
            self.msgBuffer['::'.join([Receiver,Sender])].append({Sender:message})
        else:
            self.msgBuffer['::'.join([Sender,Receiver])] = [{Sender:message}]
        
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
                (sender,receiver) = key.split('::')
                msg_list = self.msgBuffer[key]
                messages = '&*'.join(['&:'.join(msg.keys()+msg.values())
                                    for msg in msg_list])
                encrypted_msg = encryptor.EncryptStr(messages)
                msg_dir = os.path.abspath(self.current_dir + '/../../Data/messages')
                self.makedir(msg_dir)
                date = time.strftime("%Y%m%d%H%M",time.localtime())
                sender_path = os.path.join(msg_dir,sender,receiver,date)
                receiver_path = os.path.join(msg_dir,receiver,sender,date)
                self.makedir(sender_path)
                self.makedir(receiver_path)
                self.writeFile(sender_path,encrypted_msg)
                self.writeFile(receiver_path,encrypted_msg)
            self.msgBuffer = dict()

    def makedir(self,target_dir):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

    def writeFile(self,target_path,content):
        output_file = open(os.path.join(target_path,'chat.bin'),'wb')
        output_file.write(content)
        output_file.close()
