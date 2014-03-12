from allchat import app
from allchat.database.sql import get_session

def init_db():
    if app.config['DATABASE'].upper() == 'MYSQL':
        import MySQLdb
        origin_url = app.config['DATABASE_URL']
        url = app.config['DATABASE_URL']
        if url.startswith("mysql://"):
            url = url[8:]
        else:
            raise Exception('ERROR format in DATABASE_URL')
        tmp = url.split('/', 1)
        if(len(tmp) == 1):
            raise Exception('ERROR format in DATABASE_URL')
        other, db_name = tmp[0], tmp[1]
        tmp = other.split('@', 1)
        if(len(tmp) == 1):
            raise Exception('ERROR format in DATABASE_URL')
        account, address = tmp[0], tmp[1]
        tmp = account.split(':', 1)
        if(len(tmp) == 1):
            raise Exception('ERROR format in DATABASE_URL')
        user, password = tmp[0], tmp[1]
        tmp = address.split(':', 1)
        ip = tmp[0]
        try:
            port = tmp[1]
        except IndexError, e:
            port = 3306
        else:
            port = int(tmp[1])
        info = dict(host = ip, port = port, user = user, passwd = password)
        conn = MySQLdb.connect(host = info['host'], port = info['port'], user = info['user'], passwd = info['passwd'])
        cursor = conn.cursor()
        cursor.execute("create database if not exists %s" % (db_name,))
        conn.close()
        return get_session(origin_url)
    elif app.config['DATABASE'].upper() == 'SQLITE':
        pass
    else:
        pass
