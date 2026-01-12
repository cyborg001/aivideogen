import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime

url = "https://www.diariolibre.com/rss/planeta.xml"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Testing URL: {url}")
try:
    response = requests.get(url, timeout=10, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        content = response.content.strip()
        print(f"Content length: {len(content)}")
        root = ET.fromstring(content)
        items = root.findall('.//item')
        print(f"Items found: {len(items)}")
        if items:
            first = items[0]
            title = first.find('title').text if first.find('title') is not None else "N/A"
            link = first.find('link').text if first.find('link') is not None else "N/A"
            pub_date = first.find('pubDate').text if first.find('pubDate') is not None else "N/A"
            print(f"First Item Title: {title}")
            print(f"First Item PubDate: {pub_date}")
            
            # Test Date Parsing
            try:
                # Expected format: Fri, 27 Dec 2024 12:00:00 -0400
                parsed_date = datetime.strptime(pub_date[:25].strip(), '%a, %d %b %Y %H:%M:%S')
                print(f"Date parsed successfully: {parsed_date}")
            except Exception as e:
                print(f"Date parsing FAILED: {e}")
                
except Exception as e:
    print(f"General Error: {e}")
