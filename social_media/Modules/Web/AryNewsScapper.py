from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
import pandas as pd
from datetime import datetime
import re
import requests
# from database import Database, News
import time
import concurrent.futures
from ...models import web

class AryNewsScraper:
    def __init__(self, urls):
        self.urls = urls
        self.data = []

    def scrape(self, url):
        try:
            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Firefox(options=options)
            driver.get(url)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            title = self.get_title(soup)
            descriptions = self.get_description(soup)
            date_time = self.get_date(soup)
            image_url = self.get_image(soup)

            # Append the scraped data to the 'data' list
            self.data.append({
                'link': url,
                'title': title,
                'image': image_url,
                'news_creation_date': date_time,
                'description': descriptions,
                'platform': "arynews",
            })

            print("Data Added to DataFrame")
            driver.close()
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")

    def get_title(self, soup):
        titles = soup.find('h1', class_='tdb-title-text')
        if titles:
            title = titles.get_text(strip=True)
            return title
        else:
            return "Title not found"

    def get_description(self, soup):
        desc = soup.find_all(class_="tdb-block-inner td-fix-index")
        descriptions = []
        for i in desc:
            paragraphs = i.find_all("p")
            for paragraph in paragraphs:
                text = paragraph.get_text().strip()
                if text:
                    descriptions.append(text)
        return "".join(descriptions)

    def get_date(self, soup):
        dates = soup.find('time', class_='entry-date updated td-module-date')
        if dates:
            date_str = dates.get_text(strip=True)
            date_time = datetime.strptime(date_str, "%B %d, %Y")
            return date_time
        else:
            return "Date not found"

    def get_image(self, soup):
        image_divs = soup.find_all("div",
                                   class_="td_block_wrap tdb_single_bg_featured_image tdi_86 tdb-content-horiz-left td-pb-border-top td_block_template_1")

        for div in image_divs:
            style_tags = div.find_all("style")
            for style_tag in style_tags:
                style_content = style_tag.string

                match = re.search(r'\.tdi_86 \.tdb-featured-image-bg\s*{\s*background:\s*url\(\'(.*?)\'\)',
                                  style_content, re.DOTALL)

                if match:
                    image_url = match.group(1)
                    print("Image URL:", image_url)
                    return image_url
        return None

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


def scrape_ary_news():
    url = "https://arynews.tv/category/pakistan/"
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    driver.implicitly_wait(5)
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, "html.parser")
    target_elements = soup.find_all(class_="td_block_inner tdb-block-inner td-fix-index")

    ary_news_set = set()
    filtered_urls=[]
    for element in target_elements:
        links = element.find_all("a", href=True)
        for link in links:
            ary_news_set.add(link['href'])

    ary_news = list(ary_news_set)
    for link in ary_news:
        if web.objects.filter(link=link).count()>0:
            pass
        else:
            filtered_urls.append(link)
    print(len(filtered_urls))
    scraper = AryNewsScraper(filtered_urls)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scraper.scrape, url) for url in ary_news]
        concurrent.futures.wait(futures)

    # Create a DataFrame from the collected data
    df = pd.DataFrame(scraper.data)
    print(df.columns)
    return df



