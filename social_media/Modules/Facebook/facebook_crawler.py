    #!/usr/bin/env python
# coding: utf-8

# In[2]:


# import undetected_chromedriver as webdriver
from selenium import webdriver
import time
import datetime
import random
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import os
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
import pandas as pd

# In[3]:


import psycopg2

class FacebookDatabase:
    def __init__(self, host, database, user, password):
        self.db_params = {
            "host": host,
            "database": database,
            "user": user,
            "password": password
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.db_params)
            # print("Connected to the database.")
        except psycopg2.Error as e:
            print("Connection error:", e)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            # print("Disconnected from the database.")

    def create_posts_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS posts (
            ID SERIAL PRIMARY KEY,
            Account TEXT,
            Post TEXT,
            Reactions TEXT,
            Shares TEXT,
            Comments TEXT,
            Type TEXT,
            Upload_Time TEXT,
            Shared TEXT,
            Thumbnail_Link TEXT
        );
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            self.connection.commit()
            # print("Table 'posts' created successfully.")
        except psycopg2.Error as e:
            print("Error:", e)
    
    def delete_posts_table(self):
        delete_table_sql = """
        DROP TABLE IF EXISTS posts;
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(delete_table_sql)
            self.connection.commit()
            # print("Table 'posts' deleted successfully.")
        except psycopg2.Error as e:
            print("Error:", e)


    def insert_into_posts_table(self, data_dict):
        self.create_posts_table()
        select_sql = """
        SELECT ID, Thumbnail_Link FROM posts WHERE Account = %s AND Post = %s;
        """
        update_sql = """
        UPDATE posts
        SET Reactions = %s, Shares = %s, Comments = %s, Type = %s, Upload_Time = %s, Shared = %s, Thumbnail_Link = %s
        WHERE ID = %s;
        """
        insert_sql = """
        INSERT INTO posts (Account, Post, Reactions, Shares, Comments, Type, Upload_Time, Shared, Thumbnail_Link,link)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s);
        """

        try:
            cursor = self.connection.cursor()

            # Check if data is already present
            cursor.execute(select_sql, (data_dict['Account'], data_dict['Post']))
            existing_row = cursor.fetchone()

            if existing_row:
                existing_id, existing_thumbnail = existing_row
                new_thumbnail = data_dict['Thumbnail Link']
                if new_thumbnail == '':
                    new_thumbnail = existing_thumbnail
                
                update_values = (
                    data_dict['Reactions'],
                    data_dict['Shares'],
                    data_dict['Comments'],
                    data_dict['Type'],
                    data_dict['Upload Time'],
                    data_dict['Shared'],
                    new_thumbnail,
                    existing_id
                )
                cursor.execute(update_sql, update_values)
                self.connection.commit()
                # print("Data updated in 'posts' table successfully.")
            else:
                values = (
                    data_dict['Account'],
                    data_dict['Post'],
                    data_dict['Reactions'],
                    data_dict['Shares'],
                    data_dict['Comments'],
                    data_dict['Type'],
                    data_dict['Upload Time'],
                    data_dict['Shared'],
                    data_dict['Thumbnail Link'],
                    data_dict['link']
                )
                cursor.execute(insert_sql, values)
                self.connection.commit()
                # print("Data inserted into 'posts' table successfully.")

        except psycopg2.Error as e:
            print("Error:", e)

    
    def get_all_posts(self):
        select_all_sql = """
        SELECT * FROM posts;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(select_all_sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return result
        except psycopg2.Error as e:
            print("Error:", e)


# In[4]:


def open_profile(profile):
    # Profile Opening
    current_directory = os.getcwd()
    print("Opening Profile:", current_directory, fr"\{profile}")
    user_data_dir = Path(rf"{current_directory}\{profile}")
    
    # Replace the ChromeOptions with FirefoxOptions
    options = FirefoxOptions()

    # TELL WHERE IS THE DATA DIR
    options.add_argument("--user-data-dir={}".format(user_data_dir))
    
    # USE THIS IF YOU NEED TO HAVE MULTIPLE PROFILES
    options.add_argument('--profile-directory=Default')
    
    # Use Firefox instead of Chrome
    browser = webdriver.Firefox(options=options)

    # Set the width and height of the WebDriver window
    width = 1080  # Replace with your desired width
    height = 720  # Replace with your desired height
    browser.set_window_size(width, height)
    
    return browser


# In[5]:


def scroll_post(driver, posts=1, special=False):
    for i in range(posts):
        # Define the scroll step size and total steps
        scroll_step = 10  # Adjust the step size as needed
        total_steps = 77  # Adjust the total number of steps as needed
        
        # Perform slow scroll down the page
        for step in range(total_steps):
            driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            driver.implicitly_wait(0.1)  # Wait to create a smooth scroll effect
        if special:
            time.sleep(3)
        


# In[6]:


def get_features(text, link=None):
    try:
        shared = False
        if 'Reels' in text:
            post_message = text.split("Reels")[0].strip().split('\n')[:-1]
            post_message = post_message[0]
            upload_time = text.split('Reels')[1].strip().split('.')[0].split('\n')[0].replace('·', '').strip()
            reactions, comments, shares = text.split('·')[-1].strip().split('\n')
            post_type = 'reel'
        else:
            #for message
            post_message_start = text.index("·") + 1
            post_message_end = text.index("All reactions:")
            post_message = text[post_message_start:post_message_end].strip().replace('See translation','')
            video_time_pattern = re.compile(r"\d+:\d+ / \d+:\d+")
            post_message =video_time_pattern.sub("", post_message).strip()
    
            if "·" in post_message:
                post_message = post_message.replace('·', '')
                shared = True
        
            # Extract reactions, comments, and shares
            reactions_start = text.index("All reactions:") + len("All reactions:")
            reactions_end = text.index("Like")
            reactions = text[reactions_start:reactions_end].strip()
            reactions = reactions.split('\n')[0]
        
            likes = text.split('All reactions:')[1].split("\nLike\n")[0]
            comments = likes.split('\n')[-2]
            shares = likes.split('\n')[-1]
            
            #upload time
            upload_time = text.split('\n')[1]
        
            #type of the post
            # Extract the video time using regular expression
            video_time_pattern = re.compile(r"\d+:\d+ / \d+:\d+")
            video_time_match = video_time_pattern.search(text)
            post_type = 'text'
            
            if video_time_match:
                post_type = "video"
                post_type += " " + video_time_match.group()
            
    
            if link != None and 'text' in post_type:
                post_type = 'photo'   
        print("Post:\n", post_message)
        print(f"\nReactions: {reactions}  Shares: {shares} Comments: {comments}")
        print("Type:",post_type, "Upload Time:", upload_time, "Shared:", shared)
        if link != None and post_type != 'reel':
            print("Photo: ", link)
        data = {
        "Post": str(post_message),
        "Reactions": str(reactions),
        "Shares": str(shares),
        "Comments": str(comments),
        "Type": str(post_type),
        "Upload Time": str(upload_time),
        "Shared": str(shared),
        "Thumbnail Link": str(link)
        }
        # print(data)
        return data
    except Exception as e:
        print(str(e))
        print("Text is :", text)
        return None
        
        


# In[7]:


def get_last_posts(driver,account, last_posts):
    all_posts=[]
    for post_number in range(1,last_posts+1):
        scroll_post(driver)
        time.sleep(2)
        div_elements = driver.find_elements(By.XPATH ,f"//div[@aria-posinset='{post_number}']")
        print("Post Number: ", post_number)
        # Print details of the found elements
        for div_element in div_elements:
            tag_name = div_element.tag_name
            text = div_element.text
            attributes = div_element.get_attribute("outerHTML")
        
            photo = False
            soup = BeautifulSoup(attributes, 'html.parser')
            img_tags = soup.find_all('img')
            target_keywords = ['live', 'photo', 'video']
            filtered_links = [a['href'] for a in soup.find_all('a', href=True) if any(keyword in a['href'] for keyword in target_keywords)]
            # Print details of each <img> tag
            for img_tag in img_tags:
                src_value = img_tag.get('src')
                if "scontent" in src_value:
                    photo = True
                    break
            post_link = ""            
            if photo:
                data = get_features(text.strip(), link=src_value)
                print("The type of data is: ",type(data))
                print("---"*30)
                if data:
                    if filtered_links:
                        data['link']=filtered_links[-1]
                        # update_data(account, data)
                    else:
                        data['link']=None
                        # update_data(account, data)
                    all_posts.append(data)
                else:
                    pass
            else:
                data = get_features(text.strip())
                if data:
                    if filtered_links:
                        data['link']=filtered_links[-1]
                        # update_data(account, data)
                    else:
                        data['link']=None
                        # update_data(account, data)
                    all_posts.append(data)
                else:
                    pass
    driver.quit()
    return all_posts


# In[8]:


def update_data(account, data):
#    print("Acount:", data)
    db = FacebookDatabase(
         host= "localhost",
        database= "Facebook",
        user= "postgres",
        password= "ticker@1234"
    )
    db.connect()
    account_name = { 'Account': account}
    db.insert_into_posts_table({**account_name, **data})
    db.disconnect()


# In[9]:



def check_login(driver):
    username = 'zain@forbmax.ai'
    password = 'Forbmax1234'
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Extract visible text from the parsed 
    if "Sign Up" in soup.get_text():
        email_input = driver.find_element(By.XPATH, '//*[@id="email"]')
        email_input.click()
        for key in username:
            email_input.send_keys(key)  # Type the desired search query
            time.sleep(0.2)
        
        time.sleep(5)
        password_input = driver.find_element(By.XPATH, '//*[@id="pass"]')
        password_input.click()
        for key in password:
            password_input.send_keys(key)
            time.sleep(0.3)
        
        button = driver.find_element(By.NAME, "login")
        # Create an instance of ActionChains
        actions = ActionChains(driver)
        # Perform a click action on the button
        actions.click(button).perform()


# In[10]:


def sleep_random_time():
    # Generate a random sleep time between 45 and 60 minutes
    sleep_time = random.randint(45 * 60, 60 * 60)  # Convert minutes to seconds
    print("Stoped for ", sleep_time//60)
        # Sleep for the random time
    time.sleep(sleep_time)

def is_between_1am_and_3am(current_time):
    return current_time.time() >= datetime.time(1, 0) and current_time.time() <= datetime.time(3, 0)


# In[11]:

def facebook_profile(account):
    driver = open_profile('fb profile')
    driver.get('https://www.facebook.com/')
    check_login(driver)
    time.sleep(10)
    print("Account:", account)
    driver.get(r'https://www.facebook.com/'+account+'/')
    time.sleep(5)
    post=get_last_posts(driver,account, 30)
    print("all_posts:",post)
    df=pd.DataFrame(post)
    return df
# df=facebook_profile(account="GeoEnglishdotTV")
# df.to_csv("facebook_profile.csv")
# print(df)

# if __name__ == "__main__":
#     # accounts1 = ['https://www.facebook.com/GeoUrduDotTv'] #'DawnNews','anwarlodhi', 'MoeedPirzada', 'SabirShakirARY'
#     # accounts2 = ['GeoUrduDotTv', 'expressnewspk', 'UDarOfficial', 'arynewsasia', 'samaatvnews' ]
#     main('arynewsasia')

