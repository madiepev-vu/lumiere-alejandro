import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from pathlib import Path
import re
import json

# --- Configurations ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def clean_text(text):
    """Utility to clean up whitespace inconsistencies from HTML extraction."""
    return "\n".join(line.strip() for line in text.split("\n") if line.strip())

def extract_topic_from_url(url):
    """Extracts the textbook name from the URL."""
    match = re.search(r'/books/([^/]+)/pages/', url)
    if match:
        raw_topic = match.group(1)
        clean_topic = raw_topic.replace('introduction-', '').replace('introductory-', '').replace('-essentials', '').replace('-3e', '').replace('-2e', '')
        return clean_topic.replace('-', ' ').title()
    return "Unknown Topic"

def get_chapter_structure(chapter_url):
    """
    Finds subchapters and explicitly constructs the Key Terms URL 
    to bypass OpenStax's JavaScript-hidden menus.
    """
    response = requests.get(chapter_url, headers=HEADERS)
    response.encoding = 'utf-8'
    
    if response.status_code != 200:
        return [], None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. Identify the book base and chapter number
    match = re.search(r'(/books/[^/]+/pages/)(\d+)-', chapter_url)
    if not match:
        return [chapter_url], None
        
    base_path = match.group(1)
    chapter_num = match.group(2)
    chapter_prefix = f"{base_path}{chapter_num}-"
    
    # 2. Find subchapters (using links on the page)
    subchapters = []
    for link in soup.find_all('a', href=True):
        absolute_url = urljoin(chapter_url, link['href']).split('#')[0]
        url_lower = absolute_url.lower()

        if chapter_prefix in url_lower:
            if any(skip in url_lower for skip in ["key-terms", "review-questions", "references", "summary", "assessment"]):
                continue
            if absolute_url not in subchapters:
                subchapters.append(absolute_url)

    # 3. DIRECTLY CONSTRUCT the Key Terms URL and verify it exists
    base_domain = chapter_url.split('/books/')[0]
    constructed_key_terms_url = f"{base_domain}{base_path}{chapter_num}-key-terms"
    
    check_exists = requests.head(constructed_key_terms_url, headers=HEADERS)
    key_terms_url = constructed_key_terms_url if check_exists.status_code == 200 else None

    return subchapters, key_terms_url

def extract_section_content(url):
    """Extracts body text from a subchapter."""
    response = requests.get(url, headers=HEADERS)
    response.encoding = 'utf-8' # Prevents Mojibake (â€œ)
    
    if response.status_code != 200:
        return ""
        
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('main') or soup.find('div', {'data-type': 'page'}) or soup.find('div', class_='os-chapter-content')
    if not main_content:
        main_content = soup.body 
    if not main_content:
        return ""

    for extra in main_content.find_all(['nav', 'footer', 'header', 'script', 'style']):
        extra.decompose()
    for extra in main_content.find_all(class_=['os-review-questions', 'os-references']):
        extra.decompose()

    return clean_text(main_content.get_text(separator='\n'))

def harvest_chapter_data(chapter_start_url):
    print(f"\n[+] Analyzing Chapter Layout from: {chapter_start_url}")
    topic = extract_topic_from_url(chapter_start_url)
    subchapters, key_terms_url = get_chapter_structure(chapter_start_url)
    
    full_body_parts = []
    ground_truth_objectives_text = ""

    # 1. Harvest Subchapters
    for sub_url in subchapters:
        print(f" -> Fetching content: {sub_url}")
        body = extract_section_content(sub_url)
        full_body_parts.append(body)
        time.sleep(1.0) 

    # 2. Harvest standalone Key Terms page as full text
    if key_terms_url:
        print(f" -> Found Key Terms page! Fetching full text: {key_terms_url}")
        ground_truth_objectives_text = extract_section_content(key_terms_url)
        time.sleep(1.0)
    else:
        print(" -> No dedicated Key Terms page found for this chapter.")

    print("[!] Harvest complete!")
    return {
        "topic": topic,
        "ground_truth_objectives": ground_truth_objectives_text,
        "full_chapter_text": "\n\n".join(full_body_parts)
    }

urls = []
with open("URLs.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line)
        line = line.strip()
        urls.append(line)

print(urls)

dic = {}

output_dir = Path("textbooks")
output_dir.mkdir(parents=True, exist_ok=True)

for url in urls:
    chapter_data = harvest_chapter_data(url)
    if chapter_data['topic'] not in dic:
        dic[chapter_data['topic']] = 0
    dic[chapter_data['topic']] += 1
    filename = output_dir / f"{chapter_data['topic'].replace(' ', '_').lower()}_{dic[chapter_data['topic']]}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(chapter_data, f, ensure_ascii=False, indent=4)
    print(f"[+] Data saved to {filename}\n\n")

