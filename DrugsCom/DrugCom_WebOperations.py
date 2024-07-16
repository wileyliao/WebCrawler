import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def initialize_driver():
    options = webdriver.EdgeOptions()
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)
    return driver

def wait_and_get_element(driver, by, value, timeout=20):
    time.sleep(random.uniform(1, 1.5))
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except:
        raise

def send_input(element, text):
    time.sleep(random.uniform(0.5, 0.8))
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.02, 0.05))
    element.send_keys(Keys.ENTER)

def clear_input(element):
    time.sleep(random.uniform(0.5, 0.8))
    text_length = len(element.get_attribute('value'))
    while text_length > 0:
        element.send_keys(Keys.BACKSPACE)
        text_length -= 1
        time.sleep(random.uniform(0.02, 0.05))
    time.sleep(random.uniform(0.2, 0.5))
    element.send_keys(Keys.BACKSPACE)

def click_element(driver, element):
    time.sleep(random.uniform(0.5, 0.8))
    try:
        driver.execute_script("arguments[0].click();", element)
    except Exception:
        raise

def extract_info(driver, by, value, timeout):
    time.sleep(random.uniform(0.5, 0.8))
    info_object = wait_and_get_element(driver, by, value, timeout)
    if info_object is None:
        return ""
    info = driver.find_elements(by, value)
    info_text = " ".join([element.text for element in info])
    return info_text

def dialogs_check(driver, by, value, attribute, drug):
    time.sleep(random.uniform(0.5, 0.8))
    dialogs = driver.find_elements(by, value)
    if dialogs and dialogs[0].get_attribute(attribute) is not None:
        return drug

def restart_driver(driver, url):
    driver.quit()
    driver = initialize_driver()
    driver.get(url)
    wait_and_get_element(driver, By.ID, 'livesearch-interaction-basic', 20)
    return driver
