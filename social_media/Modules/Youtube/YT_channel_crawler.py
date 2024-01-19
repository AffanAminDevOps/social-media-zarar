from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
# from database_youtube import *
from datetime import datetime, timedelta
import pandas as pd
import re

user=[]
videos=[]

def convert_time_ago(time_ago):
    # Split the input string into words
    words = time_ago.split()

    # Get the numeric value and the unit
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
    delta = value * unit_to_timedelta[unit]

    # Calculate the datetime by subtracting the delta from the current time
    result_datetime = datetime.now() - delta

    return result_datetime


def extract_data(html_content, name):
    # data_base = DatabaseYT()
    # session = data_base.create_session()
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the div with id="contents"
    contents_div = soup.find('div', {'id': 'contents', 'class': 'style-scope ytd-rich-grid-renderer'})

    if contents_div:
        contents = contents_div.find_all('div', {'id': 'content'})
        data = []
        for content in contents:
            items = get_details_videos(content)
            items['channel_name'] = name
            items['keyword'] = None
            videos.append(items)
            # data_base.add_data_to_db_video(items, session)
        return data





    else:
        print("Div with id='contents' not found on the page.")


def get_details_videos(content):
    if content is not None:
        data = {}
        div = content.find_all('span', class_='inline-metadata-item style-scope ytd-video-meta-block')
        data["title"] = content.find('yt-formatted-string', {'id': 'video-title'}).text.strip()
        data["video_duration"] = content.find('span', {'id': 'text'}).text.strip()
        data["views_count"] = div[0].text.strip()
        data["link"] = 'https://www.youtube.com/' + content.find('a', {'id': 'video-title-link'})['href']
        data['upload_date'] = convert_time_ago(div[1].text.strip())
        try:
            img = content.find('yt-image', class_='style-scope ytd-thumbnail')
            img = img.find('img')['src']
            data["image"] = img

        except:
            data["image"] = None
        return data


def get_links(element):
    soup = BeautifulSoup(element, 'html.parser')
    link_list_container = soup.find('div', {'id': 'link-list-container'})
    links_dict = {}
    link_elements = link_list_container.find_all('yt-channel-external-link-view-model')
    for link_element in link_elements:
        title = link_element.find('span', {'class': 'yt-channel-external-link-view-model-wiz__title'}).text.strip()
        url = link_element.find('a', {'class': 'yt-core-attributed-string__link'}).text
        links_dict[title] = url

    return links_dict


def get_details(element):
    details = {}
    soup = BeautifulSoup(element, 'html.parser')
    all_data = soup.find_all('td', {'class': 'style-scope ytd-about-channel-renderer'})
    data = [i.text.strip() for i in all_data if len(i.text.strip()) != 0]
    try:
        details['email'], details['url'], details["subscriber_count"], details['videos_count'], details['views'], details[
            "join_date"], details['country'] = data
        return details
    except:
        details = {}
        details['url']=None
        details['subscriber_count']=None
        details['videos_count']=None
        details['views']=None
        details['join_date']=None
        details['country']=None
        
        patterns = {
            'url': re.compile(r'https?://www\.youtube\.com/.*'),
            'subscriber_count': re.compile(r'\d+\.?\d*M?\s+subscribers'),
            'videos_count': re.compile(r'\d+\s+videos'),
            'views': re.compile(r'\d+,?\d+\,?\d+\s+views'),
            'join_date': re.compile(r'Joined\s+\w+\s+\d+,\s+\d{4}'),
        }

        for i, item in enumerate(data):
            if item:
                for key, pattern in patterns.items():
                    if pattern.match(item):
                        details[key] = item
                        data[i] = None  # Mark as processed to avoid duplicate matches
                        break

        # Handle remaining values using the original logic
        try:
            details['url'] = next(value for value in data if value)
        except StopIteration:
            details['url'] = None
        try:
            details['country'] = next(value for value in data if value)
        except StopIteration:
            details['country'] = None
        
        # try:
        #     details['email']=data[0]
        # except:
        #     details['email']=None
        # try:
        #     details['url']=data[1]
        # except:
        #     details['url']=None
        # try:
        #     details['subscriber_count']=data[2]
        # except:
        #     details['subscriber_count']=None
        # try:
        #     details['videos_count']=data[3]
        # except:
        #     details['videos_count']=None
        # try:
        #     details['views']=data[4]
        # except:
        #     details['views']=None
        # try:
        #     details['join_date']=data[5]
        # except:
        #     details['join_date']=None
        # try:
        #     details['country']=data[6]
        # except:
        #     details['country']=None
        print("details", details)
        return details


def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def channel_crawler_youtube(name,scrape_all_videos=False):
    # data_base = DatabaseYT()
    # sesssion = data_base.create_session()
    options = Options()
    # options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    driver.get(f"https://www.youtube.com/@{name}/videos")
    time.sleep(5)
    try:
        try:
            element = driver.find_element(By.ID, 'channel-tagline')
            element.click()
        except:
            driver.find_element(By.CLASS_NAME, "style-scope ytd-channel-tagline-renderer").click()
        time.sleep(3)
        description_container = driver.find_element(By.ID, "description-container")
        links = driver.find_element(By.CSS_SELECTOR, "#links-section")
        details = driver.find_element(By.ID, 'additional-info-container')
        data = {}
        data['description'] = description_container.text
        data['links'] = get_links(links.get_attribute('outerHTML'))
        data['details'] = get_details(details.get_attribute('outerHTML'))
        data['channel_name'] = name
        print("-------------------------------------------------------------------")
        print(data.keys(),data)
        print("--------------------------------------------------------------------")
        user.append(data)
        print(data)
        # data_base.add_data_to_db_channel(data, sesssion)
    except Exception as e:
        print(e)
        pass
    print("Fetching Videos data")
    i=0
    if scrape_all_videos:
        while True:
            print('scroll no', i)
            i=i+1
            old_page = driver.page_source
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)
            new_page = driver.page_source
            html_content = new_page
            extract_data(html_content, name)
            if "No more results" in new_page:
                break
            if old_page == new_page:
                break
    else:
        for i in range(10):
            print('scroll no', i)
            old_page = driver.page_source
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)
            new_page = driver.page_source
            html_content = new_page
            extract_data(html_content, name)
    driver.close()

def main(channel_name=None,scrape_all_videos=False):
        start_time = time.time()
        channel_crawler_youtube(name=channel_name,scrape_all_videos=scrape_all_videos)
        df1=pd.DataFrame(user)
        df2=pd.DataFrame(videos)
        df2_unique=df2.drop_duplicates(subset='link',keep='last')
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        print(df1)
        print(df2_unique)
        return df1,df2_unique
def channel_crawler_youtube_driver(channel_name):
    print("Crawler started")
    df1,df2_unique=main(channel_name=channel_name)
    # df1=pd.DataFrame(user)
    print("User is",df1)
    print("Crawler ended")
    # df2=pd.DataFrame(videos)
    # df2_unique=df2.drop_duplicates(subset='link',keep='last')
    return df1,df2_unique
# if __name__ == "__main__":
#     start_time = time.time()
#     name='offtherecord-kashifabbasi'
#     df1,df2_unique=main(channel_name=name)
#     print(df1)
#     print(len(df2_unique))
#     end_time=time.time()
#     elapsed_time = end_time - start_time