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

    for dict in rjson["image_results"]:

        for word in dict["title"].split():
            if word in words:
                words[word] += 1
            else:
                words[word] = 1

        for word in dict["snippet"].split():
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
    pass

if __name__ == '__main__':
    bg = np.zeros((1000, 1000, 3), dtype=np.uint8)




