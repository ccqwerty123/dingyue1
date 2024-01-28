import os
import requests
import re

# 定义获取网页信息的函数
def query_information():
    base_url = 'http://webpage_url.com/?before='  # 你要查询的网址
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
    }

    # 从文件中读取历史数据并添加到found_data中
    found_data = []
    if os.path.isfile('data.txt'):
        with open('data.txt', 'r') as file:
            found_data = [line.strip() for line in reversed(file.readlines())]
    
    while True:
        response = requests.get(url, headers=headers)
        html_contents = response.text
        # 使用正则匹配找到所有的数据
        regex = 'target_regex_pattern'  # 更新为你要抓取的数据的正则表达式
        temp_data = re.findall(regex, html_contents)
        if len(temp_data) == 0:
            break  # 如果没有找到数据，停止循环
        else:
            # 将临时列表的数据添加到found_data的前面
            found_data = temp_data + found_data
            # 准备下一轮查询的网址
            next_url = base_url + str(temp_data[-1]['timestamp'])

    # 保存数据到文件
    with open('data.txt', 'w') as file:
        for data_string in reversed(found_data):  # 反向打印found_data以保持最新的数据在前面
            file.write(data_string + '\n')
            
    # 如果有新数据，将最新的数据时间保存到另一个文件
    if found_data:
        with open('latest_time.txt', 'w') as file:
            # 最新的数据在found_data的末尾
            file.write(found_data[-1]['timestamp'])

# 执行查询函数
query_information()
