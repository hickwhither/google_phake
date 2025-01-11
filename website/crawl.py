from flask import *

from website import db
from website.models import *

import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

DEFAULT_ICON = "https://cdn.discordapp.com/attachments/907537629417996359/1326940639748690012/image.png?ex=67814145&is=677fefc5&hm=c6e69d5f6825d92767d1f29cd64ef6209c22c4a9ebe6b8e6f88371630fb2b13a&"
initialize_urls = ["https://en.wikipedia.org/wiki/Google", "https://vi.wikipedia.org/wiki/Google"]

class CrawlResult:
    urls: list
    words: list
    data: dict
    def __init__(self, urls: list, words: list, data: dict):
        self.urls = urls
        self.words = words
        self.data = data


def crawling(url: str) -> CrawlResult|None:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; en-GB) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url=url, headers=headers, timeout=3)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return CrawlResult(
            data={
                'url': url,
                "last_crawl": time.time()
            },
            urls=[],
            words=[]
        )

    try: soup = BeautifulSoup(response.content.decode(), "html.parser")
    except Exception as e:
        print(f"Progress Failed: {e}")
        return CrawlResult(
            data={
                'url': url,
                "last_crawl": time.time()
            },
            urls=[],
            words=[]
        )
    
    icon_url = soup.find('link', rel='icon')
    if icon_url: icon_url = urljoin(url, icon_url.get('href'))
    if not icon_url: icon_url = DEFAULT_ICON
    
    title = soup.find('title').get_text(separator=' ', strip=True) if soup.find('title') else 'No title found'
    
    description = soup.find('meta', attrs={'name': 'description'})
    if description: description = description.get('content')
    if not description: description = soup.get_text(separator=' ', strip=True)[:200]

    urls = list(set(urljoin(url, tag.get('href')).split('#')[0] for tag in soup.find_all(href=True)))
    words = list(set(soup.get_text(separator=' ', strip=True).upper().split()))
    
    return CrawlResult(
        data= {
            'url': url,
            'icon': icon_url,
            'title': title,
            'description': description,
            "last_crawl": time.time()
        },
        urls = urls,
        words = words
    )

def hyperlink_update(data:dict, words:list, urls: list) -> None:
    url = data.get('url')

    link = Hyperlinks.query.get(data.get('url'))
    if not link:
        link = Hyperlinks(url=data.get('url'),
                          icon=data.get('icon'),
                          title=data.get('title'),
                          description=data.get('description'),
                          words=words
                          )
        db.session.add(link)
    else:
        old_words = link.words
        old_word_entries = {word_entry.word: word_entry for word_entry in Word.query.filter(Word.word.in_(old_words)).all()}
        for word in old_words:
            if word in old_word_entries and url in old_word_entries[word].urls:
                old_word_entries[word].urls.remove(url)
                if not old_word_entries[word].urls:
                    db.session.delete(old_word_entries[word])
        
        link.icon = data.get('icon') or link.icon
        link.title = data.get('title') or link.title
        link.description = data.get('description') or link.description
        link.words = words or link.words

    link.last_crawl = time.time()
    
    linked_links = {link.url: link for link in Hyperlinks.query.filter(Hyperlinks.url.in_(urls)).all()}
    for linked_url in urls:
        linked_link = linked_links.get(linked_url)
        if linked_link:
            expected = 1 / (1 + 10 ** ((link.rate - linked_link.rate) / 400))
            linked_link.rate += 30 * (1 - expected)

    db.session.commit()

def new_hyperlinks(urls: list) -> None:
    urls = [url.split('#')[0] for url in urls]
    existing_urls = {link.url for link in Hyperlinks.query.filter(Hyperlinks.url.in_(urls)).all()}
    new_links = [Hyperlinks(url=url, last_crawl=0) for url in urls if url not in existing_urls]
    db.session.bulk_save_objects(new_links)
    db.session.commit()

def words_update(words: list, url: str) -> None:
    word_entries = {word_entry.word: word_entry for word_entry in Word.query.filter(Word.word.in_(words)).all()}
    
    for word in words:
        if word in word_entries:
            if url not in word_entries[word].urls:
                word_entries[word].urls.append(url)
        else:
            new_word = Word(word=word, urls=[url])
            db.session.add(new_word)

    db.session.commit()

def get_oudated() -> str|None:
    link:Hyperlinks = Hyperlinks.query.filter(Hyperlinks.last_crawl < time.time() - 3600).first()
    if link is None: return None
    return link.url

def interval(app: Flask):
    with app.app_context(): new_hyperlinks(initialize_urls)
    while True:
        # time.sleep(0.5)
        with app.app_context():
            url = get_oudated()
            if not url: continue
            # print(f"working on {url}..")
            result: CrawlResult = crawling(url)
            print(f"Crawled {url}")
            new_hyperlinks(urls=result.urls)
            words_update(words=result.words, url=url)
            hyperlink_update(data=result.data, words=result.words, urls=result.urls)

