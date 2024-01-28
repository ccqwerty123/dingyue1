import os
import requests
import re
import html
import base64


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
        pattern = re.compile(r'(export \w*="[^"]*").*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
        matches = pattern.findall(text)
        for match in matches:
            export_info = match[0].replace('\\', '')
            timestamp = match[1]
            # Base64 encryption for 'Export Info'
            export_info = base64.b64encode(export_info.encode()).decode()
            data_string = "Export Info: " + export_info + " | Timestamp: " + timestamp
            if data_string not in valid_data:
                temp_data.append(data_string)
                new_data_flag = True
          
        valid_data = temp_data + valid_data

        pattern = r'before=(\d+)'
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            url = base_url + value
        else:
            break

    # Sort data by timestamp
    valid_data.sort(key=lambda s: re.search(r'Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', s).group(1), reverse=True)
    
    # If more than 300 data, only keep the latest 300 data
    if len(valid_data) > 300:
        valid_data = valid_data[:300]
      
    if new_data_flag:
      # Update data.txt
      with open('data.txt', 'w') as file:
          for data_string in valid_data:
              file.write(data_string + '\n')

      if valid_data:
          latest_timestamp = re.search(r'Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', valid_data[0]).group(1)
          with open('latest.txt', 'w') as file:
              file.write(latest_timestamp)

    # Print valid data
    for data_string in valid_data:
        print(data_string)


query_information()
