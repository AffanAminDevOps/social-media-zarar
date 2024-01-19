from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
from datetime import datetime
# from database import Database, News
# from app import download_file
import concurrent.futures
import pandas as pd
import requests
import time
import re
# from ...models import web
from asgiref.sync import sync_to_async

def get_website_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            try:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                date = soup.find('time')['datetime']
                date_object = datetime.strptime(date, "%a, %d %b %Y")
                article = soup.find('article')
                title = article.find('h1').text
                print(title)
                source_tag = soup.find('source')
                media_attribute = source_tag.get('srcset') if source_tag else None
                p_tags = soup.find_all('p')
                description = ' '.join([p.text for p in p_tags])
                return {
                    'link': url,
                    'title': title,
                    'image': media_attribute,
                    'news_creation_date': date_object,
                    'description': description,
                    'platform': "dunyanews"
                    # 'image_data': download_file(media_attribute),
                }
            except Exception as e:
                print(e)
        else:
            print(f"Request was not successful. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return None


def store_data_in_dataframe(data):
    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    print(df)
    return df
    # Further processing or analysis can be done here


def run() -> None:
    # db = Database()
    # session = db.create_session()
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        link = "https://dunyanews.tv/en/Pakistan"
        page.goto(link, wait_until='domcontentloaded', timeout=10 * 10000)
        page_content = page.content()
        soup = BeautifulSoup(page_content, 'html.parser')
        all_links = [a.get('href') for a in soup.find_all('a')]
        filtered_urls = set()
        pakistan_link_regex = re.compile(r'/index.php/en/Pakistan/(.*)')
        for url in all_links:
            match = pakistan_link_regex.match(url)
            if match:
                url = 'https://dunyanews.tv/' + match[0]
                filtered_urls.add(url)
        # new_links=[]
        # data = list(filtered_urls)
        # # for link in data:
        # #     if await check_link_async(link):
        # #         pass
        # #     else:
        # #         new_links.append(link)
        #     # if web.objects.filter(link=link).count()>0:
        #     #     pass
        #     # else:
        #     #     new_links.append(link)
        
        print("Data to be fetched", len(filtered_urls))
        scraped_data = []
        for url in list(filtered_urls):
            scraped_data.append(get_website_html(url))
            print("Done -------------")
        # session.commit()
        # session.close()
        print("=================================================",scraped_data)
        df=store_data_in_dataframe(scraped_data)
        return df
    


def duniya_news_scrap():
    start_time = time.time()
    df=run()
    # print(df.columns,df)
    # for index, row in df.iterrows():
    #     if web.objects.filter(link=row['link']).count() > 0:
    #         df.drop(index, inplace=True)
    print(df.columns,df)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    return df
# duniya_scrapper()