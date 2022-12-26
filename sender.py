import getpass
import pickle
import platform
import time

import asyncio

import pyperclip
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from config import db, bot


# options = Options()

# chrome_driver_binary = "C:\\Users\\hdhrh\\PycharmProjects\\group_sendeer\\webdriver\\chromedriver.exe"
#
# options.add_argument(f"user-data-dir=C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Google\\Chrome\\User Data")
# options.add_argument("profile-directory=Profile 1")


async def sender():
    with open("чаты люди.txt", 'r', encoding="utf-8") as f3:
        href_list = list(set(f3.read().split('\n') + db.get_all_groups()))

    with open("interval.txt", 'r', encoding="utf-8") as f:
        interval = int(f.read())
    driver = webdriver.Chrome("webdriver/chromedriver.exe")
    while True:
        try:
            registered = bool(int(open("is_registered.txt", "r", encoding="utf-8").read()))
            is_stopped = bool(int(open("is_stopped.txt", 'r', encoding="utf-8").read()))
            if not is_stopped:
                if not registered:
                    driver.get("https://web.telegram.org/")
                    time.sleep(40)

                    with open("is_registered.txt", 'w') as f2:
                        f2.write("1")
                for h in href_list:
                    driver.get(h)
                    time.sleep(3)

                    group_href = driver.find_element(By.CLASS_NAME, "tgme_action_web_button").get_property("href")
                    driver.get(group_href)
                    driver.fullscreen_window()
                    time.sleep(4)

                    try:
                        [el.click() for el in driver.find_elements(By.TAG_NAME, "button") if
                         "join" in el.text.lower() or "subscribe" in el.text.lower()]
                    except Exception as e:
                        print("already joined")
                    with open("message.txt", 'r', encoding="utf-8") as f:
                        msg = f.read()

                    try:
                        msg_input = driver.find_element(By.ID, "editable-message-text")
                        print("thats what i need")
                        time.sleep(20)
                    except Exception as e:
                        try:
                            msg_input = driver.find_element(By.CLASS_NAME, "input-message-input")
                        except:
                            msg_input = None
                            print("Not Found")
                            time.sleep(5)
                    JS_ADD_TEXT_TO_INPUT = """
                              var elm = document.querySelector("#editable-message-text"); 
                              if (elm === null) {
                                elm = document.querySelector(".input-message-input");
                              }
                              let txt = arguments[0];
                              elm.innerHTML = txt;
                              elm.dispatchEvent(new Event('change'));
                              """

                    if msg_input is not None:
                        driver.execute_script(JS_ADD_TEXT_TO_INPUT, msg)
                        time.sleep(17)

                        msg_input.send_keys(Keys.ENTER)
                    time.sleep(4)
                time.sleep(interval)
        except Exception as e:
            await bot.send_message(818525681, "Похоже, вы были не зарегестрированы")
            with open("is_registered.txt", 'w') as f:
                f.write("0")


def wrapper():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(sender())
    loop.close()


if __name__ == '__main__':
    wrapper()
