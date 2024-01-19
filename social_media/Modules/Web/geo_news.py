from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pandas as pd
import time
from .database import Database, News
import concurrent.futures
from selenium.webdriver.firefox.options import Options
from ...models import web

class GeoNewsScraper:
    def __init__(self, urls):
        self.urls = urls
        self.data = []

    def scrape(self,url):
        database = Database()
        # session = database.create_session()
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        title = self.get_title(soup)
        descriptions = self.get_description(soup)
        date_time = self.get_date(soup)
        img_src = self.get_image(soup)
       
        self.data.append({
            'link': url,
            'title': title,
            'image': img_src,
            'news_creation_date': date_time,
            'description': descriptions,
            'platform': "geo",
        })

        print("Data Added to DataFrame")


    def get_title(self, soup):
        titles = soup.find('title')
        if titles:
            title = titles.get_text()
            return title
        else:
            return "Title not found"


    def get_description(self, soup):
        desc = soup.find_all(class_="content-area")
        descriptions = []
        for i in desc:
            paragraphs = i.find_all("p")
            for paragraph in paragraphs:
                text = paragraph.get_text().strip()
                if text:
                    descriptions.append(text)
        return "".join(descriptions)


    def get_date(self, soup):
        date = soup.find_all(class_="time-section")
        for i in date:
            date_str = i.find("p").text.strip()
            date_time = datetime.strptime(date_str, "%A, %B %d, %Y")
            return date_time


    def get_image(self, soup):
        image = soup.find_all(class_="content-area")
        for i in image:
            img = i.find("img")
            if img:
                img_src = img.get("src")
                return img_src


    def download_file(self, img_src):
        try:
            response = requests.get(img_src)
            if response.status_code == 200:
                file_data = response.content
                return file_data
            else:
                print(f"Failed to download the file from {img_src}. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None


def geo_news_scrapper():
    # Scraping URLs using Selenium and BeautifulSoup
    url = "https://www.geo.tv/category/pakistan"

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    driver.implicitly_wait(5)
    page_source = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_source, "html.parser")
    target_elements = soup.find_all(
        class_="col-xs-12 col-sm-12 col-md-8 col-lg-8 video-content latest-content latest-page-new")
    geo_news = []
    filtered_links=[]
    for element in target_elements:
        links = element.find_all("a", href=True)
        for link in links[1:]:
            geo_news.append(link['href'])
    for link in geo_news:
        if web.objects.filter(link=link).count()>0:
            pass
        else:
            filtered_links.append(link)
    scraper = GeoNewsScraper(filtered_links)
    print(geo_news)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scraper.scrape, url) for url in geo_news]
        concurrent.futures.wait(futures)
    df=pd.DataFrame(scraper.data)
    return df
# df=geo_news_scrapper()
# df=geo_news_scrapper()
# print(df.columns,df)
