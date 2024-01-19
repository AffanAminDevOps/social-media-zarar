import pandas as pd
from sqlalchemy import create_engine, Column,String, DateTime,LargeBinary,Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib import parse
from sqlalchemy.orm import relationship
from utility import *

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from config import *

Base = declarative_base()

class Ads(Base):
    __tablename__ = 'Advertisments'
    id=Column(Integer,primary_key=True,autoincrement=True)
    timestamp = Column(DateTime)
    top_left_coordinates = Column(String)
    bottom_right_coordinates = Column(String)
    position_relative_to_page = Column(String)
    position = Column(String)
    image = Column(LargeBinary)
    ad_name = Column(String)


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
