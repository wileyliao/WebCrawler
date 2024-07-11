import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import random

def initialize_driver():
    options = webdriver.EdgeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')

    # 設置 WebDriver
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)
    return driver

def send_input(element, text):
    """
    緩慢地將文本輸入到指定元素中
    """
    print("keying drug.........")
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.02, 0.05))
    element.send_keys(Keys.ENTER)
    time.sleep(random.uniform(0.02, 0.05))


def clear_input(element):
    """
    緩慢地清除指定元素中的文本
    """
    print("deleting drug.........")
    text_length = len(element.get_attribute('value'))
    while text_length > 0:
        element.send_keys(Keys.BACKSPACE)
        text_length -= 1
        time.sleep(random.uniform(0.02, 0.05))
    time.sleep(random.uniform(0.2, 0.5))
    element.send_keys(Keys.BACKSPACE)
    time.sleep(random.uniform(0.2, 0.5))

def wait_for_element(driver, by, value, timeout):
    """
    等待元素出現
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except:
        return None

def click_element(driver, by, value, timeout):
    """
    等待元素出現並點擊
    """
    element = wait_for_element(driver, by, value, timeout)
    if element:
        element.click()
        return True
    else:
        print(f"Element not found: {by} {value}")
        return False


driver = initialize_driver()

def main():
    try:
        driver.get('https://www.drugs.com/drug_interactions.html')

        # 等待並定位第一個輸入框
        input_box = wait_for_element(driver, By.ID, 'livesearch-interaction-basic', 20)
        # 輸入第一個藥物名稱並按下Enter
        send_input(input_box, 'Abacavir')
        time.sleep(random.uniform(0.5, 0.8))

        # 等待頁面刷新後的新輸入框出現
        input_box = wait_for_element(driver, By.ID, 'livesearch-interaction', 20)
        time.sleep(random.uniform(0.5, 0.8))

        # 清除新輸入框的內容
        clear_input(input_box)
        time.sleep(random.uniform(0.5, 0.8))
        # 輸入第二個藥物名稱
        send_input(input_box, 'Ethanol')
        time.sleep(random.uniform(0.5, 0.8))
        click_element(driver, By.LINK_TEXT, 'Check Interactions', 1)

        # 給點時間觀察結果
        time.sleep(10)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()