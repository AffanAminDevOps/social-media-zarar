from sqlalchemy import create_engine, Column, Integer, String, DateTime, ARRAY, BigInteger, ForeignKey, LargeBinary
from urllib import parse
from utility import *
from sqlalchemy.orm import sessionmaker, declarative_base
from config import *
import json
import datetime as d

Base4 = declarative_base()


class Youtube(Base4):
    __tablename__ = 'youtube_channel_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String)
    links = Column(String)  # Store links as a JSON string
    email = Column(String)
    url = Column(String)
    subscriber_count = Column(String)
    videos_count = Column(String)
    views = Column(String)
    join_date = Column(String)
    country = Column(String)
    channel_name = Column(String)
    last_scraped_user = Column(DateTime)

    def set_links(self, links_dict):
        self.links = json.dumps(links_dict)

    def get_links(self):
        return json.loads(self.links)


class YouTubeVideo(Base4):
    __tablename__ = 'youtube_video_details'
    id = Column(Integer, primary_key=True)
    video_title = Column(String)
    video_duration = Column(String)
    views_count = Column(String)
    link = Column(String)
    image = Column(String)
    channel_name = Column(String)
    keyword = Column(String)
    last_scraped_video = Column(DateTime)


class Database():
    def __init__(self) -> None:
        self.database_url = 'postgresql://postgres:{password}@localhost/{db}'.format(password=parse.quote(password),
                                                                                     db=db4)
        self.engine = create_engine(self.database_url)
        self.conn = self.engine.connect()
        Base4.metadata.create_all(self.engine)

    def create_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session
