from .facebook_crawler import *
from bs4 import BeautifulSoup
import datetime as d
from urllib import parse
from .utils import *
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BOOLEAN, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import inspect
import json
from ...models import *
Base = declarative_base()


class Facebook(Base):
    __tablename__ = 'keywords'
    id = Column(Integer,primary_key=True,autoincrement=True)
    account = Column(String)
    post = Column(String)
    reactions = Column(String)
    shares = Column(String)
    comments = Column(String)
    type = Column(String)
    upload_time = Column(String)
    shared = Column(String)
    thumbnail_link = Column(String)
    keyword = Column(String)
    link=Column(String)

class DatabaseFB:
    def __init__(self) -> None:
        self.database_url = 'postgresql://postgres:{password}@localhost/{db}'.format(
            password=parse.quote('ticker@1234'),
            db='Facebook')
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

    def add_data_to_db(self,data,session):
        existing_data = session.query(Facebook).filter(Facebook.post == data['Post']).first()
        if existing_data is None:
            fb_object = Facebook(
                account=None,
                post=data["Post"],
                reactions=data["Reactions"],
                shares=data["Shares"],
                comments=data["Comments"],
                type=data["Type"],
                upload_time=data["Upload Time"],
                shared=data["Shared"],
                thumbnail_link=data["Thumbnail Link"],
                keyword=data['keyword'],
                link=data['link'])
            try:
                session.add(fb_object)
                session.commit()
                print(data["Post"])
                print("ADDED data to DB")
            except Exception as e:
                session.rollback()
                print(e)
        else:
            try:
                print("Data Already Exists")
                if (
                        existing_data.shares != data["Shares"] or
                        existing_data.comments != data["Comments"] or
                        existing_data.reactions != data["Reactions"]
                ):
                    existing_data.shares = data["Shares"]
                    existing_data.comments = data["Comments"]
                    existing_data.reactions = data["Reactions"]
                print(data["Post"])
                print("UPDATED data in DB")
                session.commit()
            except Exception as e:
                session.rollback()
                print(e)

def add_data_to_database(data):
    photo_data= None
    if data["Thumbnail Link"] != None and data['Type'] =='photo':
        # Read and convert the image file to bytes
        print("Photo: ", data["Thumbnail Link"])
        photo_path = download_image(data["Thumbnail Link"])
    try:
        if facebook_post.objects.filter(post=data['Post']).first():
            print("Post Already Exists")
        else:
            fb_post=facebook_post(
                post=data['Post'],
                reactions=data['Reactions'],
                shares=data['Shares'],
                comments=data['Comments'],
                type=data['Type'],
                upload_time=data['Upload Time'],
                shared=data['Shared'],
                thumbnail_link=photo_path,
                keyword=data['keyword'],
                link=data['link'],
                last_scraped=datetime.now()
            )
            fb_post.save()
            print("Post saved")
        
    except:
        print("Post Not saved")


def get_posts(driver, last_posts,keyword):
    # db=DatabaseFB()
    # session=db.create_session()
    for post_number in range(1, last_posts + 1):
        scroll_post(driver)
        time.sleep(2)
        div_elements = driver.find_elements(By.XPATH, f"//div[@aria-posinset='{post_number}']")
        print("Post Number: ", post_number)
        for div_element in div_elements:
            try:
                # tag_name = div_element.tag_name
                text = div_element.text
                attributes = div_element.get_attribute("outerHTML")
                photo = False
                soup = BeautifulSoup(attributes, 'html.parser')
                img_tags = soup.find_all('img')
                print('links')
#                 'https://www.facebook.com/watch/live/?ref=watch_permalink&v=1041087500468043'
#                 '''https://www.facebook.com/photo/?fbid=1162543468039470&set=a.101289734164854&__
# cft__[0]=AZVFQCtwPaqymJq8AjvEmvSOT3ifj8szr15L_D6Yn5PBwleEUvA4mobP0BylLga4cvgLpfqplIiu05_0bIRwfBTiH80C6LZL7U8U7cY5VU3zBLQlv0sTmB9H7NO0v0mTr8gpW2RgXY65Sp6fAYW1vka_XIROGIs7wXCrLGWTKv9xrAXr6ebOSuJWCbC2G0BhE4I&__tn
# __=EH-R'''
#                 '''https://www.facebook.com/watch/live/?ref=watch_permalink&v=1041087500468043'''
                target_keywords = ['live', 'photo', 'video']
                filtered_links = [a['href'] for a in soup.find_all('a', href=True) if any(keyword in a['href'] for keyword in target_keywords)]
                print(filtered_links[-1])

                for img_tag in img_tags:
                    src_value = img_tag.get('src')
                    if "scontent" in src_value:
                        photo = True
                        break
                post_link = ""            
                if photo:
                    data = get_features(text.strip(), link=src_value)
                    print(data)
                    if data:
                        if filtered_links:
                            data['keyword']=keyword
                            data['link']=filtered_links[-1]
                            add_data_to_database(data)
                        else:
                            data['keyword']=keyword
                            data['link']=None
                            add_data_to_database(data)
                    else:
                        pass
                else:
                    data = get_features(text.strip())
                    if data:
                        if filtered_links:
                            data['keyword']=keyword
                            data['link']=filtered_links[-1]
                            add_data_to_database(data)
                        else:
                            data['keyword']=keyword
                            data['link']=None
                            add_data_to_database(data)
                    else:
                        pass
                print("---"*30)
            except Exception as e:
                print(e)

    # driver.quit()


def keyword_crawling(keywords=None):
    driver = open_profile('fb profile')
    driver.get('https://www.facebook.com/')
    check_login(driver)
    time.sleep(10)
    if keywords is not None:
        driver.get(f"https://www.facebook.com/search/top?q={keywords}")
        time.sleep(5)
        get_posts(driver, 25,keywords)
    else:
        all_keywords = list(keyword.objects.values_list('keywords', flat=True))
        all_facebook_crawl = list(keyword.objects.values_list('facebook_crawl', flat=True))
        facebook_profiles=[]
        for index in range(len(all_keywords)):
            if all_facebook_crawl[index]==True:
                facebook_profiles.append(all_keywords[index])
        for profile in facebook_profiles:
            try:
                print("Profile: ", profile)
                driver.get(f"https://www.facebook.com/search/top?q={profile}")
                time.sleep(5)
                get_posts(driver, 25,profile)
            except Exception as e:
                print(e)
    driver.quit()      

# The code `if __name__ == "__main__":` is a common Python idiom that allows a module to be run as a
# standalone script or imported by other modules.

# if __name__ == "__main__":
#     main("Imran khan")
