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

    old_data = []
    if os.path.exists('data.txt'):
        with open('data.txt', 'r') as file:
            old_data = [line.strip() for line in file]

    found_data = []

    while True:
        response = requests.post(url, headers=headers)
        text = html.unescape(response.text)
        pattern = re.compile(r'(export \w*="[^"]*").*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
        matches = pattern.findall(text)
        for match in matches: 
            export_info = match[0].replace('\\', '')
            timestamp = match[1]
            data_string = "Export Info: " + export_info + " | Timestamp: " + timestamp
            if data_string not in old_data:            
                found_data.append(data_string) 

        pattern = r'before=(\d+)'
        match = re.search(pattern, text)
        if match:  
            value = match.group(1)
            url = base_url + value
        else:
            break  

    if found_data:
        old_data.extend([x for x in found_data if x not in old_data]) # Avoid duplication in the final data

        with open('data.txt', 'w') as file:
            for data_string in old_data:
                file.write(data_string + '\n')

        latest_timestamp = re.search(r'Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', found_data[-1]).group(1)
        with open('latest.txt', 'w') as file:
            file.write(latest_timestamp)

    for data_string in found_data:
        print(data_string)

query_information()
