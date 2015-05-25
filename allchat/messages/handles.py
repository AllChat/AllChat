# -*- coding: utf-8 -*-
from flask import json
try:
    import queue as Queue
except ImportError:
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
        except Exception as e:
            raise e

    def add_friend_req(self, body, message):
        para = body['para']
        user_from = para['from']
        msg = para['msg']
        tmp = dict()
        tmp['method'] = body['method']
        tmp['args'] = dict()
        tmp['args']['account'] = user_from
        tmp['args']['time'] = para['time']
        tmp['args']['msg'] = msg
        try:
            self.queue.put(tmp, True, self.timeout)
        except Queue.Full as e:
            message.reject()
            return None
        message.ack()

    def add_friend_resp(self, body, message):
        para = body['para']
        user_from = para['from']
        result = para['msg']
        if result == 'accept':
            pass
            # try:
            #     user = db_session.query(UserInfo).join(FriendList).with_lockmode('read').filter(and_(
            #             UserInfo.username == para['to'], UserInfo.deleted == False)).one()
            # except Exception as  e:
            #     message.ack()
            #     return None
            # for tmp in user.friends:
            #     if tmp == para['from']:
            #         tmp.confirmed = True
            #         db_session.begin()
            #         try:
            #             db_session.add(user)
            #             db_session.commit()
            #         except:
            #             db_session.rollback()
            #             message.ack()
            #             return None
        elif result == 'reject' or result == 'failed':
            pass
            # try:
            #     user = db_session.query(UserInfo).join(FriendList).with_lockmode('read').filter(and_(
            #             UserInfo.username == para['to'], UserInfo.deleted == False)).one()
            # except Exception as  e:
            #     message.ack()
            #     return None
            # for tmp in user.friends:
            #     if tmp == para['from']:
            #         db_session.begin()
            #         try:
            #             db_session.delete(tmp)
            #             db_session.commit()
            #         except:
            #             db_session.rollback()
            #             message.ack()
            #             return None
        else:
            message.reject()
            return None
        tmp = dict()
        tmp['method'] = body['method']
        tmp['args'] = dict()
        tmp['args']['account'] = user_from
        tmp['args']['time'] = para['time']
        tmp['args']['msg'] = result
        try:
            self.queue.put(tmp, True, self.timeout)
        except Queue.Full as e:
            message.reject()
            return None
        message.ack()

    def join_group_apply(self, body, message):
        para = body.get("para")
        account = para.get("applicant")
        group_id = para.get("groupid",0)
        tmp = dict()
        tmp["method"] = body.get("method")
        tmp["args"] = {"account":account, "group_id":group_id,
                        "time":para.get("time",""),"msg":para.get("msg","")}
        try:
            self.queue.put(tmp, True, self.timeout)
        except Queue.Full as  e:
            message.reject()
            return None
        message.ack()

    def join_group_confirm(self, body, message):
        para = body.get("para")
        tmp = dict()
        tmp["method"] = body.get("method")
        tmp["args"] = {"group_id":para.get("groupid"), "time":para.get("time",""),
                        "result":para.get("result","unkown")}
        try:
            self.queue.put(tmp, True, self.timeout)
        except Queue.Full as  e:
            message.reject()
            return None
        message.ack()

    def send_individual_message(self, body, message):
        para = body['para']
        user_from = para['from']
        msg = para['msg']
        tmp = dict()
        tmp['method'] = body['method']
        tmp['args'] = dict()
        tmp['args']['account'] = user_from
        tmp['args']['time'] = para['time']
        tmp['args']['msg'] = msg
        try:
            self.queue.put(tmp, True, self.timeout)
        except Queue.Full as e:
            message.reject()
            return None
        message.ack()

    def send_group_message(self, body, message):
        para = body['para']
        user_from = para['from']
        msg = para['msg']
        tmp = dict()
        tmp['method'] = body['method']
        tmp['args'] = dict()
        tmp['args']['account'] = user_from
        tmp['args']['group_id'] = para['group_id']
        tmp['args']['time'] = para['time']
        tmp['args']['msg'] = msg
        try:
            self.queue.put(tmp, True, self.timeout)
        except Queue.Full as e:
            message.reject()
            return None
        message.ack()

    def friendlist_update_status(self, body, message):
        para = body['para']
        user_from = para['from']
        msg = para['msg']
        tmp = dict()
        tmp['method'] = body['method']
        tmp['args'] = dict()
        tmp['args']['account'] = user_from
        tmp['args']['time'] = para['time']
        tmp['args']['msg'] = msg
        try:
            self.queue.put(tmp, True, self.timeout)
        except Queue.Full as e:
            message.reject()
            return None
        message.ack()

    def group_update_status(self, body, message):
        para = body['para']
        user_from = para['from']
        msg = para['msg']
        tmp = dict()
        tmp['method'] = body['method']
        tmp['args'] = dict()
        tmp['args']['account'] = user_from
        tmp['args']['group_id'] = para['group_id']
        tmp['args']['time'] = para['time']
        tmp['args']['msg'] = msg
        try:
            self.queue.put(tmp, True, self.timeout)
        except Queue.Full as e:
            message.reject()
            return None
        message.ack()

    def get_msg(self):
        try:
            tmp = self.queue.get(True, self.timeout)
        except Queue.Empty as e:
            return None
        self.queue.task_done()
        return tmp

    @property
    def empty(self):
        return self.queue.empty()

