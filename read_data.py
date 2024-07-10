import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import random

options = webdriver.EdgeOptions()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')

# 設置 WebDriver
service = EdgeService(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=service, options=options)

def slow_send_keys(element, text):
    """
    緩慢地將文本輸入到指定元素中
    """
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.12))

def slow_clear(element):
    """
    緩慢地清除指定元素中的文本
    """
    text_length = len(element.get_attribute('value'))
    while text_length > 0:
        element.send_keys('\b')
        text_length -= 1
        time.sleep(random.uniform(0.05, 0.12))

def send_medicine(input_box, medicine):
    """
    輸入藥品名稱並選擇下拉框中的唯一項目
    """
    slow_clear(input_box)
    slow_send_keys(input_box, medicine)

    # 檢查是否顯示 No Results
    no_results = driver.find_element(By.ID, 'MDICldrugnor')
    if no_results.value_of_css_property('display') == 'block':
        print(f'No results found for {medicine}')
        return False

    # 等待 <ul id="MDICdrugs"> 列表出現
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'MDICdrugs'))
    )
    time.sleep(random.uniform(0.7, 1))

    # 等待 <li class="activeItem"> 項目變為唯一
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, '#MDICdrugs li.activeItem')) == 1
    )
    time.sleep(random.uniform(0.8, 1.2))

    # 選擇唯一的 <li class="activeItem"> 項目中的 <a> 標籤
    first_result = driver.find_element(By.CSS_SELECTOR, '#MDICdrugs li.activeItem a')
    first_result.click()
    return True


def main():
    # 打開目標URL
    driver.get('https://reference.medscape.com/drug-interactionchecker')

    # 等待網頁載入
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'MDICtextbox'))
    )

    # 找到輸入框，使用ID為 'MDICtextbox'
    input_box = driver.find_element(By.ID, 'MDICtextbox')

    # 輸入並查詢第一個藥品名稱
    send_medicine(input_box, 'acebutolol')
    time.sleep(random.uniform(0.7, 1))
    # 輸入並查詢第二個藥品名稱
    send_medicine(input_box, 'salsalate')

    # 等待結果頁面載入，並等待 intcheck_intfound 顯示
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, 'intcheck_intfound').value_of_css_property('display') == 'block'
    )

    # 獲取 <p> 標籤的內容
    significant_list = driver.find_element(By.ID, 'significant_list')
    interaction_items = significant_list.find_elements(By.TAG_NAME, 'li')

    for item in interaction_items:
        header = item.find_element(By.TAG_NAME, 'h4').text
        paragraph = item.find_element(By.TAG_NAME, 'p').text
        print(f'{header}：{paragraph}')

    # 點擊 "Clear All" 按鈕
    time.sleep(random.uniform(0.7, 1))
    clear_all_btn = driver.find_element(By.ID, 'clearallbtn').find_element(By.TAG_NAME, 'a')
    clear_all_btn.click()

    time.sleep(random.uniform(0.7, 1))
    # 等待並點擊彈窗中的 "Clear" 按鈕
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'clearallalert'))
    )
    time.sleep(random.uniform(0.7, 1))
    confirm_clear_btn = driver.find_element(By.ID, 'subclearbtn').find_element(By.TAG_NAME, 'a')
    confirm_clear_btn.click()
    time.sleep(random.uniform(0.7, 1))

if __name__ == '__main__':
    main()
    driver.quit()

