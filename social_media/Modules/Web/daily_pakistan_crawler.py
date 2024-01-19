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
        outer_html = driver.find_element(By.CLASS_NAME, 'responsive_test').get_attribute("outerHTML")
        soup = BeautifulSoup(outer_html, 'html.parser')
        # Find all image tags
        image_tags = soup.find_all('img')
        # Extract src attributes to get image URLs
        image_urls = [img['src'] for img in image_tags]
        for url in image_urls:
            print("Image:", url)
            return url
    except Exception as e:
        print("Image not Found")
    return None


def get_id(link):
    match = re.search(r"https:\/\/www\.express\.pk\/story\/(\d+)", link)
    if match:
        number = match.group(1)
        # print("Extracted Number:", number)
        return number
    else:
        print("No match found in:", link)

def details(driver, link):
    title, author, up_date, article, photo, photo_link = "", "", "","", "",""
    try:
        banner = driver.find_element(By.CLASS_NAME, 'theiaStickySidebar').text
        # Define a regular expression pattern to match the time and date
        pattern_author = r'\d{2}:\d{2} [APap][Mm] \| \d{1,2} [A-Za-z]{3}, \d{4}'
        # Use re.sub to remove the time and date from the input string
        author = re.sub(pattern_author, '', banner).strip()
        # Print the extracted author
        pattern_time = r'\b\d{2}:\d{2}(?:\s?[APap][Mm])?\b'
        matches = re.findall(pattern_time, banner)
        date = ""
        date = banner.split("|")[1].strip()
        up_date = date.split("\n")[0]
        catogory = driver.find_element(By.CLASS_NAME, 'tt-blog-category').text
        text = driver.find_element(By.CLASS_NAME, "custom-tt-wrapper").text
        article = ""
        title = driver.find_element(By.CLASS_NAME, 'c-h1').text
        for row in text.split("\n"):
            if row.strip() == catogory:
                break
            if not row.startswith("Advertisement"):
                article += row + "\n"
        photo_link = image_link(driver)
        photo = None
        return title, author, up_date, article, photo, photo_link
    except Exception as e:
        print("Error in text")
        print(e)
        print(text)
        return None, None, None, None, None, None


def convert_date(input_date=""):
    try:
        # Parse the input date string using the specified format
        date_obj = datetime.strptime(input_date, '%d %b, %Y')

        # Format the date as 'YYYY-MM-DD'
        formatted_date = date_obj.strftime('%Y-%m-%d')

        return formatted_date
    except ValueError:
        print("Error converting date", date_obj)
        # Handle invalid date format
        return None
    

def extract_links(driver, paper):
    # db=Database()
    # session=db.create_session()
    # all_db_links = [result[0] for result in session.query(News.link).all()]
    try:
        filtered_urls=[]
        page_html = driver.page_source
        soup = BeautifulSoup(page_html, 'html.parser')
        links = set()
        link_elements = soup.find_all('a')
        pattern = r"https://en\.dailypakistan\.com\.pk/\d+"
        for link_element in link_elements:
            link = link_element.get('href')
            if re.match(pattern, link):
                    links.add(link)
        for link in list(links):
            if web.objects.filter(link=link).count()>0:
                pass
            else:
                filtered_urls.append(link)
        # filtered_data = [url for url in links if url not in all_db_links]
        print("links to be fetched ",len(filtered_urls))
        # session.commit()
        # session.close()
        return filtered_urls
    except Exception as e:
        print(e)
        print("Error on extracting links.....................>>>>>>>")
        

    

def main():
    try:
        # db=Database()
        # session=db.create_session()
        data=[]
        paper = "daily_pakistan"
        driver = open_profile(profile="Daily Pakistan", headless=True)
        driver.get('https://en.dailypakistan.com.pk/')
        driver.get('https://en.dailypakistan.com.pk/latest')
        try:
            wait = WebDriverWait(driver, 15) 
            element = wait.until(EC.presence_of_element_located((By.ID, 'smart_push_smio_not_allow')))
            driver.find_element(By.ID, "smart_push_smio_not_allow").click()
        except Exception as e:
            print(e)
            print("Error while canceling notificaitons.........................................<><><><>")
    
        for _ in range(3):
            try:
                scroll_post(driver, 1)
                wait = WebDriverWait(driver, 15) 
                element = wait.until(EC.presence_of_element_located((By.ID, 'post_show_more')))
                driver.find_element(By.ID, "post_show_more").click()
                print("Clicked on load meore")
            except Exception as e:
                print(e)
                print("Error while clicking show more...............................<><><><>")
       
        time.sleep(1)
        links = extract_links(driver, paper)
        for link in links:
            print(link)
            try:
                time.sleep(45)
                scroll_post(driver,2)
                driver.get(link)
                print("Link:", link)
                title, author, up_date, article, photo, photo_link = details(driver, link)
                up_date = convert_date(up_date)
                if title:
                    data.append({
                        "link":link,
                        "title": title,
                        "image":photo_link,
                        "news_creation_date": up_date,
                        "description": article,
                        "platform": "dailypakistan"
                    })
                    
                    # print(photo_link)
                    # if photo_link:
                    #     photo=download_file(photo_link)
                    # news_entry = News(link=link, title=title, image=photo_link, news_creation_date=up_date,description=article,platform=paper,image_data=photo)
                    
                    # session.add(news_entry)
                    # session.commit()
                    # print(title)
                    print("Data added to DB")
            except Exception as e:
                print(e)
        driver.quit()
        return pd.DataFrame(data)
        # session.close()
    except Exception as e:
        print(e)
        print("Main Loop Error ..................<<>>")
        try:
            driver.quit()
        except:
            pass
        return pd.DataFrame([])

def daily_pakistan():
    df=main()
    print(df)
    return df