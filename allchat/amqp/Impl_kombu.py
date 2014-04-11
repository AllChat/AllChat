from kombu import Exchange, Connection, Consumer, Producer


class rpc(object):
    def __init__(self):
        self.exchange = None
        connection = None
        connection_pool = None
        queue = {}
        consumer = {}
        producer = {}

    def get_exchange(self):
        if self.exchange is None:
            pass
        else:
            return self.exchange

    def get_connection(self):
        pass

    def create_consumer(self):
        pass

    def release_consumer(self):
        pass

    def create_producer(self):
        pass

    def release_producer(self):
        pass

    def create_queue(self):
        pass

