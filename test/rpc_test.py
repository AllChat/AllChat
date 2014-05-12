# -*- coding: utf-8 -*-

import os, sys

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(
        sys.argv[0]), os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "allchat", "__init__.py")):
    sys.path.insert(0, possible_topdir)
sys.path.insert(0, possible_topdir)

from allchat import amqp
from allchat.amqp.Impl_kombu import cast,RPC

class callback(object):
    def __init__(self):
        self.s = None
    def __call__(self, body, message):
        self.func(body, message)
    def func(self, body, message):
        print body
        message.ack()

def test(body, message):
    message.ack()

if __name__ == '__main__':
    #app.run(debug = True, use_debugger = False, use_reloader = False)
    amqp.init_rpc()
    conn = RPC.create_connection()
    pro = RPC.create_producer("pengdong", conn)
    # RPC.release_connection(conn)
    # RPC.release_producer("pengdong")
    RPC.register_callbacks("fang", [callback()])

    queue = RPC.create_queue("fang", "test")
    #conn = RPC.create_connection()
    com = RPC.create_consumer("fang", conn, queue)
    # cast(pro,"kakakakakakaka", "test")
    # cast(pro,"kakakakakakaka", "test")
    # cast(pro,"kakakakakakaka", "test")
    # cast(pro,"kakakakakakaka", "test")
    # cast(pro,"kakakakakakaka", "test")
    # cast(pro,"kakakakakakaka", "test")
    while True:
        msg = com.queues[0].get(no_ack = True)
        print msg.payload
    RPC.release_consumer("fang")

    RPC.extend_callbacks("fang", [test])
    com = RPC.create_consumer("fang", conn)
    RPC.release_consumer(com)
    RPC.release_connection(conn)

    RPC.del_queue("fang")

    print "over"


