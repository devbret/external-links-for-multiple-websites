import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time

def is_external(url, base):
    return urlparse(url).netloc != urlparse(base).netloc

def crawl_site(start_urls, max_links=10, retries=3, delay=5):
    external_links = {}
    internal_links = {}

    def crawl(url, base_url, visited):
        if len(visited) >= max_links:
            return
        visited.add(url)
        print(f"Crawling: {url}")
        
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                break
            except requests.exceptions.RequestException as e:
                print(f"Failed to crawl {url}: {e}")
                if attempt < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    return
        
        for link in soup.find_all('a', href=True):
            href = urljoin(url, link.get('href'))
            if is_external(href, base_url):
                if href not in external_links:
                    external_links[href] = []
                external_links[href].append(url)
            else:
                if href not in visited:
                    if base_url not in internal_links:
                        internal_links[base_url] = []
                    internal_links[base_url].append(href)
                    crawl(href, base_url, visited)

    for start_url in start_urls:
        visited = set()
        crawl(start_url, start_url, visited)

    return external_links, internal_links

def save_links_as_json(external_links, internal_links, filename='links.json'):
    data = {
        'external_links': external_links,
        'internal_links': internal_links
    }
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

start_urls = ['https://www.example.com/',]
external_links, internal_links = crawl_site(start_urls)
save_links_as_json(external_links, internal_links)
