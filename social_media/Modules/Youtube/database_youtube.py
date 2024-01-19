import datetime as d
from urllib import parse

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import inspect
import json
import re

Base = declarative_base()


def extract_numbers(input_string):
    # Use regular expression to find all numeric characters
    numbers = re.findall(r'\d+', input_string)
    numbers=[]
    return ''.join(numbers)


class Youtube(Base):
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


class YouTubeVideo(Base):
    __tablename__ = 'youtube_video_details'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    video_duration = Column(String)
    views_count = Column(String)
    link = Column(String)
    image = Column(String)
    channel_name = Column(String)
    keyword = Column(String)
    upload_date = Column(DateTime)
    last_scraped_video = Column(DateTime)


class DatabaseYT:
    def __init__(self) -> None:
        self.database_url = 'postgresql://postgres:{password}@localhost/{db}'.format(
            password=parse.quote('ticker@1234'),
            db='Youtube')
        self.engine = create_engine(self.database_url)
        self.conn = self.engine.connect()
        self.create_tables(Base)

    def create_tables(self, base):
        inspector = inspect(self.engine)
        for table in Base.metadata.tables.values():
            if not inspector.has_table(table.name):
                base.metadata.create_all(self.engine)
                print(f"Table '{table.name}' created")

    def create_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def add_data_to_db_channel(self, data, session):
        existing_data = session.query(Youtube).filter(
            Youtube.channel_name == data['channel_name']).first()
        if existing_data is None:
            youtube = Youtube(
                description=data['description'],
                email=data['details']['email'],
                url=data['details']['url'],
                subscriber_count=data['details']['subscriber_count'],
                videos_count=extract_numbers(data['details']['videos_count']),
                views=extract_numbers(data['details']['views']),
                join_date=data['details']['join_date'],
                country=data['details']['country'],
                channel_name=data['channel_name'],
                last_scraped_user=d.datetime.now()

            )
            youtube.set_links(data['links'])
            session.add(youtube)
            session.commit()
            print(data['channel_name'])
            print("Added data to db")
        else:
            print("Data Already exists")

    def add_data_to_db_video(self, data, session):
        existing_data = session.query(YouTubeVideo).filter(
            YouTubeVideo.link == data['link']).first()
        if existing_data is None:
            video_instance = YouTubeVideo(
                title=data['title'],
                video_duration=data['video_duration'],
                views_count=data['views_count'],
                link=data['link'],
                image=data['image'],
                channel_name=data['channel_name'],
                keyword=data['keyword'],
                upload_date=data['upload_date'],
                last_scraped_video=d.datetime.now()
            )
            session.add(video_instance)
            session.commit()
            print(data['title'])
            print("Added data to db")
            return True
        else:
            print("Data Already exists")
            return False
