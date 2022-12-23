import requests
import numpy as np
import random
import cv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import os
from dotenv import load_dotenv
import json


def overlay_transparent(background, overlay, x, y):
    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype=overlay.dtype) * 255
            ],
            axis=2,
        )

    overlay_image = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    background[y:y + h, x:x + w] = (1.0 - mask) * background[y:y + h, x:x + w] + mask * overlay_image

    return background


def get_high_quality_images(keyword):

    # Uses selenium to virtually click on the high res versions of the images
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, service=Service(GeckoDriverManager().install()))
    driver.get(f"https://www.google.com/search?q={keyword}&source=lnms&tbm=isch&source=hp&biw=1680")

    while True:
        element = driver.find_element(By.XPATH, f'//*[@id="islrg"]/div[1]/div[{random.randint(1,3)}]/a[1]')
        element.click()
        time.sleep(.5)
        image_link = driver.find_element(By.CSS_SELECTOR, ".tvh9oe.BIB1wf .eHAdSb>img").get_attribute("src")
        if image_link[0:4] != "data":
            break

    driver.quit()
    return image_link


def get_keywords(image_link):

    response = requests.get(f"https://serpapi.com/search.json?engine=google_reverse_image&image_url={image_link}&api_key={os.getenv('API_KEY')}")
    rjson = json.loads(response.content)
    words = {}

    for dictionary in rjson["image_results"]:

        for word in dictionary["title"].split():
            if word in words:
                words[word] += 1
            else:
                words[word] = 1

        for word in dictionary["snippet"].split():
            if word in words:
                words[word] += 1
            else:
                words[word] = 1

    maximum = 0
    max_word = "Daft"
    for i in words:
        if words[i] > maximum and i != "the":
            max_word = i
            maximum = words[i]

    return max_word


def place_image(bg_img, new_image, pos):
    if pos == 1:
        return overlay_transparent(bg_img, new_image, 0, 0)
    elif pos == 2:
        return overlay_transparent(bg_img, new_image, 500, 0)
    elif pos == 3:
        return overlay_transparent(bg_img, new_image, 0, 500)
    else:
        return overlay_transparent(bg_img, new_image, 500, 500)


def store_as_opencv_object(image_link):

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0"
    }

    # Makes a request to the image source and stores the byte string of the image
    new_response = requests.get(image_link, headers=headers)

    # Stores image as OpenCV object
    nparr = np.frombuffer(new_response.content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


if __name__ == '__main__':
    bg = np.zeros((1000, 1000, 3), dtype=np.uint8)
    arrows = cv2.imread('overlay.png', cv2.IMREAD_UNCHANGED)
    images = []

    image_1 = input("What is the link for the starting image? ")
    images.append(store_as_opencv_object(image_1))
    image_2 = get_high_quality_images(get_keywords(image_1))
    images.append(store_as_opencv_object(image_2))
    image_3 = get_high_quality_images(get_keywords(image_2))
    images.append(store_as_opencv_object(image_3))
    image_4 = get_high_quality_images(get_keywords(image_3))
    images.append(store_as_opencv_object(image_4))

    x = 1
    for i in images:
        bg = place_image(bg, i, x)
        x += 1

    cv2.imwrite("Result.png", bg)
    cv2.imshow("result", bg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



