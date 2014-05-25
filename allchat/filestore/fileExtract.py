# --*-- coding:utf-8 --*--
import win32com.client
import os

class FileExtract(object):
    def __init__(self):
        self.key = '0x1cd59c152bL'
        
    def getFileContent(self, startTime, endTime, option):
        ''' get the file content of required users in the specific time duration.
            option(dict) contains user/group information, 'type'=user/group;
            in case of user, there shall include 'chatFrom'=... and 'chatTo'=...
            in case of group, there shall include 'groupName'=...
            if no files can be found according to the params, returns None
        '''
        pass
        
    def decrypt(self, content): # key:密钥,content:密文 
        EncryptedData = win32com.client.Dispatch('CAPICOM.EncryptedData') 
        EncryptedData.Algorithm.KeyLength = 5 
        EncryptedData.Algorithm.Name = 2 
        EncryptedData.SetSecret(self.key) 
        EncryptedData.Decrypt(content) 
        str = EncryptedData.Content 
        return str 
