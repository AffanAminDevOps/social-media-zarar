from .utility import *
from .database import *
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
from ...models import web

def image_link(driver):
    try:
        outer_html = driver.find_element(By.CLASS_NAME, "story-image.catbdr").get_attribute("outerHTML")
        soup = BeautifulSoup(outer_html, "html.parser")
        image_element = soup.find("img")
        image_url = image_element.get("src")
        print("Image URL:", image_url)
        return image_url
    except Exception as e:
        print(e)
        return None


def get_id(link):
    match = re.search(r"https:\/\/www\.express\.pk\/story\/(\d+)", link)
    if match:
        number = match.group(1)
        return number
    else:
        print("No match found in:", link)

def details(driver, link):
    title, author, up_date, article, photo, photo_link = "", "", "","", "",""
    try:
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'title')))
        title = driver.find_element(By.CLASS_NAME, 'title').text
        
        element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'timestamp')))
        up_date = driver.find_element(By.CLASS_NAME, 'timestamp').get_attribute("title")
        try:
            up_date=convert_date(up_date)
        except:
            pass
        element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'author')))
        author = driver.find_element(By.CLASS_NAME, 'author').text
        text = driver.find_element(By.XPATH, f'//*[@id="id-{get_id(link)}"]').text
        article = "\n".join(text.split("شیئر")[0].split('\n')[2:])
        photo_link = image_link(driver)
        photo=None
        if photo_link:
            photo=download_file(photo_link)
        print("Title:", title)
        print("Author:", author)
        print("Data:", up_date)
        print("Article:", article[:30], ".....")
        return title, author, up_date, article, photo, photo_link
    except Exception as e:
        print("Error in text")
        print(e)
        print(text)
        return None, None, None, None, None, None


def convert_date(date_str):
    try:
        # Parse the input date string into a datetime object
        date_obj = datetime.strptime(date_str, "%B %d, %Y")

        # Convert the datetime object to the desired format
        formatted_date = date_obj.strftime("%Y-%m-%d")

        return formatted_date
    except ValueError:
        # Handle invalid date strings
        return None
    

def extract_links(driver, paper):
    try:
        db=Database()
        session=db.create_session()
        page_html = driver.page_source
        news_links = set()
        filtered_links=[]
        soup = BeautifulSoup(page_html, 'html.parser')
        pattern = r'.*\d{1,}$'
        list_items = soup.find_all('li')
        i=1
        for li in list_items:
            links = li.find_all('a')
            for link in links:
                href = link.get('href')
                if href and re.match(pattern, href) and href.startswith('https://www.express.pk/story'):
                    news_links.add(href)
        for link in list(news_links):
            if web.objects.filter(link=link).count()>0:
                pass
            else:
                filtered_links.append(link)
        # all_db_links = [result[0] for result in session.query(News.link).all()]
        # filtered_data = [url for url in news_links if url not in all_db_links]
        print("links to be fetched ",len(filtered_links))
        session.commit()
        session.close()
        return list(filtered_links)
    except Exception as e:
        print(e)
        print("Error on extracting links.....................>>>>>>>")
        

    

def main():
    try:
        # db=Database()
        # session=db.create_session()
        data=[]
        paper = "express"
        driver = open_profile(profile="Express", headless=True)
        driver.get('https://www.express.pk/')
        driver.get('https://www.express.pk/latest-news/')
        wait = WebDriverWait(driver, 10)
        scroll_post(driver, 5)
        time.sleep(1)
        links = extract_links(driver, paper)
        for link in links:
            try:
                time.sleep(45)
                scroll_post(driver,2)
                driver.get(link)
                print("Link:", link)
                title, author, up_date, article, photo, photo_link = details(driver, link)
                if title:
                    
                    data.append({
                        "link":link,
                        "title": title,
                        "image":photo_link,
                        "news_creation_date": up_date,
                        "description": article,
                        "platform": paper
                    })
                    
                    # news_entry = News(link=link, title=title, image=photo_link, news_creation_date=up_date,description=article,platform=paper,image_data=photo)
                    # session.add(news_entry)
                    # session.commit()
                    print(title)
                    print("Data added to DB")

            except Exception as e:
                print(e)
        driver.quit()
        # session.close()
        return pd.DataFrame(data)
    except Exception as e:
        print(e)
        print("Main Loop Error ..................<<>>")
        try:
            driver.quit()
        except:
            pass
        return pd.DataFrame([])

def express_news_crawler():
    df=main()
    return df