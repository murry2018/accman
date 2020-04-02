from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

default_db = 'sqlite:///:memory:'

engine = None

Session = sessionmaker(autocommit=False, autoflush=False)
session = scoped_session(Session)

Base = declarative_base()
Base.query = session.query_property()

def init_db(database_url=default_db):
    global engine, Session
    import flaskr.model.models
    engine = create_engine(database_url)
    Session.configure(bind=engine)
    Base.metadata.create_all(bind=engine)
