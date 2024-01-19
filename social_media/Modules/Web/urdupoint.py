from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import cv2
import numpy as np
import os

def search_and_highlight(template_path, target_path, output_path, page_width):
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
    print(f"Top Left Coordinates: {top_left}")
    print(f"Bottom Right Coordinates: {bottom_right}")
    print(f"Position Relative to Page: ({top_left[0]}, {top_left[1]}) to ({bottom_right[0]}, {bottom_right[1]})")
    if box_center_x < page_center_x:
        print("The bounding box is on the LEFT side of the page.")
    else:
        print("The bounding box is on the RIGHT side of the page.")
    cv2.imwrite(output_path, highlighted_image)

def search_and_highlight_batch(template_path, target_directory, output_directory):
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

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
                    search_and_highlight(template_path, target_path, output_path,page_width=1920)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

def take_screenshot(driver, file_path):
    # Set higher resolution and pixel density
    driver.set_window_size(1920, 1080)  # You can adjust the resolution as needed
    driver.execute_script("document.body.style.zoom='100%'")  # Set pixel density to 100%

    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")

    for i in range(0, total_height, viewport_height):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(0.2)

        screenshot = driver.get_screenshot_as_png()
        screenshot_image = cv2.imdecode(np.frombuffer(screenshot, np.uint8), 1)

        # Save each screenshot individually with a unique filename
        screenshot_filename = os.path.join(file_path, f"screenshot_{i}.jpg")
        cv2.imwrite(screenshot_filename, screenshot_image)

def main():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox()
    driver.get('https://www.urdupoint.com/')
    take_screenshot(driver, 'images/')
    driver.quit()
    for image in os.listdir('templates'):
        print(image)
        search_and_highlight_batch("templates/"+image, 'images', 'result')
    

if __name__ == "__main__":
    main()
