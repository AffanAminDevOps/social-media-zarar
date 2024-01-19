from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import cv2
import numpy as np
import os
import pandas as pd
from .utility import *
# from ads_database import *
from usp.tree import sitemap_tree_for_homepage
from ...models import *
from datetime import date
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



def search_and_highlight_batch(template_path, target_directory, output_directory):
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    results = []

    for filename in os.listdir(target_directory):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            target_path = os.path.join(target_directory, filename)
            output_path = os.path.join(output_directory, f"highlighted_{filename}")

            try:
                
                target = cv2.imread(target_path)
                result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
                _, _, _, max_loc = cv2.minMaxLoc(result)
                match_accuracy = result[max_loc[1], max_loc[0]]
                if match_accuracy > 0.7:
                    result = search_and_highlight(template_path, target_path, output_path, page_width=1920, page_height=1080)
                    print("Template path",template_path)
                    ad_obj=Ads_table.objects.get(template_path=template_path)
                    result['image']=save_image_to_binary(result['image_path'])
                    result['ad_name']=ad_obj.ad_name#os.path.basename(template_path)#template_path.split('/')[-1]
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



def urdu_point_ads(source="urdu_point"):
    # db=Database()
    # session=db.create_session()
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox()
    if source=="urdu_point":
        driver.get('https://www.urdupoint.com/')
    if not os.path.exists("social_media/Modules/Ad_tracking/images"):
        os.mkdir("social_media/Modules/Ad_tracking/images")
    take_screenshot(driver, 'social_media/Modules/Ad_tracking/images')
    driver.quit()

    results = []
    today=date.today()
    images=Ads_table.objects.filter(source=source,tracking=True,start_date__lte=today).filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
    image_values = [instance.template_path for instance in images]
    for image in image_values:
        print(image)
        results.extend(search_and_highlight_batch(image, 'social_media/Modules/Ad_tracking/images', 'social_media/Modules/Ad_tracking/result'))
    detected_results = [result for result in results if "image_path" in result]
    print("-----"*10)
    # for result in detected_results:
    #         ad_entry = Ads(timestamp=result['timestamp'], top_left_coordinates=str(result['top_left_coordinates']), bottom_right_coordinates=str(result['bottom_right_coordinates']),
    #                           position_relative_to_page=str(result['position_relative_to_page']), position=result['position'],
    #                           image=result['image'],ad_name=result['ad_name'])
    #         session.add(ad_entry)
    #         print("Data added to db")
    # session.commit()
    # df = df.drop('Image_path', axis=1)
    # df = pd.DataFrame(detected_results)
    # print(df)
    remove_files_from_directory('social_media/Modules/Ad_tracking/images')
    remove_files_from_directory('social_media/Modules/Ad_tracking/result')
    df=pd.DataFrame(detected_results)
    df.to_csv('detected_results.csv', index=False)
    return df

# if __name__ == "__main__":
#     df=main()
#     print(df)
#     tree = sitemap_tree_for_homepage('https://www.urdupoint.com/')
#     print(tree)