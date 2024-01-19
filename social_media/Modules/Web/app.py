from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from ...models import *
import requests
from .utility import *
import concurrent.futures

def convert_to_datetime(date_time_str):
    try:
        date_format = "%Y-%m-%dT%H:%M:%S%z"
        date_time_obj = datetime.strptime(date_time_str, date_format)
        return date_time_obj
    except ValueError as e:
        print(f"Error: {e}")
        return None


def get_posts(element):
    if element.find('a').get('href'):
        return element.find('a').get('href')
    else:
        return None


def get_headline(element):
    if element.find('a'):
        return element.find('a').text
    else:
        return None


def get_time(element):
    if element.find('time', class_='entry-date'):
        return convert_to_datetime(element.find('time', class_='entry-date').get('datetime'))
    else:
        return None


def get_image(element):
    if element.find('img', class_='attachment-post-thumbnail'):
        return element.find('img', class_='attachment-post-thumbnail').get('src')
    else:
        return None


def check_notification(page):
    close_button_selector = 'div[aria-label="Close ad"]'
    close_button = page.locator(close_button_selector)
    return close_button


def get_details(page):
    data = page.inner_html("[class='single-post-left']")
    soup = BeautifulSoup(data, "html.parser")
    descripion = [txt.text.strip() for txt in soup.find_all('p')]
    Author = soup.find('span', class_='byline').text
    if soup.find('span', class_='byline').get('href') != None:
        Author_link = soup.find('span', class_='byline').get('href')
    else:
        Author_link = None
    # print(descripion)
    # print(Author)
    # print(Author_link)
    # ,Author,Author_link
    return ''.join(descripion)


# def process_row(element):
#     parse(element)


# def connection():
#     query = 'SELECT * FROM public."AppNews"'
#     df1 = pd.read_sql(query, db.engine)
#     query = 'SELECT * FROM public."News"'
#     df2 = pd.read_sql(query, db.engine)
#     print('Total News Collected', len(df1))
#     df1_filtered = df1[~df1['link'].isin(df2['link'])]
#     print('Remaining Data to be collected', len(df1_filtered))
#     return df1_filtered


def parse_elem(element):
    post = {}
    # db = Database()
    # session = db.create_session()
    try:
        post['Link'] = get_posts(element)
        # existing_data = session.query(News).filter(News.link == post['Link']).order_by(
        #     News.news_creation_date.desc()).first()
        if web.objects.filter(link=post['Link']).count()>0:
            print("News Already Exists")
        else:
            post['Title'] = get_headline(element)
            post['News_creation_date'] = get_time(element)
            post['Media'] = get_image(element)
            post['Platform'] = "app.pk"
            post['Description'] = run_page2(post['Link'])
            news=web(
                title=post['Title'],
                description=post['Description'],
                link=post['Link'],
                image=post['Media'],
                platform="app",
                news_creation_date=post['News_creation_date']
            )
            news.save()
            # news_entry = News(link=post['Link'], title=post['Title'], image=post['Media'],
            #                   news_creation_date=post['News_creation_date'], description=post['Description'],
            #                   platform=post['Platform'], image_data=download_file(post['Media']))
            # session.add(news_entry)
            # session.commit()
            print(post['Title'])
            print("Data added to the database.")
            print('-------' * 30)
        
    except AttributeError as e:
        print(e)
        


def app_scrape(scrape_all_pages=True) -> None:
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        link = "https://www.app.com.pk/national/"
        while (True):
            page.goto(link, wait_until='domcontentloaded', timeout=10 * 10000)
            data = page.inner_html("[class='site-content']")
            soup = BeautifulSoup(data, "html.parser")
            elements = soup.find_all("article")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(parse_elem, element) for element in elements]
                concurrent.futures.wait(futures)
            if scrape_all_pages == True:
                next_link = page.inner_html("[class='navigation pagination']")
                soup = BeautifulSoup(next_link, "html.parser")
                link = soup.find('a', class_='next page-numbers').get('href')
                print('Link')
                print(link)
                print('-------' * 30)
                if link == None:
                    break
            else:
                break
        context.close()
        browser.close()


def run_page2(link):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(link)
    data = driver.find_element(By.CSS_SELECTOR, "[class='single-post-left']").get_attribute('outerHTML')
    soup = BeautifulSoup(data, "html.parser")
    descripion = [txt.text.strip() for txt in soup.find_all('p')]
    print(descripion)
    Author = soup.find('span', class_='byline').text
    if soup.find('span', class_='byline').get('href') != None:
        Author_link = soup.find('span', class_='byline').get('href')
    else:
        Author_link = None
    driver.close()
    driver.quit()
    return ''.join(descripion)


# if __name__ == "__main__":
#     start_time = time.time()
#     run(scrape_all_pages=False)
#     end_time = time.time()
#     elapsed_time = end_time - start_time
#     print(f"Elapsed time: {elapsed_time:.2f} seconds")
