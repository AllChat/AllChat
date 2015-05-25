# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
import sys

class Encryptor(object):
    def __init__(self, key, IV):
        self.key = key
        self.IV = IV
        self.blocksize = 16

    def EncryptStr(self,content):
        if sys.version_info.major == 2:
            content = content.encode("utf-8")
        elif sys.version_info.major == 3:
            content = bytes(content,"utf-8")
        while len(content)%self.blocksize != 0:
            content += b"\0"
        obj = AES.new(self.key,AES.MODE_CBC,self.IV)
        return obj.encrypt(content)

    def DecryptStr(self,content):
        obj = AES.new(self.key,AES.MODE_CBC,self.IV)
        content = obj.decrypt(content).strip(b"\0")
        return content.decode("utf-8")
