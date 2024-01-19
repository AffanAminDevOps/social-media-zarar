try:
    import undetected_chromedriver as webdriver
except:
    from selenium import webdriver

from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.keys import Keys
import os
from pathlib import Path
# from database import *
import requests
from datetime import datetime, time
import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

import os
from pathlib import Path
# from database import *
from . import conf
import requests

import time
import random

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

def sleep_random_time():
    # Generate a random sleep time between 45 and 60 minutes
    sleep_time = random.randint(45 * 60, 60 * 60)  # Convert minutes to seconds
    print("Stoped for ", sleep_time//60)
        # Sleep for the random time
    time.sleep(sleep_time)

def is_between_1am_and_3am(current_time=datetime.now()):
    return current_time.time() >= time(1, 0) and current_time.time() <= time(3, 0)


def download_image(image_url):
    if not os.path.exists("static/facebook"):
        os.makedirs("static/facebook")
    # Send an HTTP GET request to the image URL
    response = requests.get(image_url)
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Get the content of the response (image bytes)
        image_content = response.content
        file_extension = "png"
        count=len(os.listdir("static/facebook"))
        # Specify the path where you want to save the image
        save_path = f"static/facebook/{count}.{file_extension}"
        
        # Save the image content to the specified path
        with open(save_path, 'wb') as f:
            f.write(image_content)
        return save_path
    else:
        print("Failed to download the image.")
        return None


def open_profile(profile="-", new=False, headless=False):
    if profile == "-":
        new=True
    if new:
        if headless:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            browser = webdriver.Chrome(options=options)
        else:
            browser = webdriver.Chrome()
    
    else:
        current_directory = os.getcwd()
        print("Opening Profile:", current_directory , fr"\{profile}")
        user_data_dir = Path(rf"{current_directory}\{profile}")
        options = webdriver.ChromeOptions()
        
        if headless:
            options.add_argument('--headless')
        
        # Set the user data directory
        options.add_argument("--user-data-dir={}".format(user_data_dir))
        # Use this if you need to have multiple profiles
        options.add_argument('--profile-directory=Default')

        browser = webdriver.Chrome(options=options)
    
    if not headless:
        width = 1080  
        height = 740 
        browser.set_window_size(width, height)
    
    return browser


def check_login(driver):
    username = conf.fb_username
    password = conf.fb_password
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Extract visible text from the parsed 
    if "sign up" in soup.get_text().lower():
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
