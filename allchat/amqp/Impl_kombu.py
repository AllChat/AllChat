# -*- coding: utf-8 -*-
from kombu import Exchange, Connection, Consumer, Producer,Queue
from flask import json
#import time
from eventlet import sleep
import allchat
from allchat import user_states
from allchat.messages.handles import rpc_callbacks

class rpc(object):
    def __init__(self):
        self.exchange = None
        self.connection = None
        self.connection_pool = None
        self.queue = {}
        self.consumer = {}
        self.producer = {}
        self.callbacks = {}

    def init_exchange(self, name = 'AllChat', type = 'direct', channel = None, durable = True, delivery_mode = 2):
        if self.exchange is None:
            self.exchange = Exchange(name, type, channel = channel, durable = durable, delivery_mode = delivery_mode)
        return self.exchange

    def init_connection(self,url,ssl = False):
        if self.connection is None:
            self.connection = Connection(url, ssl = ssl)
            try:
                self.connection.connect()
            except Exception as e:
                raise e
            else:
                self.connection.close()
        return self.connection

    def get_exchange(self):
        if self.exchange is None:
            raise Exception("No exchange. Please invoke init_exchange firstly")
        else:
            return self.exchange

    def create_connection(self):
        if self.connection_pool is None:
            self.connection_pool = self.connection.Pool(allchat.app.config['RPC_POOL_NUM'])
        return self.connection_pool.acquire()

    def release_connection(self, conn):
        try:
            if conn is not None:
                conn.release()
        except Exception as e:
            raise e

    def close_connection(self, conn):
        try:
            if conn is not None:
                conn.close()
        except Exception as e:
            raise e

    # def create_channel(self, conn):
    #     if conn is not None:
    #         return conn.channel()
    #     else:
    #         return None
    #
    # def release_channel(self, channel):
    #     try:
    #         if channel is not None:
    #             channel.close()
    #     except Exception as e:
    #         raise e

    # def create_consumer(self, name, channel , queues = None, callbacks = None):
    #     if name in self.consumer:
    #         self.consumer[name].revive(channel)
    #     else:
    #         if not any([queues, callbacks]):
    #             raise Exception("queues and callbacks can't be None")
    #         if isinstance(callbacks, list):
    #             self.consumer[name] = Consumer(channel, queues, callbacks)
    #         else:
    #             self.consumer[name] = Consumer(channel, queues)
    #             self.consumer[name].register_callback(callbacks)
    #     self.consumer[name].consume()
    #     return self.consumer[name]

    def create_consumer(self, name, channel, queues = None):
        if name in self.consumer:
            try:
                if self.callbacks[name] != self.consumer[name].callbacks:
                    self.consumer[name].callbacks = self.callbacks[name]
            except KeyError as e:
                raise Exception("Please invoke register_callbacks before")
            self.consumer[name].revive(channel)
        else:
            if not queues:
                queues = self.create_queue(name, name)
            try:
                self.callbacks[name]
            except KeyError as e:
                self.register_callbacks(name, [rpc_callbacks()])
                #raise Exception("Please invoke register_callbacks before")
            finally:
                self.consumer[name] = Consumer(channel, queues, callbacks = self.callbacks[name])
        #self.consumer[name].consume()
        return self.consumer[name]

    def release_consumer(self, name):
        try:
            if name in self.consumer:
                self.consumer[name].cancel()
        except Exception as e:
            raise e

    def create_producer(self, name, channel):
        if name in self.producer:
            self.producer[name].revive(channel)
        else:
            self.producer[name] = Producer(channel, self.get_exchange())
        return self.producer[name]

    def release_producer(self, name):
        try:
            if name in self.producer:
                self.producer[name].close()
        except Exception as e:
            raise e

    def create_queue(self, name, routing_key, durable = True):
        if name not in self.queue:
            self.queue[name] = Queue(name, self.get_exchange(), routing_key, durable = durable)
        return self.queue[name]

    def del_queue(self, name):
        try:
            if name in self.callbacks:
                del self.callbacks[name]
            if name in self.consumer:
                try:
                    self.consumer[name].close()
                except Exception as e:
                    pass
                del self.consumer[name]
            if name in self.producer:
                try:
                    self.producer[name].close()
                except Exception as e:
                    pass
                del self.producer[name]
            if name in self.queue:
                tmp = self.create_connection() #Kombu中删除Queue，必须保证Queue是绑定在一个channel上的，否则删除失败
                self.queue[name].maybe_bind(tmp)
                self.queue[name].delete()
                self.close_connection(tmp)
                del self.queue[name]
        except Exception as e:
            raise e

    def register_callbacks(self, name, callbacks):
        if isinstance(callbacks, list):
            self.callbacks[name] = callbacks
        else:
            raise Exception("The parameter callbacks should be a list")

    def extend_callbacks(self, name, callbacks):
        if isinstance(callbacks, list):
            if name in self.callbacks:
                self.callbacks[name].extend(callbacks)
            else:
                raise Exception("The {account} callbacks don't exist".format(account = name))
        else:
            raise Exception("The parameter callbacks should be a list")

def cast(producer, message, routing_key, delivery_mode = 2):
    try:
        producer.publish(message, routing_key, delivery_mode)
    except Exception as e:
        raise e

def send_message(req_user, resp_user, message):
    cnn = RPC.create_connection()
    sender = RPC.create_producer(req_user, cnn)
    try:
        cast(sender, json.dumps(message), resp_user)
    except:
        return ("Send message failed due to system error", 500)
    finally:
        RPC.release_producer(req_user)
        RPC.release_connection(cnn)
    return None

def receive_message(user, timeout = 240):
    queue = RPC.create_queue(user, user)
    conn = RPC.create_connection()
    consumer = RPC.create_consumer(user, conn, queue)
    if not consumer.callbacks[0].empty: #若回调函数消息队列非空，则直接从队列中获取消息
        state = user_states.get(user)
        if state is None or state == "offline":
            msg = None
        else:
            msg = consumer.callbacks[0].get_msg()
        RPC.release_connection(conn)
        RPC.release_consumer(user)
        return msg
    SLEEP_INTERVAL = 5
    waited = 0
    while waited < timeout:
        sleep(SLEEP_INTERVAL)
        waited += SLEEP_INTERVAL
        state = user_states.get(user)
        if state is None or state == "offline":
            break
        #conn.drain_events(timeout = timeout)
        msg = consumer.queues[0].get()
        if msg:
            break
    if msg:
        consumer.receive(msg.payload, msg)
        msg = consumer.callbacks[0].get_msg()
    else:
        msg = None
    RPC.release_connection(conn)
    RPC.release_consumer(user)
    return msg


RPC = rpc()