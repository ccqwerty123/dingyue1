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
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    # 检查data.txt文件是否存在且非空
    if os.path.isfile('data.txt'):
        with open('data.txt', 'r') as file:
            found_data = [line.strip() for line in file.readlines()]

        print(f"从data.txt加载了 {len(found_data)} 条记录。")

        # 检查是否每行都包含 "Export Info" 和 "Timestamp"
        for line in found_data:
            if "Export Info" in line and "Timestamp" in line:
                valid_data.append(line)
    else:
        print("data.txt 不存在。它可能是空的或缺失。")

    # 打印读取的有效数据，检查是否正确加载
    print(f"从data.txt加载了 {len(valid_data)} 条有效记录。")
    
    # 网络抓取循环
    total_messages_count = 0  # 初始化消息总数计数器
    
    while True:
        temp_data = []
        response = requests.get(url, headers=headers)
        text = html.unescape(response.text)

        # 打印网页的原始响应，检查网页内容
        print(f"获取页面内容。长度: {len(text)}")

        # 使用 BeautifulSoup 来解析 HTML 页面
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到所有消息内容
        messages = soup.find_all("div", class_="tgme_widget_message_text js-message_text")
        print(url)
        print(f"在页面上找到了 {len(messages)} 条消息。")

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

            # 输出提取的时间戳，检查是否正确提取
            print(f"提取的时间戳: {timestamp}")

            if timestamp:
                # 确保时间戳是有效的
                try:
                    timestamp_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    print(f"解析的时间戳: {timestamp_obj}")
                except ValueError:
                    timestamp_obj = None
                    print(f"无效时间戳: {timestamp}")
            else:
                timestamp_obj = None

            # 格式化数据
            export_info_b64 = base64.b64encode(export_line.encode()).decode() if export_line else None
            data_string = f"{export_info_b64} | 时间戳: {timestamp} | 消息ID: {message_id}"

            # 如果该数据不是重复的，则添加到临时数据列表
            if data_string not in valid_data:
                temp_data.append((data_string, timestamp_obj))
                new_data_flag = True
                total_messages_count += len(messages)  # 增加消息总数计数

        valid_data = [data[0] for data in temp_data] + valid_data

        # 继续抓取下一页的逻辑
        pattern = r'before=(\d+)'
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            url = base_url + value
        else:
            break
        
    # 如果抓取的消息总数超过300条，退出抓取
        if total_messages_count > 300:
            print(f"抓取的消息总数达到 {total_messages_count}，退出抓取。")
            break

    # 排序：根据时间戳排序（使用 datetime 处理）
    print(f"正在根据时间戳排序 {len(valid_data)} 条记录...")
    valid_data.sort(key=lambda s: datetime.strptime(re.search(r'时间戳: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', s).group(1), '%Y-%m-%d %H:%M:%S') if re.search(r'时间戳: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', s) else datetime.min, reverse=True)

    # 如果数据超过300条，仅保留最新的300条
    if len(valid_data) > 300:
        valid_data = valid_data[:300]

    # 输出更新前的 valid_data 内容
    print(f"更新前的有效数据: {len(valid_data)} 条记录。")

    # 如果有新数据，更新文件
    if new_data_flag:
        print(f"发现新数据，正在更新 data.txt 和 latest.txt...")

        # 更新 data.txt 文件
        with open('data.txt', 'w') as file:
            for data_string in valid_data:
                file.write(data_string + '\n')

        if valid_data:
            latest_timestamp = re.search(r'时间戳: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', valid_data[0]).group(1)
            with open('latest.txt', 'w') as file:
                file.write(latest_timestamp)

        print("data.txt 和 latest.txt 已更新。")
    else:
        print("未发现新数据。未进行更新。")

    # 打印有效数据
    for data_string in valid_data:
        print(data_string)

# 调用查询信息函数
query_information()
