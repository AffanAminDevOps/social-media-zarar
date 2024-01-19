from .utility import download_file,open_profile,scroll_post
from .database import Database,News
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
from datetime import datetime
from .database import Database
import pandas as pd
# import tldextract
def get_image_link(driver):        
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    figure_elements = soup.find_all('img',  class_='uploaded-jshare-image')
    for figure in figure_elements:
        src_link = figure.get('src')
        print(src_link)
        return src_link
    return None


def details(driver):
    title, author, up_date, article, photo, photo_link= "", "", "","", "", ""
    try:
        banner = driver.find_element(By.CLASS_NAME, "detail-right-top").text
        title = banner.split("\n")[0]
        up_date = banner.split("\n")[-1]
        type = banner.split("\n")[-2]
        photo_link = get_image_link(driver)
        # photo_path = ""
        # if photo_link:
        #     photo_path = download_file(photo_link)
        article = driver.find_element(By.CLASS_NAME, 'detail_view_content').text
        if 'فائل فوٹو' in article.split('\n')[0]:
            lines = article.split('\n')    
            if lines:
                lines = lines[1:] 
            article = '\n'.join(lines) 
        video_text = "Pause\nUnmute"
        if article.startswith(video_text):
            article = "\n".join(article.split("\n")[7:])
        print(article[:40])
        return  title, author, up_date, article , photo_link
    except Exception as e:
        print("Error in text")
        print(e)
        print(article)
        return None, None, None, None, None


def convert_urdu_date_to_iso(input_date="", year=""):
    urdu_month_mapping = {
        "جنوری": "01",
        "فروری": "02",
        "مارچ": "03",
        "اپریل": "04",
        "مئی": "05",
        "جون": "06",
        "جولائی": "07",
        "اگست": "08",
        "ستمبر": "09",
        "اکتوبر": "10",
        "نومبر": "11",
        "دسمبر": "12",
    }
    parts = input_date.split()
    day = int(parts[0])
    urdu_month = parts[1]
    month = urdu_month_mapping.get(urdu_month, "")
    if month:
        formatted_date = f"{year}-{month}-{day:02}"
        return formatted_date.strip()
    else:
        return None
    

def extract_links(driver, paper):
    # db=Database()
    # session=db.create_session()
    # all_db_links = [result[0] for result in session.query(News.link).all()]
    try:
        page_html = driver.page_source
        soup = BeautifulSoup(page_html, 'html.parser')
        pattern = r'.*\d{4,}$'
        list_items = soup.find_all('li')
        news_links = set()
        for li in list_items:
            links = li.find_all('a')
            for link in links:
                href = link.get('href')
                if href and re.match(pattern, href) and href.startswith('https://jang.com.pk/news/'):
                    news_links.add(href)
        
        # filtered_data = [url for url in news_links if url not in all_db_links]
        print("links to be fetched ",len(news_links))
        # session.commit()
        # session.close()
        return list(news_links)
    except Exception as e:
        print(e)
        print("Error on extracting links.....................>>>>>>>")
 

def main():
    try:
        data=[]
        paper = "jang"
        driver = open_profile(profile="Jang", headless=True)
        driver.get('https://www.jang.com.pk/')
        driver.get('https://jang.com.pk/category/latest-news')
        scroll_post(driver, 20)
        time.sleep(1)
        links = extract_links(driver, paper)
        for link in links:
            try:
                time.sleep(30)
                driver.get(link)
                print("Link:", link)
                title, author, up_date, article , photo_link= details(driver)
                try:
                    date, year = up_date.split("،")
                    up_date = convert_urdu_date_to_iso(date, year)                        
                except:
                    up_date = datetime.now().strftime('%Y-%m-%d')
                print("**__++__** "*10)
                if title:
                    data.append({
                        "link":link,
                        "title": title,
                        "image":photo_link,
                        "news_creation_date": up_date,
                        "description": article,
                        "platform": paper
                    })
                    
                    # print(photo_link)
                    # if photo_link:
                    #     photo=download_file(photo_link)
                    # news_entry = News(link=link, title=title, image=photo_link, news_creation_date=up_date,description=article,platform="jang",image_data=photo)
                    # session.add(news_entry)
                    # session.commit()
                    # session.close()
                    print(title)
                    print("Data added to DB")
            except Exception as e:
                print(e)
        driver.quit()
        return pd.DataFrame(data)
    except Exception as e:
        print(e)
        print("Main Loop Error ..................<<>>")
        try:
            driver.quit()
        except:
            pass
        return pd.DataFrame([])


def jang_news_scraper():
    df=main()
    return df
# if __name__ == "__main__":
#     df=main()
#     print(df)