# -*- coding: utf-8 -*-

class Encryptor(object):
    def __init__(self, key):
        self._key = key
        self._key_length = len(hex(key).lstrip("0x").rstrip("L"))
        self._block_length = self._key_length

    def EncryptStr(self,string):
        import os
        salt = os.urandom(16).encode("hex")
        hex_str = string.encode("hex")
        blocks = len(hex_str)/self._block_length
        if len(hex_str)%self._block_length>0:
            blocks += 1
            hex_str = hex_str.zfill(blocks*self._block_length)
        return salt + "".join([hex(int(hex_str[i*self._block_length:(i+1)*self._block_length],16)^self._key^(int(salt,16))
            ).lstrip("0x").rstrip("L").zfill(self._key_length) for i in xrange(blocks)])

    def DecryptStr(self,string):
        salt = string[:32]
        string = string[32:]
        blocks = len(string)/self._key_length
        hex_str = "".join([hex(int(string[i*self._key_length:(i+1)*self._key_length],16)^self._key^(int(salt,16))
            ).lstrip("0x").rstrip("L").zfill(self._block_length) for i in xrange(blocks)])
        hex_str = hex_str.lstrip("0")
        return hex_str.decode("hex")