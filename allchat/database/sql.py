from allchat.database.models import Base

db_session = None

def get_session(url, encode = "utf-8"):
    global db_session
    if url is not None:
        if db_session is None:
            engine = create_engine(url, encoding = encode, echo = False)
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            db_session = Session()
            return db_session
        else:
            return db_session
    else:
        raise Exception("DATABASE URL is None")
        
