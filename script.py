import requests
from bs4 import BeautifulSoup
import re

# URL of the Telegram channel's web view
url = 'https://t.me/s/faketoulu?before'

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Send the request
response = requests.get(url, headers=headers)

# Check the status code
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all message containers (correct class name based on actual HTML structure)
    messages = soup.find_all("div", class_="tgme_widget_message_text js-message_text")
    
    if not messages:
        print("No messages found.")
    
    for message in messages:
        # Extract message content (getting text with strip)
        message_content = message.get_text(strip=True)
        
        # Find the message ID from the footer (this assumes message ID is inside the <a> tag with the given class)
        message_id_tag = message.find_next("a", class_="tgme_widget_message_date")
        if message_id_tag:
            message_id = message_id_tag['href'].split('/')[-1]  # Extract message ID from URL
        else:
            message_id = None
        
        # Extract export line using fixed regex (this assumes export is in the form export="value")
        export_match = re.search(r'(export\s+[^"]*?="[^"]*")', message_content)
        export_line = export_match.group(0) if export_match else None
        
        # Extract timestamp using regex (this assumes timestamp is in 'YYYY-MM-DD HH:MM:SS' format)
        time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message_content)
        timestamp = time_match.group(1) if time_match else None
        
        # Output the results
        print(f"Message Content: {message_content}")
        print(f"Export Line: {export_line}")
        print(f"Timestamp: {timestamp}")
        print(f"Message ID: {message_id}")
        print("-" * 50)  # Separator for readability
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
