# -*- coding: utf-8 -*-
class Encryptor(object):
    def __init__(self):
        self.key = 3881916286L
        
    def int2hexStr(self,integer):
        string = hex(integer)[2:-1]
        while len(string)<8:
            string = '0'+string
        array = [string[i*2:i*2+2].decode('hex')
                        for i in range(4)]
        return ''.join(array)

    def hexStr2int(self,string):
        s_array = [x.encode('hex') for x in string]
        s = ''.join(s_array)
        return int(s,16)

    def intEcrypt(self,integer):
        return integer^self.key

    def EncryptStr(self,string):
        if isinstance(string,unicode):
            string = string.encode('utf-8')
        while len(string)%4>0:
            string += '\x00'
        encryptedStr = ''
        index = 0
        while index<len(string):
            sliceStr = string[index:index+4]
            encryptedStr += self.int2hexStr(self.intEcrypt(
                self.hexStr2int(sliceStr)))
            index += 4
        return encryptedStr

    def DecryptStr(self,string):
        decryptedStr = ''
        index = 0
        while index<len(string):
            sliceStr = string[index:index+4]
            decryptedStr += self.int2hexStr(self.intEcrypt(
                self.hexStr2int(sliceStr)))
            index += 4
        while decryptedStr[-1]=='\x00':
            decryptedStr = decryptedStr[:-1]
        return decryptedStr
