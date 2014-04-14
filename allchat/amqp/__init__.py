from allchat import app
from allchat.amqp.Impl_kombu import RPC

def init_rpc():
    url = app.config['RPC_URL']
    exchange_name = app.config['RPC_EXCHANGE']
    str = "^amqp://([\w:@]+)$"
    import re
    tmp = re.match(str, url)
    if tmp is None:
        raise Exception("Please configure an available RPC_URL, \
                        the correct pattern is 'amqp://user:password@address:port//'")
    try:
        host = tmp.group(1)
    except IndexError,e:
        raise e
    account, address = host.split('@', 1)
    if not any(account, address):
        raise Exception("Please configure an available RPC_URL, \
                        the correct pattern is 'amqp://user:password@address:port//'")
    if len(account.split(":", 1)) != 2 or len(address.split(":", 1)) != 2:
        raise Exception("Please configure an available RPC_URL, \
                        the correct pattern is 'amqp://user:password@address:port//'")
    try:
        RPC.init_connection(url)
    except Exception,e:
        raise e

    RPC.init_exchange(exchange_name)


