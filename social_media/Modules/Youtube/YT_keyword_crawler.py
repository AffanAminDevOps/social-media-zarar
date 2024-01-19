from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import json
from bs4 import BeautifulSoup
import time
from datetime import datetime,timedelta
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# from database_youtube import DatabaseYT
import pandas as pd


videos=[]

def get_details_videos(content):
    if content is not None:
        data = {
            'views_count': None,
        }
        data['title'] = content.find('a', {'id': 'video-title'})['title']
        data['link'] = "https://www.youtube.com/"+content.find('a', {'id': 'video-title'})['href']
        # Find all spans with the specified class
        metadata_items = content.find_all('span', {'class': 'inline-metadata-item style-scope ytd-video-meta-block'})

        # Loop through metadata items
        for item in metadata_items:
            text = item.text.strip()

            # Check if 'views' is present in text
            if 'views' in text:
                data['views_count'] = text
            else:
                # Assuming the remaining item is the upload date
                data['upload_date'] = convert_time_ago(str(text))
                print(data['upload_date'])
                break
        channel = content.find("ytd-channel-name", {"id": "channel-name"})
        name = channel.find('yt-formatted-string')
        try:
            duration = content.find('div', {'id': 'time-status',
                                            'class': 'style-scope ytd-thumbnail-overlay-time-status-renderer'})
            data["video_duration"] = \
            duration.find('span', {'id': 'text', 'class': 'style-scope ytd-thumbnail-overlay-time-status-renderer'})[
                'aria-label']
        except:
            data["video_duration"] = None

        channel_name = name.find('a')['href']
        data['channel_name'] = channel_name[2:]
        try:
            img = content.find('yt-image', class_='style-scope ytd-thumbnail')
            img = img.find('img')['src']
            data["image"] = img

        except:
            data["image"] = None
        return data
def convert_time_ago(time_ago):
    # Split the input string into words
    words = time_ago.split()
    print(words)
    # Get the numeric value and the unit
    try:
        if "Streamed" in words:
            value, unit = int(words[1]), words[2].lower()
        else:
            value, unit = int(words[0]), words[1].lower()

        # Define the mapping of units to timedelta
        unit_to_timedelta = {
            'year': timedelta(days=365),
            'years': timedelta(days=365),
            'month': timedelta(days=30),
            'months': timedelta(days=30),
            'week': timedelta(weeks=1),
            'weeks': timedelta(weeks=1),
            'day': timedelta(days=1),
            'days': timedelta(days=1),
            'hour': timedelta(hours=1),
            'hours': timedelta(hours=1),
            'minute': timedelta(minutes=1),
            'minutes': timedelta(minutes=1),
            'second': timedelta(seconds=1),
            'seconds': timedelta(seconds=1),
        }

        # Multiply the numeric value with the corresponding timedelta
        
        delta = value * unit_to_timedelta.get(unit, timedelta(seconds=0))

        # Calculate the datetime by subtracting the delta from the current time
        result_datetime = datetime.now() - delta

        return result_datetime
    except:
        return None

def extract_data(html_content, keyword):
    # data_base = DatabaseYT()
    # session=data_base.create_session()
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the div with id="contents"
    contents_div = soup.find_all('div', {"id": "contents"})
    items = []
    for data in contents_div:
        contents = data.find_all('ytd-video-renderer')
        for content in contents:
            data = get_details_videos(content)
            items.append(data)
            data['keyword'] = keyword
            # data_base.add_data_to_db_video(data,session)
            videos.append(data)
            print(data)
            print('=----' * 20)


def channel_crawler_keyword(keyword):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Firefox(options=chrome_options)
    driver.get(f'https://www.youtube.com/results?search_query={keyword}')
    i = 0
    for i in range(5):
        print('scroll no', i)
        old_page = driver.page_source
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)
        new_page = driver.page_source
        html_content = new_page
        extract_data(html_content, keyword)
        if "No more results" in new_page:
            break
        if old_page == new_page:
            break
    driver.close()

def main(keyword=None):
    start_time = time.time()
    channel_crawler_keyword(keyword)
    df=pd.DataFrame(videos)
    df_unique=df.drop_duplicates(subset='link',keep='last')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(df_unique)
    return df_unique


def youtube_keyword_crawler(keyword):
    videos_df=main(keyword)
    return videos_df

# youtube_keyword_crawler("")
