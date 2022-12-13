import pickle
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from config import db
import cv2

# читать изображение QRCODE

options = webdriver.ChromeOptions()

options.add_argument("--user-data-dir=C:\\Users\\hdhrh\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")
options.add_argument("--disable-extensions")


def sender():
    href_list = db.get_all_groups()
    with open("interval.txt", 'r', encoding="utf-8") as f:
        interval = int(f.read())

    driver = webdriver.Chrome(executable_path="webdriver/chromedriver.exe", options=options)
    try:
        registered = False
        while True:
            if not registered:
                driver.get("https://t.me/testgroup127")
                time.sleep(3)

                group_href = driver.find_element(By.CLASS_NAME, "tgme_action_web_button").get_property("href")
                driver.get(group_href)

                time.sleep(10)
                registered = True
            for h in href_list:
                driver.get(h)
                time.sleep(3)

                group_href = driver.find_element(By.CLASS_NAME, "tgme_action_web_button").get_property("href")
                driver.get(group_href)
                time.sleep(4)

                try:
                    driver.find_elements(By.CLASS_NAME, "primary")[1].click()
                except:
                    pass
                time.sleep(4)
                try:
                    with open("message.txt", 'r', encoding="utf-8") as f:
                        msg = f.read().split('\n')

                    driver.find_element(By.ID, "editable-message-text").send_keys("\n".join(msg))
                    time.sleep(2)
                    driver.find_element(By.CLASS_NAME, "click-allowed").click()
                    time.sleep(3)
                except Exception as e:
                    print(e)
            time.sleep(interval)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    sender()
