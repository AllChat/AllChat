from allchat.database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.databases import mysql

db_session = None

def get_session(url = None, encode = "utf-8", echo = True):
    global db_session
    if url is not None:
        if db_session is None:
            engine = create_engine(url, encoding = encode, echo = echo)
            db_session = scoped_session(sessionmaker(bind=engine))
            Base.query = db_session.query_property()
            Base.metadata.create_all(bind=engine)
            return db_session
        else:
            return db_session
    else:
        if(db_session is not None):
            return db_session
        else:
            raise Exception("DATABASE URL is None")
