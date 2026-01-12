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
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
        except Exception as e:
            print(f"DEBUG: Scraper error for r/{subreddit_name}: {e}", flush=True)
            return 0
        
        if response.status_code != 200:
            print(f"DEBUG: Scraper received {response.status_code} for r/{subreddit_name}", flush=True)
            return 0
            
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', class_='thing')
        
        posts_count = 0
        for item in items[:limit]:
            post_id = item.get('data-fullname')
            title = item.find('a', class_='title').text
            url = item.find('a', class_='title')['href']
            
            # Deep scrape to get the body
            body = ""
            full_url = f"https://reddit.com{url}" if url.startswith('/') else url.replace("old.reddit.com", "reddit.com")
            scrape_url = full_url.replace("reddit.com", "old.reddit.com")
            
            if "/comments/" in full_url:
                try:
                    # print(f"DEBUG: Scraping detail page: {scrape_url}", flush=True)
                    detail_res = requests.get(scrape_url, headers=self.headers, timeout=10)
                    if detail_res.status_code == 200:
                        detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
                        body_div = detail_soup.find('div', class_='expando')
                        if body_div:
                            body = body_div.text.strip()
                            
                        # Scrape all available comments - MOVED OUTSIDE body_div check
                        from radar.storage.db import save_comment
                        comment_items = detail_soup.select('div.comment')
                        for c_item in comment_items:
                            try:
                                c_id = c_item.get('data-fullname')
                                if not c_id: continue
                                
                                c_author = c_item.get('data-author')
                                c_content_div = c_item.select_one('div.md')
                                c_body = c_content_div.text.strip() if c_content_div else ""
                                
                                # Skip very short or empty comments
                                if len(c_body) < 5: continue
                                
                                c_score_attr = c_item.find('span', class_='score unvoted')
                                c_score = 0
                                if c_score_attr:
                                    c_score_text = c_score_attr.get('title', '0')
                                    try:
                                        c_score = int(c_score_text)
                                    except:
                                        c_score = 0
                                
                                save_comment({
                                    'id': c_id,
                                    'post_id': post_id,
                                    'author': c_author,
                                    'body': c_body,
                                    'score': c_score,
                                    'created_at': datetime.utcnow().isoformat(),
                                    'depth': 0
                                })
                            except Exception as ce:
                                # print(f"DEBUG: Error saving comment: {ce}", flush=True)
                                pass
                except Exception as e:
                    print(f"DEBUG: Detail scrape failed: {e}", flush=True)

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
            print(f"DEBUG: [{subreddit_name}] Scraped: {title[:30]}...", flush=True)
            time.sleep(random.uniform(0.5, 1.5)) # Slightly faster for testing
            
        return posts_count
