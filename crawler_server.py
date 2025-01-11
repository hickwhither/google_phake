"""
Planned on doing a seperate server as crawler but too lazy lmao
"""

import threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tinydb import TinyDB, Query
import time


DEFAULT_ICON = "https://cdn.discordapp.com/attachments/907537629417996359/1326940639748690012/image.png?ex=67814145&is=677fefc5&hm=c6e69d5f6825d92767d1f29cd64ef6209c22c4a9ebe6b8e6f88371630fb2b13a&"

initialize_urls = ["https://en.wikipedia.org/wiki/Google", "https://vi.wikipedia.org/wiki/Google"]

class CrawlerGroup:
    db_urls: TinyDB
    db_words: TinyDB
    links = set()

    def __init__(self, db_urls_file:str = "urls.json", db_words_file:str = "words.json"):
        self.db_urls = TinyDB(db_urls_file)
        self.db_words = TinyDB(db_words_file)
        for url in initialize_urls:
            self.db_urls.insert({'url': url, 'last_crawl': 0})
    
    def start(self):
        while True:
            now = time.time()
            link = self.db_urls.get(Query().last_crawl < (now - 86400))
            if link:
                link = link.get('url')
                data = self.CrawlEmDi(link)
                print(f"Crawled: {link}")
                self.db_urls.insert(data)
            time.sleep(0.5)
    
    def CrawlerLinkUpdate(self):
        while True:
            now = time.time()
            self.links = set([item['url'] for item in self.db_urls.search(Query().last_crawl < (now - 86400))])
            time.sleep(0.5)
    
    def CralwerAgent(self):
        while True:
            print("Hello")
            time.sleep(1)
            if not self.links: continue
            link = set.pop()
            data = self.CrawlEmDi(link)
            print(f"Crawled: {link}")
            self.db_urls.upsert(data, Query().url == link)
    
    def CrawlEmDi(self, link: str):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; en-GB) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url=link, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")
        
        icon_url = soup.find('link', rel='icon')
        if icon_url: icon_url = urljoin(response.url, icon_url.get('href'))
        if not icon_url: icon_url = DEFAULT_ICON
        
        title = soup.find('title').get_text(separator=' ', strip=True) if soup.find('title') else 'No title found'
        
        description = soup.find('meta', attrs={'name': 'description'})
        if description: description = description.get('content')
        if not description: description = soup.get_text(separator=' ', strip=True)[:200]

        for tag in soup.find_all(href=True):
            url = urljoin(response.url, tag.get('href'))
            if not self.db_urls.search(Query().url == url):
                self.db_urls.insert({'url': url, 'last_crawl': 0})

        words = set(soup.get_text(separator=' ', strip=True).split())
        
        return {
            'url': response.url,
            'icon': icon_url,
            'title': title,
            'description': description,
            "last_crawl": time.time()
        }

cg = CrawlerGroup()
cg.start()
