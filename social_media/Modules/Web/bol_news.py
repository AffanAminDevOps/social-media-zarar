from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from selenium.webdriver.common.by import By
# from database import Database,News
from .utility import *
# from utility import *
# from social_media.models import web
from ...models import web
class BolNewsScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.data = []
    def scrape(self):
        driver = self.initialize_driver()
        try:
            bol_news_links = self.get_bol_news_links(driver)
            self.extract_data(driver, bol_news_links)
        finally:
            driver.quit()
    def initialize_driver(self):
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)
        driver.get(self.base_url)
        return driver
    def get_bol_news_links(self, driver):
        assert isinstance(driver, webdriver.Chrome), "Expected a Chrome WebDriver"
        target_elements = driver.find_elements(By.CSS_SELECTOR, ".stripe-top-10.home-lazy-load")
        bol_news_links = set()
        filtered_links=[]
        for target in target_elements:
            links = target.find_elements(By.TAG_NAME, "a")
            for link in links:
                bol_news_links.add(link.get_attribute("href"))
            # for link in links:
            #     if web.objects.filter(link=link).count()>0:
            #         pass
            #     else:
            #         filtered_links.append(link)
            # filtered_links.append()
            return list(bol_news_links)
    def extract_data(self, driver, bol_news_links):
        for url in bol_news_links:
            driver.get(url)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            title = self.get_title(soup)
            # print("------------------------- title -----------------------------")
            print(title)
            desc = self.get_description(soup)
            # print("--------------------------Description ----------------------")
            # print(desc)
            date = self.get_date(soup)
            # print("--------------------------Date ----------------------")
            # print(date)
            img_src = self.get_image(soup)
            # print("------------------------- img_src -----------------------------")
            # print(img_src)
            
            data_entry = {
                "title": title,
                "description": desc,
                "link": url,
                "news_creation_date": date,
                "image": img_src,
                "platform":"bolnews"
            }
            self.data.append(data_entry)
    def get_title(self, soup):
        titles = soup.find('h1', class_='mb-0')
        return titles.get_text(strip=True) if titles else "Title not found"
    def get_description(self, soup):
        desc = soup.find_all(class_='col-lg-6')
        descriptions = []
        for i in desc:
            paragraphs = i.find_all("p")
            for paragraph in paragraphs[1:-2]:
                text = paragraph.get_text().strip()
                if "also read" in text.lower():
                    break
                descriptions.append(text)
            if "also read" in [desc.lower() for desc in descriptions]:
                break
        return "".join(descriptions)
    def get_date(self, soup):
        date_element = soup.find('span', class_='date')
        if date_element:
            raw_date = date_element.get_text(strip=True)
            try:
                parsed_date = datetime.strptime(raw_date, "%dth %b, %Y. %I:%M %p")
                formatted_date = parsed_date.strftime("%Y-%m-%d")
                return formatted_date
            except ValueError:
                return "Invalid Date Format"
        else:
            return "Date Not Found"
    def get_image(self, soup):
        image = soup.find_all('figure', class_='featuredimg')
        for i in image:
            img = i.find("img")
            if img:
                img_src = img.get('src')
                return img_src
def bol_news_scraper():
    base_url = "https://www.bolnews.com"
    scraper = BolNewsScraper(base_url)
    scraper.scrape()
    df = pd.DataFrame(scraper.data)
    print(df)
    return df
# df=bol_news_scraper()
# print(df.columns)
# print(df)
# if __name__ == "__main__":
#     start_time = time.time()
#     main()
#     end_time = time.time()
#     elapsed_time = end_time - start_time
#     print(f"Elapsed time: {elapsed_time:.2f} seconds")
    