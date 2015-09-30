import os
import sys
import eventlet
import eventlet.wsgi
import socket
import greenlet
from multiprocessing import Pool, cpu_count
# from twisted.web.wsgi import WSGIResource
# from twisted.internet import reactor
# from twisted.web.server import Site

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(
        sys.argv[0]), os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "allchat", "__init__.py")):
    sys.path.insert(0, possible_topdir)
# sys.path.insert(0, possible_topdir)


from allchat import app, init

class worker(object):
    def __init__(self, application, host="0.0.0.0", port=8000, size=1024, use_ssl=False):
        self.app = application
        self.host = host
        self.port = port
        self.size = size
        self.use_ssl = use_ssl
        self.pool = eventlet.GreenPool(size)
        self.sock = eventlet.listen((host, port))
    def __call__(self):
        eventlet.hubs.use_hub()
        if self.use_ssl:
            pass
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # sockets can hang around forever without keepalive
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        wsgi_kwargs = {
            'func': eventlet.wsgi.server,
            'sock': self.sock,
            'site': self.app,
            'custom_pool': self.pool
        }
        server = eventlet.spawn(**wsgi_kwargs)
        try:
            server.wait()
        except greenlet.GreenletExit:
            pass

if __name__ == '__main__':
    if '--debug' in sys.argv:
        app.debug = True
    init()
    wrap = []
    work = worker(app)
    # pool = Pool(cpu_count())
    # pool.map(worker, [])
    # pool.close()
    # pool.join()
    # for i in range(0,4):
    #     pid = os.fork()
    #     if pid == 0:
    #         work()
    #     wrap.append(pid)
    # while True:
    #     try:
    #         pid, status = os.wait()
    #     except:
    #         pass
    #     finally:
    #         if pid in wrap:
    #             wrap.remove(pid)
    work()
    # app.run(debug = True, use_debugger = False, use_reloader = False)
    # pool = reactor.getThreadPool()
    # pool.start()
    # resource = WSGIResource(reactor, pool, app)
    # reactor.listenTCP(8080, Site(resource))
    # reactor.run()
