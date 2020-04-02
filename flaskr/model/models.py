from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from sqlalchemy import (Column, ForeignKey,
                        Integer, String, DateTime, Text)
from .db import Base

def nowkor():
    return datetime.utcnow() + timedelta(hours=9)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    identifier = Column(String, unique=True)
    username   = Column(String)
    password   = Column(String)
    lastlogin  = Column(DateTime)
    currlogin  = Column(DateTime, default=nowkor)

    articles = relationship('Article', back_populates='publisher',
                            cascade='delete')

    def __repr__(self):
        return '#User<{}>'.format(self.identifier)

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(128))
    content = Column(Text)
    created = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))

    publisher = relationship('User', back_populates='articles')

    def __repr__(self):
        return '#article<\'{}\'>'.format(self.title)
    