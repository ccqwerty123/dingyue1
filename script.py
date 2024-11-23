import os
import requests
import re
from bs4 import BeautifulSoup
import base64
import html
from datetime import datetime

def query_information():
    # 初始化有效数据列表
    valid_data = []
    new_data_flag = False
    encoded_url = "aHR0cHM6Ly90Lm1lL3MvZmFrZXRvdWx1P2JlZm9yZT0="
    decoded_url = base64.b64decode(encoded_url).decode('utf-8')

    base_url = decoded_url
    url = base_url
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'Host': 't.me'
    }

    # 检查data.txt文件是否存在
    if os.path.isfile('data.txt'):
        # 如果存在，则打开文件并读取内容
        with open('data.txt', 'r') as file:
            found_data = [line.strip() for line in file.readlines()]

            # 检查是否每行都包含 "Export Info" 和 "Timestamp"
            for line in found_data:
                if "Export Info" in line and "Timestamp" in line:
                    valid_data.append(line)

    while True:
        temp_data = []
        response = requests.post(url, headers=headers)
        text = html.unescape(response.text)

        # 使用 BeautifulSoup 来解析 HTML 页面
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到所有消息内容
        messages = soup.find_all("div", class_="tgme_widget_message_text js-message_text")
        
        for message in messages:
            # 提取消息内容
            message_content = message.get_text(strip=True)
            
            # 提取消息 ID (从消息的 footer 部分获取)
            message_id = message.find_next("a", class_="tgme_widget_message_date")
            if message_id:
                message_id = message_id['href'].split('/')[-1]

            # 提取 export 行（正则表达式提取 export 信息）
            export_match = re.search(r'(export\s+[^"]*?="[^"]*")', message_content)
            export_line = export_match.group(0) if export_match else None

            # 提取时间戳
            time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message_content)
            timestamp = time_match.group(1) if time_match else None

            if timestamp:
                # 确保时间戳是有效的
                try:
                    timestamp_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    timestamp_obj = None
            else:
                timestamp_obj = None

            # 格式化数据
            export_info_b64 = base64.b64encode(export_line.encode()).decode() if export_line else None
            data_string = f"Export Info: {export_info_b64} | Timestamp: {timestamp} | Message ID: {message_id}"

            # 如果该数据不是重复的，则添加到临时数据列表
            if data_string not in valid_data:
                temp_data.append((data_string, timestamp_obj))
                new_data_flag = True

        valid_data = [data[0] for data in temp_data] + valid_data

        # 继续抓取下一页的逻辑
        pattern = r'before=(\d+)'
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            url = base_url + value
        else:
            break

    # 排序：根据时间戳排序（使用 datetime 处理）
    valid_data.sort(key=lambda s: datetime.strptime(re.search(r'Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', s).group(1), '%Y-%m-%d %H:%M:%S') if re.search(r'Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', s) else datetime.min, reverse=True)

    # 如果数据超过300条，仅保留最新的300条
    if len(valid_data) > 300:
        valid_data = valid_data[:300]

    # 如果有新数据，更新文件
    if new_data_flag:
        # 更新 data.txt 文件
        with open('data.txt', 'w') as file:
            for data_string in valid_data:
                file.write(data_string + '\n')

        if valid_data:
            latest_timestamp = re.search(r'Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', valid_data[0]).group(1)
            with open('latest.txt', 'w') as file:
                file.write(latest_timestamp)

    # 打印有效数据
    for data_string in valid_data:
        print(data_string)


query_information()
