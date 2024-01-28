import os
import requests
import re
import html

def query_information():
    base_url = 'https://t.me/s/faketoulu?before='
    url = base_url
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'Host': 't.me'
    }

    # 创建一个列表来存储已经找到的字符串
    found_data = []

    while True:
        # 创建一个临时列表来存储这次循环找到的字符串
        temp_data = []
        
        # 访问URL
        response = requests.post(url, headers=headers)
        
        # 解析HTML
        text = html.unescape(response.text)
        
        pattern = re.compile(r'(export \w*="[^"]*").*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
        matches = pattern.findall(text)
        for match in matches: 
            export_info = match[0].replace('\\', '')
            timestamp = match[1]
            data_string = "Export Info: " + export_info + " | Timestamp: " + timestamp  # 将URL和时间戳组成一个字符串
            if data_string not in found_data:  # 如果字符串是唯一的，保存数据
                temp_data.append(data_string)  # 将新字符串添加到临时列表

        # 将临时列表的数据添加到found_data的开始
        found_data = temp_data + found_data

        # 查找 before= 后的值，并更新URL
        pattern = r'before=(\d+)'
        match = re.search(pattern, text)
        if match:  
            value = match.group(1)
            url = base_url + value
        else:
            break  

    # 倒序排序结果列表
    found_data.reverse()

    # 保存数据到文件
    with open('data.txt', 'a') as file:
        for data_string in found_data:
            file.write(data_string + '\n')
    
    # 保存最新的日期到另一个文件
    if found_data:
        latest_timestamp = re.search(r'Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', found_data[-1]).group(1)
        with open('latest.txt', 'w') as file:
            file.write(latest_timestamp)

    # 输出最终的结果
    for data_string in found_data:
        print(data_string)
        
# 从文件中读取历史数据并添加到found_data中
if os.path.isfile('data.txt'):
    with open('data.txt', 'r') as file:
        found_data = [line.strip() for line in file.readlines()]
else:
    found_data = []

# 查询新的信息并在查询后保存到found_data
query_information()
