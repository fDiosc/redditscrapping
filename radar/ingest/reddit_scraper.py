import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from radar.storage.db import save_post

class RedditScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_subreddit_posts(self, subreddit_name: str, days: int = 7, limit: int = 20):
        url = f"https://old.reddit.com/r/{subreddit_name}/new/"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            return 0
            
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', class_='thing')
        
        posts_count = 0
        for item in items[:limit]:
            post_id = item.get('data-fullname')
            title = item.find('a', class_='title').text
            url = item.find('a', class_='title')['href']
            # Old reddit usually doesn't show full body in list view easily without more scraping
            # This is a simplified fallback
            
            # Deep scrape to get the body
            body = ""
            full_url = f"https://reddit.com{url}" if url.startswith('/') else url.replace("old.reddit.com", "reddit.com")
            scrape_url = full_url.replace("reddit.com", "old.reddit.com")
            
            if "/comments/" in full_url:
                try:
                    detail_res = requests.get(scrape_url, headers=self.headers)
                    if detail_res.status_code == 200:
                        detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
                        body_div = detail_soup.find('div', class_='expando')
                        if body_div:
                            body = body_div.text.strip()
                except:
                    pass

            post_data = {
                'id': post_id,
                'platform': 'reddit',
                'source': subreddit_name,
                'url': full_url,
                'title': title,
                'body': body,
                'author': item.get('data-author'),
                'score': int(item.get('data-score', 0)),
                'num_comments': int(item.get('data-comments-count', 0)),
                'created_at': datetime.utcnow().isoformat(),
                'ingestion_method': 'scraper'
            }
            save_post(post_data)
            posts_count += 1
            time.sleep(random.uniform(1, 3)) # Anti-block
            
        return posts_count
