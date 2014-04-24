# -*- coding: utf-8 -*-
from flask import json
import Queue
class base(object):
    def __init__(self):
        super(base, self).__init__()
    def default(self, body, message):
        raise Exception("Can't find the responding callback method")

class rpc_callbacks(base):
    def __init__(self, maxsize = 10, timeout = 10):
        self.queue = Queue.Queue(maxsize)
        self.timeout = timeout
        super(rpc_callbacks, self).__init__()
    def __call__(self, body, message):
        body = json.loads(body)
        method = body['method']
        handle = getattr(self, method, self.default)
        try:
            return handle(body, message)
        except Exception,e:
            raise e

    def add_friend_req(self, body, message):
        para = body['para']
        user_from = para['from']
        msg = para['msg']
        tmp = dict()
        tmp['method'] = body['method']
        tmp['args'] = dict()
        tmp['args']['account'] = user_from
        tmp['args']['msg'] = msg
        try:
            self.queue.put(tmp, True, self.timeout)
        except Queue.Full,e:
            return None
        message.ack()

    def add_friend_resp(self, body, message):
        pass
    def send_individual_message(self, body, message):
        pass
    def send_group_message(self, body, message):
        pass
    def get_msg(self):
        try:
            tmp = self.queue.get(True, self.timeout)
        except Queue.Empty, e:
            return None
        self.queue.task_done()
        return tmp

