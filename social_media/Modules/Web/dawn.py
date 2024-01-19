import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import re
from .utility import *
from .database import Database,News
import pandas as pd
from ...models import web
def image_link(driver, id):
     # Find the element by its ID
    element = driver.find_element(By.ID, str(id))
    # Get the outer HTML of the element
    outer_html = element.get_attribute("outerHTML")
    pattern = r'<picture>(.*?)</picture>'
    # Use re.findall to find all occurrences of the pattern in the text
    matches = re.findall(pattern, outer_html, re.DOTALL)
    # Print the list of matched text
    for match in matches:
        if "?r=" not in match and r'https://i.dawn.com/primary' in match:
            print("Thumbnail Image:", match.split('src="')[1].split('" alt')[0])
            # print("-_-*-_"*10)
            return match.split('src="')[1].split('" alt')[0]
    print("No image Link Found")
    return None


def details(text):
    title, author, up_date, article = "", "", "",""
    try:
        title = text.split('\n')[0]
        details = text.split('\n')[1]
        author = details.split('Published')[0].strip()
        up_date = " ".join(details.split('Published')[1].strip().split(' ')[:3])
        value = "Read more"
        try:
            article = text.split("1.5x")[1].split(value)[0].strip()
            if article[-1] == "0":
                article = article[:-1]
        except:
            article = text.split("    0")[1].split(value)[0].strip()
            if article[-1] == "0":
                article = article[:-1]
        return title, author, up_date, article
    except Exception as e:
        print("Error in text")
        print(e)
        print(text)
        return None, None, None, None


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
    # db=Database()
    # session=db.create_session()
    try:
        filtered_links=[]
        page_html = driver.page_source
        # Create a BeautifulSoup object to parse the HTML content
        soup = BeautifulSoup(page_html, 'html.parser')
        
        extra_links = ['https://www.dawn.com/advertise', 'https://www.dawn.com/events/supplements','https://www.dawn.com/']
        links = set()
        # Find all the anchor elements (links) on the page
        link_elements = soup.find_all('a')
        
        # Extract and print the href attribute of each link
        for link_element in link_elements:
            link = link_element.get('href')
            if link.startswith('https://www.dawn.com/') and not link.startswith('https://www.dawn.com/authors'):
                if link not in extra_links :
                    links.add(link)
        for link in list(links):
            if web.objects.filter(link=link).count()>0:
                pass
            else:
                filtered_links.append(link)
        print(len(filtered_links))
        # all_db_links = [result[0] for result in session.query(News.link).all()]
        # filtered_data = [url for url in links if url not in all_db_links]
        # print("links to be fetched ",len(filtered_data))
        return filtered_links
    except Exception as e:
        print(e)
        print("Error on extracting links.....................>>>>>>>")
        
def get_id(text=""):
    # Define a regular expression pattern to match the value between slashes
    pattern = r"/(\d+)/"
    
    # Use re.findall to find all occurrences of the pattern in the text
    matches = re.findall(pattern, text)
    
    if matches:
        extracted_value = matches[0]
        return extracted_value
    else:
        pattern = r'\d+$'  # Matches one or more digits at the end of the string
        match = re.search(pattern, text)
        if match:
            digits = match.group()
            return digits
        print("No ID found.")
        return None
    

def dawn_news_scrape():
    try:
        paper = "dawn"
        driver = open_profile(profile="Dawn", headless=True)
        driver.get('https://www.dawn.com/')
        driver.get('https://www.dawn.com/latest-news')
        scroll_post(driver, 13)
        time.sleep(1)
        links = extract_links(driver, paper)
        data=[]
        # db=Database()
        # session=db.create_session()

        for link in links:
            try:
                driver.get(link)
                print("Link:", link)
                id = get_id(driver.current_url)
                if driver.current_url[:23] != link[:23]:
                    print("Skipped: ", driver.current_url)
                    continue
                if id != None:
                    text = driver.find_element(By.ID, str(id)).text
                    title, author, up_date, article = details(text)
                    up_date = convert_date(up_date)                        
                    if title:
                        photo_link = image_link(driver, id)
                        photo=None
                        
                        # if photo_link:
                        #     photo=download_file(photo_link)
                        # news_entry = News(link=link, title=title, image=photo_link, news_creation_date=up_date,description=article,platform="dawn",image_data=photo)
                        data.append({
                            'link': link,
                            'title':title,
                            'image':photo_link,
                            'news_creation_date':up_date,
                            'description':article,
                            'platform': "dawn"
                        })
                        
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

# df=dawn_news_scrape()
# print(df.columns,df)