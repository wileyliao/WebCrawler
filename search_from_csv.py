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
        time.sleep(random.uniform(0.02, 0.05))

def slow_clear(element):
    """
    緩慢地清除指定元素中的文本
    """
    text_length = len(element.get_attribute('value'))
    while text_length > 0:
        element.send_keys('\b')
        text_length -= 1
        time.sleep(random.uniform(0.02, 0.05))
    time.sleep(random.uniform(0.2, 0.5))
    element.send_keys('\b')
    time.sleep(random.uniform(0.2, 0.5))
    element.send_keys('\b')

def clear_all_interactions(driver):
    """
    點擊 "Clear All" 按鈕並確認清除所有交互信息
    """
    try:
        time.sleep(random.uniform(0.2, 0.5))
        clear_all_btn_container = driver.find_element(By.ID, 'clearallbtn')

        # 檢查 clearallbtn 是否顯示
        if clear_all_btn_container.value_of_css_property('display') == 'block':
            clear_all_btn = clear_all_btn_container.find_element(By.TAG_NAME, 'a')
            clear_all_btn.click()

            time.sleep(random.uniform(0.7, 1))
            # 等待並點擊彈窗中的 "Clear" 按鈕
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'clearallalert'))
            )
            confirm_clear_btn = driver.find_element(By.ID, 'subclearbtn').find_element(By.TAG_NAME, 'a')
            confirm_clear_btn.click()
            time.sleep(random.uniform(0.7, 1))
    except Exception as e:
        print(f"Exception encountered while trying to clear interactions")
        pass

def send_medicine(input_box, medicine):
    """
    輸入藥品名稱並選擇下拉框中的唯一項目
    """
    slow_clear(input_box)
    slow_send_keys(input_box, medicine)
    time.sleep(random.uniform(0.5, 0.8))
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, 'MDICdrugs'))
    )

    # 檢查是否顯示 No Results 或有結果
    try:
        time.sleep(random.uniform(0.5, 0.8))
        # 等待 'MDICilfulllist' 的 'display' 屬性為 'block'
        WebDriverWait(driver, 20).until(
            lambda d: d.find_element(By.ID, 'MDICilfulllist').value_of_css_property('display') == 'block'
        )

        # 檢查 'MDICildrugnor' 的 'display' 屬性是否為 'none' 或 'MDICdrugs' 中是否有 'activeItem'
        no_results = driver.find_element(By.ID, 'MDICildrugnor')
        active_items = driver.find_elements(By.CSS_SELECTOR, '#MDICdrugs li.activeItem')

        if no_results.value_of_css_property('display') == 'none' and len(active_items) > 0:
            # 點擊第一個結果
            time.sleep(random.uniform(0.5, 0.8))
            first_result = active_items[0].find_element(By.TAG_NAME, 'a')
            first_result.click()
            time.sleep(random.uniform(0.5, 0.8))
            return True
        else:
            slow_clear(input_box)
            print(f'No results found for {medicine}')
            return False
    except:
        print(f'No results found for {medicine}')
        return False

def extract_interactions():
    """
    提取所有交互信息
    """
    interaction_ids = ['contraindicated_list', 'serious_list', 'significant_list', 'monitor_list', 'minor_list']
    interactions = []
    for interaction_id in interaction_ids:
        try:
            interaction_list = driver.find_element(By.ID, interaction_id)
            if interaction_list.value_of_css_property('display') == 'block':
                interaction_items = interaction_list.find_elements(By.TAG_NAME, 'li')
                for item in interaction_items:
                    header = item.find_element(By.TAG_NAME, 'h4').text
                    paragraph = item.find_element(By.TAG_NAME, 'p').text
                    interactions.append(f'{header}：{paragraph}')
        except:
            pass
    if not interactions:
        return ["No interactions found"]
    return interactions

def main():
    temp_file = 'temp_results.xlsx'
    df = pd.read_excel(temp_file)
    # 打開目標URL
    driver.get('https://reference.medscape.com/drug-interactionchecker')

    # 等待網頁載入
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'MDICtextbox'))
    )

    # 找到輸入框，使用ID為 'MDICtextbox'
    input_box = driver.find_element(By.ID, 'MDICtextbox')

    # 用來記錄查不到結果的藥品
    skipped_drugs_1 = set()  # 用來記錄查不到結果的 drug_1
    skipped_drugs_2 = set()  # 用來記錄查不到結果的 drug_2

    for index, row in df.iterrows():
        # 如果 interactions 欄位已有值，則跳過
        if pd.notna(row['interactions']):
            print(f'{index}: Skipped as interactions already have value')
            continue
        drug_1 = row['drug_1']
        drug_2 = row['drug_2']

        # 如果藥品在跳過清單中，則跳過查詢
        if drug_1 in skipped_drugs_1:
            print(f'{index}: Skipped {drug_1} as it was previously found to have no results')
            df.at[index, 'interactions'] = 'No results'
            continue

        if drug_2 in skipped_drugs_2:
            print(f'{index}: Skipped {drug_2} as it was previously found to have no results')
            df.at[index, 'interactions'] = 'No results'
            continue

        time.sleep(random.uniform(1.5, 2))
        if not send_medicine(input_box, drug_1):
            slow_clear(input_box)
            clear_all_interactions(driver)
            print(f'{index}: No results for {drug_1}')
            df.at[index, 'interactions'] = 'No results'
            skipped_drugs_1.add(drug_1)  # 將該藥品加入跳過清單
            continue

        if not send_medicine(input_box, drug_2):
            slow_clear(input_box)
            clear_all_interactions(driver)
            print(f'{index}: No results for {drug_2}')
            df.at[index, 'interactions'] = 'No results'
            skipped_drugs_2.add(drug_2)  # 將該藥品加入跳過清單
            continue

        time.sleep(random.uniform(1, 1.5))
        interactions = extract_interactions()
        print(f'{index}: {interactions}')
        df.at[index, 'interactions'] = '; '.join(interactions)
        slow_clear(input_box)
        time.sleep(random.uniform(0.7, 1))
        clear_all_interactions(driver)
        df.to_excel(temp_file, index=False)

if __name__ == '__main__':
    main()
    driver.quit()