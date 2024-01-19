from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import os
from urllib.parse import urlparse
from pathlib import Path
import requests
from datetime import datetime


def find_link_in_string(input_string):
    try:
        words = input_string.split()

        for word in words:
            parsed_url = urlparse(word)
            if parsed_url.scheme and parsed_url.netloc:
                return parsed_url.geturl()

        return None
    except:
        return None


def find_value_by_key(dictionary, target_key):
    if isinstance(dictionary, dict):
        for key, value in dictionary.items():
            if key == target_key:
                return value
            elif isinstance(value, (dict, list)):
                result = find_value_by_key(value, target_key)
                if result is not None:
                    return result
    elif isinstance(dictionary, list):
        for tweet_dict in dictionary:
            if isinstance(tweet_dict, (dict, list)):
                result = find_value_by_key(tweet_dict, target_key)
                if result is not None:
                    return result

    return None


def find_all_values_by_key(obj, target_key):
    results = []

    def recursive_search(dictionary):
        if isinstance(dictionary, dict):
            for key, value in dictionary.items():
                if key == target_key:
                    results.append(value)
                elif isinstance(value, (dict, list)):
                    recursive_search(value)
        elif isinstance(dictionary, list):
            for item in dictionary:
                if isinstance(item, (dict, list)):
                    recursive_search(item)

    recursive_search(obj)
    return results


def open_profile(profile="-", new=False, headless=False):
    if profile == "-":
        new = True
    if new:
        if headless:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            browser = webdriver.Firefox(options=chrome_options)
        else:
            browser = webdriver.Firefox()

    else:
        current_directory = os.getcwd()
        print("Opening Profile:", current_directory, fr"\{profile}")
        user_data_dir = Path(rf"{current_directory}\{profile}")
        chrome_options = Options()

        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')

        chrome_options.add_argument("--user-data-dir={}".format(user_data_dir))
        chrome_options.add_argument('--profile-directory=Default')
        browser = webdriver.Firefox(options=chrome_options)
    if not headless:
        width = 1080
        height = 740
        browser.set_window_size(width, height)

    return browser


def scroll_post(driver, posts=1):
    for i in range(posts):
        # Define the scroll step size and total steps
        scroll_step = 10  # Adjust the step size as needed
        total_steps = 77  # Adjust the total number of steps as needed
        # Perform slow scroll down the page
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
