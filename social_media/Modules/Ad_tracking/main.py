from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import cv2
import numpy as np
import os
import pandas as pd
from .utility import *
from selenium.webdriver.common.by import By
import concurrent.futures
from ...models import *
from datetime import datetime,date

from django.db.models import Q
def search_and_highlight(template_path, target_path, output_path, page_width, page_height):
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    target = cv2.imread(target_path)
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)
    top_left = max_loc
    h, w = template.shape[:2]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    highlighted_image = target.copy()
    cv2.rectangle(highlighted_image, top_left, bottom_right, (0, 0, 255), 2)

    box_center_x = (top_left[0] + bottom_right[0]) // 2
    box_center_y = (top_left[1] + bottom_right[1]) // 2

    page_center_x = page_width // 2
    page_center_y = page_height // 2

    print("----------------------------- Box Center X ----------------------")
    print(box_center_x)
    print("----------------------------- Box Center Y ----------------------")
    print(box_center_y)
    print("----------------------------- Page Center X ----------------------")
    print(page_center_x)
    print("----------------------------- Page Center Y ----------------------")
    print(page_center_y)

    print(f"Top Left Coordinates: {top_left}")
    print(type(top_left))
    print(f"Bottom Right Coordinates: {bottom_right}")
    print(type(bottom_right))
    print(
        f"Position Relative to Page: ({top_left[0]}, {top_left[1]}) to ({bottom_right[0]}, {bottom_right[1]})"
    )

    # Define a threshold for considering it as near the center horizontally
    threshold_horizontal = 50

    if (
            abs(box_center_x - page_center_x) < threshold_horizontal
            and box_center_y < page_center_y
    ):
        position = "TOP CENTER"
        print("The bounding box is in the TOP CENTER of the page.")
    elif box_center_x < page_center_x:
        if box_center_y < page_center_y:
            position = "TOP LEFT"
            print("The bounding box is in the TOP LEFT of the page.")
        elif box_center_y > page_center_y:
            position = "BOTTOM LEFT"
            print("The bounding box is in the BOTTOM LEFT of the page.")
        else:
            position = "LEFT CENTER"
            print("The bounding box is in the LEFT CENTER of the page.")
    elif box_center_x > page_center_x:
        if box_center_y < page_center_y:
            position = "TOP RIGHT"
            print("The bounding box is in the TOP RIGHT of the page.")
        elif box_center_y > page_center_y:
            position = "BOTTOM RIGHT"
            print("The bounding box is in the BOTTOM RIGHT of the page.")
        else:
            position = "RIGHT CENTER"
            print("The bounding box is in the RIGHT CENTER of the page.")
    else:
        if box_center_y < page_center_y:
            position = "TOP CENTER"
            print("The bounding box is in the TOP CENTER of the page.")
        elif box_center_y > page_center_y:
            position = "BOTTOM CENTER"
            print("The bounding box is in the BOTTOM CENTER of the page.")
        else:
            position = "UNKNOWN"

    cv2.imwrite(output_path, highlighted_image)

    # Return the bounding box information
    return {
        "image_path": output_path,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "top_left_coordinates": top_left,
        "bottom_right_coordinates": bottom_right,
        "position_relative_to_page": f"({top_left[0]}, {top_left[1]}) to ({bottom_right[0]}, {bottom_right[1]})",
        "position": position,
    }


def search_and_highlight_batch(template_path, target_directory, output_parent_directory, link):
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if not os.path.exists(output_parent_directory):
        os.makedirs(output_parent_directory)

    results = []

    # Extract the template image name without extension
    template_name = os.path.splitext(os.path.basename(template_path))[0]
    output_directory = os.path.join(output_parent_directory, template_name)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(os.path.join(target_directory,get_folder_name(link))):
            if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                target_path = os.path.join(target_directory,get_folder_name(link), filename)
                output_path = os.path.join(output_directory, f"highlighted_{filename}")

                try:
                    target = cv2.imread(target_path)
                    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
                    _, _, _, max_loc = cv2.minMaxLoc(result)
                    match_accuracy = result[max_loc[1], max_loc[0]]
                    if match_accuracy > 0.9:
                        result = search_and_highlight(template_path, target_path, output_path, page_width=1920,
                                                      page_height=1080)
                        result['image'] = save_image_to_binary(result['image_path'])
                        result['ad_name'] = template_name  # Use the template name instead of the full path
                        result['url'] = link
                        results.append(result)
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")

    return results


def take_screenshot(driver, file_path):
    # Set higher resolution and pixel density
    driver.set_window_size(1920, 1080)  # You can adjust the resolution as needed
    driver.execute_script("document.body.style.zoom='100%'")  # Set pixel density to 100%

    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")

    for i in range(0, total_height, viewport_height):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(2)

        screenshot = driver.get_screenshot_as_png()
        screenshot_image = cv2.imdecode(np.frombuffer(screenshot, np.uint8), 1)

        # Save each screenshot individually with a unique filename
        screenshot_filename = os.path.join(file_path, f"screenshot_{i}.jpg")
        cv2.imwrite(screenshot_filename, screenshot_image)


def get_folder_name(url):
    try:
        folder = url.split('/')[-1]
        if folder == "":
            folder = 'extras'
            return folder
        return folder
    except:
        folder = 'extras'
        return folder


def screen_shot_all(url,driver):
    try:
        driver.get(url)
        time.sleep(10)
        folder = get_folder_name(url)
        dir = f'social_media/Modules/Ad_tracking/images/{folder}'
        if not os.path.exists(dir):
            os.mkdir(dir)
        take_screenshot(driver, dir)
    except:
        pass


def detected_ads(url,source):
    print(url)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome()
    if not os.path.exists("social_media/Modules/Ad_tracking/images"):
        os.mkdir("social_media/Modules/Ad_tracking/images")
    # take_screenshot(driver, 'social_media/Modules/Ad_tracking/images')
    screen_shot_all(url,driver)
    
    driver.close()
    results = []
    today=date.today()
    images=Ads_table.objects.filter(source=source,tracking=True,start_date__lte=today).filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
    image_values = [instance.template_path for instance in images]
    for image in image_values:
        print(image)
        results.extend(search_and_highlight_batch(image, 'social_media/Modules/Ad_tracking/images', 'social_media/Modules/Ad_tracking/result'))
    detected_results = [result for result in results if "image_path" in result]
    # for result in detected_results:
    print("-----"*10)
    
    df=pd.DataFrame(detected_results)
    count=0
    if len(df)>0:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        for index,row in df.iterrows():
            try:
                ad_instance = Ads_table.objects.get(ad_name=row['ad_name'])
                print(ad_instance)
                date=row['timestamp'].date()
                hour=row['timestamp'].hour
                minute=row['timestamp'].minute
                if web_ads.objects.filter(Q(timestamp__date=date, timestamp__hour=hour, timestamp__minute=minute) & Q(ad_name=ad_instance)).count()<=0:
                    instance = web_ads(
                        timestamp=row['timestamp'],
                        top_left_coordinates=row['top_left_coordinates'],
                        bottom_right_coordinates=row['bottom_right_coordinates'],
                        position_relative_to_page=row['position_relative_to_page'],
                        position=row['position'],
                        image=row['image'],
                        ad_name=ad_instance,
                    )
                    instance.save()
                    print("web_ads saved")
                    count+=1
                else:
                    print("Already Exists")
            except Ads_table.DoesNotExist:
                # Handle the case when the object doesn't exist
                print(f"Ads_table with ad_name {row['ad_name']} does not exist.")
            
            except:
                print("web_ads not saved")
    print("Ads saved",count)
    # return count, "AD tracking done"
    # df.to_csv('detected_results.csv', index=False)
    # return df

def ads_detection(source):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome()
    if source=="urdu_point":
        driver.get('https://www.urdupoint.com/')
    elif source=="jang_news":
        driver.get('https://jang.com.pk/')
    elif source=="hum_news":
        driver.get('https://humnews.pk/')
    # driver.get(link)

    time.sleep(5)
    links = driver.find_elements(By.TAG_NAME, 'a')
    
    urls = set()
    for link in links:
        try:
            urls.add(link.get_attribute('href'))
        except Exception as e:
            print(e)
            pass
    urls = list(urls)
    urls.insert(0,driver.current_url)
    driver.close()
    print(urls)
    for url in urls:
        detected_ads(url)
    # df = df.drop('Image_path', axis=1)
    # df = pd.DataFrame(detected_results)
    # print(df)
    remove_files_from_directory('social_media/Modules/Ad_tracking/images')


# if __name__ == "__main__":
#     start_time = time.time()
#     # 'https://www.urdupoint.com/'
#     # 'https://humnews.pk/'
#     "https://jang.com.pk/"
#     main('https://humnews.pk/')
#     # session.close()
#     end_time = time.time()
#     elapsed_time = end_time - start_time
#     print(f"Elapsed time: {elapsed_time:.2f} seconds")
