from selenium.webdriver.chrome.options import Options

try:
    import undetected_chromedriver as webdriver

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=chrome_options)
    browser.quit()
except:
    import chromedriver_autoinstaller

    chromedriver_autoinstaller.install()
    from selenium import webdriver
import os
from urllib.parse import urlparse
from pathlib import Path
from database import *
import requests
from datetime import datetime

def scroll_post(driver, posts=1):
    for i in range(posts):
        scroll_step = 10
        total_steps = 77
        for step in range(total_steps):
            driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            driver.implicitly_wait(0.1)  # Wait to create a smooth scroll effect


def download_file(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_data = response.content
            return file_data
        else:
            print(f"Failed to download the file from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
