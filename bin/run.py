import os
import sys
#from twisted.web.wsgi import WSGIResource
#from twisted.internet import reactor
#from twisted.web.server import Site

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(
        sys.argv[0]), os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "allchat", "__init__.py")):
    sys.path.insert(0, possible_topdir)
sys.path.insert(0, possible_topdir)


from allchat import app


if __name__ == '__main__':
    app.run(debug = True, use_debugger = False, use_reloader = False)
#    pool = reactor.getThreadPool()
#    pool.start()
#    resource = WSGIResource(reactor, pool, app)
#    reactor.listenTCP(5000, Site(resource))
#    reactor.run()
