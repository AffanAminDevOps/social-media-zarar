import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ARRAY, BigInteger, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib import parse
from sqlalchemy.orm import relationship
from .utility import *
import psycopg2
import sqlalchemy

Base = declarative_base()
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .config import *
import json
from .utility import download_file

Base = declarative_base()


class News(Base):
    __tablename__ = 'News'
    title = Column(String)
    description = Column(String)
    link = Column(String, primary_key=True)
    image = Column(String)
    platform = Column(String)
    news_creation_date = Column(DateTime)
    image_data = Column(LargeBinary)

    def serialize(self):
        return {
            'title': self.Title,
            'description': self.Description,
            'platform': self.Platform,
            'news_creation_date': str(self.News_creation_date),
            'image': self.Media,
            'link': self.Link,
            'image_data': str(self.Media_data)
        }


class Database:
    def __init__(self) -> None:
        self.database_url = 'postgresql://postgres:{password}@localhost/{db}'.format(password=parse.quote(password),
                                                                                     db=db)
        self.engine = create_engine(self.database_url)
        self.conn = self.engine.connect()
        Base.metadata.create_all(self.engine)

    def create_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session
