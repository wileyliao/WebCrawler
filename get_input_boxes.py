import requests
from bs4 import BeautifulSoup

# 目標URL
url = 'https://reference.medscape.com/drug-interactionchecker'

# 發送GET請求
response = requests.get(url)

# 確認請求成功
if response.status_code == 200:
    # 解析HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # 找到所有輸入框
    input_fields = soup.find_all('input')

    # 打印輸入框的屬性
    for input_field in input_fields:
        input_type = input_field.get('type', 'N/A')
        input_id = input_field.get('id', 'N/A')
        input_name = input_field.get('name', 'N/A')
        print(f'輸入框 - 類型: {input_type}, ID: {input_id}, Name: {input_name}')
else:
    print(f'無法訪問網頁，狀態碼: {response.status_code}')
