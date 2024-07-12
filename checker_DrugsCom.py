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
    點擊元素(隱藏的也可)
    """
    try:
        element = wait_for_element(driver, by, value, timeout)
        if element:
            driver.execute_script("arguments[0].click();", element)
            return True
        else:
            raise Exception(f"Element not found: {by} {value}")
    except Exception as e:
        print(f"Exception occurred while clicking element")
        return False


def search_pairs(driver, drug_1, drug_2, skipped_drugs_1, skipped_drugs_2):
    try:
        # 等待並定位第一個輸入框
        input_box = wait_for_element(driver, By.ID, 'livesearch-interaction-basic', 20)
        if input_box is None:
            raise Exception(f'Input box for {drug_1} not found!!!')
        send_input(input_box, drug_1)
        time.sleep(random.uniform(0.5, 0.8))
        # 等待頁面刷新後的新輸入框出現
        input_box = wait_for_element(driver, By.ID, 'livesearch-interaction', 20)
        if input_box is None:
            raise Exception(f"Input box for {drug_2} not found!!!")
        time.sleep(random.uniform(0.5, 0.8))
        clear_input(input_box)
        time.sleep(random.uniform(0.5, 0.8))
    except Exception:
        print(f"Error in search_pairs with drug {drug_1}")
        skipped_drugs_1.add(drug_1)
        return drug_1

    try:
        # 輸入第二個藥物名稱
        send_input(input_box, drug_2)
        time.sleep(random.uniform(0.5, 0.8))
    except Exception as e:
        print(f"Error in search_pairs with drug {drug_2}")
        skipped_drugs_2.add(drug_2)
        return drug_2
    return None

def extract_info(driver):
    """
    提取交互作用資訊
    """
    # 等待 class 為 interactions-reference-header 的 <p> 出現
    interaction = driver.find_elements(By.CSS_SELECTOR, '.interactions-reference p')
    info = " ".join([element.text for element in interaction])
    return info

def restart_driver(url):
    global driver
    driver.quit()
    driver = initialize_driver()
    driver.get(url)
    wait_for_element(driver, By.TAG_NAME, 'body', 20)
    return driver



driver = initialize_driver()
def main():
    global driver
    url = 'https://www.drugs.com/drug_interactions.html'
    file = 'DrugCom_results.xlsx'

    df = pd.read_excel(file)
    df['interactions_DrugCom'] = df['interactions_DrugCom'].astype(object)

    driver.get(url)
    wait_for_element(driver, By.TAG_NAME, 'body', 20)

    skipped_drugs_1 = set()  # 用來記錄查不到結果的 drug_1
    skipped_drugs_2 = set()  # 用來記錄查不到結果的 drug_2
    count = 0

    for index, row in df.iterrows():
        try:
            if pd.notna(row['interactions_DrugCom']):
                print(f'{index}: Skipped as interactions already have value')
                continue
            print(f'-----------round{count}----------')

            if count > 8:
                print('Restart.......')
                restart_driver(url)
                count = 0

            drug_1 = row['drug_1']
            drug_2 = row['drug_2']

            if drug_1 in skipped_drugs_1:
                df.at[index, 'interactions_DrugCom'] = f'{drug_1} No results'
                print(f'{index}: Skipped {drug_1} as it was previously found to have no results')
                continue

            if drug_2 in skipped_drugs_2:
                df.at[index, 'interactions_DrugCom'] = f'{drug_2} No results'
                print(f'{index}: Skipped {drug_2} as it was previously found to have no results')
                continue
            time.sleep(random.uniform(0.5, 0.8))
            click_element(
                driver,
                By.XPATH,
                '//a[@href="/drug_interactions.html" and contains(text(), '
                '"Interaction Checker")]',
                10
            )
            time.sleep(random.uniform(0.5, 0.8))

            error_drug = search_pairs(driver, drug_1, drug_2, skipped_drugs_1, skipped_drugs_2)
            count += 1
            if error_drug:
                print(f"{index}: Skipped {error_drug} as it caused an error")
                df.at[index, 'interactions_DrugCom'] = f'{error_drug} No results'
                continue
            print('Getting interaction........')
            time.sleep(random.uniform(1, 1.5))
            click_element(driver, By.LINK_TEXT, 'Check Interactions', 5)
            time.sleep(random.uniform(0.5, 0.8))
            click_element(driver, By.LINK_TEXT, 'Professional', 5)
            time.sleep(random.uniform(0.5, 0.8))
            interactions = (extract_info(driver))
            print(f'{drug_1} + {drug_2}: {interactions}')
            time.sleep(random.uniform(0.5, 0.8))
            df.at[index, 'interactions_DrugCom'] = ''.join(interactions)
            df.to_excel(file, index=False)

        except Exception as e:
            print(f"Exception encountered")
            df.at[index, 'interactions_DrugCom'] = f'No results'
            restart_driver(url)
            count = 0


if __name__ == "__main__":
    main()
    driver.quit()