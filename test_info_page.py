#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dlcweb.settings')
django.setup()

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def test_info_page():
    base_url = "https://cmu.cba.ku.edu.kw"
    info_url = urljoin(base_url, "/aolapp/syllabus/course/info/1011/201/")
    
    print(f"Fetching info page: {info_url}")
    
    try:
        response = requests.get(info_url, timeout=15)
        response.raise_for_status()
        
        # Save the HTML for inspection
        with open('debug_info_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("Page title:", soup.find('title').get_text() if soup.find('title') else 'No title')
        
        # Look for download links
        download_links = soup.find_all('a', href=True)
        download_urls = []
        
        for link in download_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if it's a download link
            if any(keyword in href.lower() for keyword in ['/archive/', 'download', '.pdf', '.docx']):
                full_url = urljoin(info_url, href)
                download_urls.append((text, full_url))
                print(f"Found download link: {text} -> {full_url}")
        
        print(f"\nTotal download links found: {len(download_urls)}")
        
        # Look for tables or lists that might contain multiple syllabi
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        lists = soup.find_all(['ul', 'ol'])
        print(f"Found {len(lists)} lists")
        
        return download_urls
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    test_info_page()