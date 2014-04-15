# -*- coding: utf-8 -*- 
class base(object):
    def __init__(self):
        pass
    def default(self, body, message):
        raise Exception("Can't find the responding callback method")

class rpc_callbacks(base):
    def __init__(self):
        pass
    def __call__(self, body, message):
        pass