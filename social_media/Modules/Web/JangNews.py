import requests
from bs4 import BeautifulSoup
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

# Step 1: Web Scraping
url = "https://jang.com.pk/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the first image URL from the webpage
img_tag = soup.find('img')
image_url = img_tag['src']

# Download the image
image_response = requests.get(image_url)
image_bytes = BytesIO(image_response.content)
img = cv2.imdecode(np.array(Image.open(image_bytes)), cv2.IMREAD_COLOR)

# Step 2: Image Recognition
template_path = "object.jpg"
template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
w, h = template.shape[::-1]

gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

res = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.8
loc = np.where(res >= threshold)

# Step 3: Coordinates
for pt in zip(*loc[::-1]):
    print(f"Image found at coordinates: {pt}")
    # You can perform further actions with the coordinates, such as drawing a rectangle
    cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)

# Display the image with rectangles around the detected templates
cv2.imshow('Detected Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
