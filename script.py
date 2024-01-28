import os
import re
import html
import requests
import base64

def is_base64(s):
    try:
        base64.b64decode(s)
        return True
    except Exception:
        return False

def query_information():
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

    old_data = []
    if os.path.exists('data.txt'):
        with open('data.txt', 'r') as file:
            for line in file:
                # Decode only if the line is base64 encoded
                if is_base64(line.strip()):
                    old_data.append(base64.b64decode(line.strip()).decode('utf-8'))
                else:
                    old_data.append(line.strip())

    found_data = []
    latest_timestamp = None

    while True:
        response = requests.post(url, headers=headers)
        text = html.unescape(response.text)
        pattern = re.compile(r'(export \w*="[^"]*").*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
        matches = pattern.findall(text)

        # Process the matches in reverse (new to old) order
        for match in reversed(matches):
            export_info = match[0].replace('\\', '')
            timestamp = match[1]

            # Update the latest_timestamp value if it's None or less than the current timestamp
            if latest_timestamp is None or timestamp > latest_timestamp:
                latest_timestamp = timestamp

            data_string = "Export Info: " + base64.b64encode(export_info.encode()).decode() + " | Timestamp: " + timestamp
            if data_string not in old_data:
                # Add new data
                found_data.append(data_string)

        pattern = r'before=(\d+)'
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            url = base_url + value
        else:
            break

     # rest of your code
     # please replace all write/read operations to data.txt with base64 encoding/decoding.
