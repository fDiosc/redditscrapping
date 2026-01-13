import json
import random
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from curl_cffi import requests
    HAS_CURL_CFFI = True
except ImportError:
    import requests
    HAS_CURL_CFFI = False

from radar.config import REDDIT_PROXY_URL
from radar.storage.db import save_post, save_comment, get_post, update_post_stats

# Pool of modern browser User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

class RedditScraper:
    """Scraper with anti-ban protections for Reddit using JSON fallback and Proxy support."""
    
    def __init__(self):
        # Rate limiting config
        self.min_delay = 2.0
        self.max_delay = 5.0
        self.burst_probability = 0.15
        self.burst_multiplier = 2.5
        
        # Retry config
        self.max_retries = 3
        self.backoff_base = 2.0
        self.backoff_max = 60.0
        
        # Stats
        self.stats = {
            "requests": 0,
            "success": 0,
            "failed": 0,
            "retries": 0,
            "rate_limited": 0,
            "skipped_deep": 0,
        }

        # Proxy Configuration
        self.proxies = None
        if REDDIT_PROXY_URL:
            self.proxies = {
                "http": REDDIT_PROXY_URL,
                "https": REDDIT_PROXY_URL
            }
    
    def _get_headers(self) -> dict:
        """Generate stealth headers compatible with JSON endpoint."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.reddit.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
    
    def _smart_delay(self):
        """Apply human-like delay with jitter between requests."""
        base_delay = random.uniform(self.min_delay, self.max_delay)
        if random.random() < self.burst_probability:
            base_delay *= self.burst_multiplier
        
        jitter = base_delay * random.uniform(-0.1, 0.1)
        time.sleep(base_delay + jitter)
    
    def _request_with_retry(self, url: str) -> Optional[Any]:
        """Make request with exponential backoff, retry, and proxy support."""
        for attempt in range(self.max_retries):
            try:
                self.stats["requests"] += 1
                headers = self._get_headers()
                
                if HAS_CURL_CFFI:
                    response = requests.get(
                        url, 
                        headers=headers, 
                        proxies=self.proxies,
                        impersonate="chrome110",
                        timeout=30,
                        verify=False
                    )
                else:
                    response = requests.get(
                        url, 
                        headers=headers, 
                        proxies=self.proxies,
                        timeout=20
                    )
                
                # Handle rate limiting
                if response.status_code == 429:
                    self.stats["rate_limited"] += 1
                    wait_time = min(self.backoff_base * (2 ** attempt), self.backoff_max)
                    time.sleep(wait_time)
                    self.stats["retries"] += 1
                    continue
                
                if response.status_code == 200:
                    self.stats["success"] += 1
                    return response.json()
                
                print(f"DEBUG: Request failed with status {response.status_code}", flush=True)
                
            except Exception as e:
                print(f"DEBUG: Request exception: {e}", flush=True)
                time.sleep(self.backoff_base * (2 ** attempt))
                self.stats["retries"] += 1
        
        self.stats["failed"] += 1
        return None
    
    def fetch_subreddit_posts(self, subreddit_name: str, days: int = 1, limit: int = 100):
        """
        Fetch posts from a subreddit using JSON endpoint with pagination support.
        Will continue fetching until it hits posts older than the 'days' cutoff or a total of 500 posts.
        """
        posts_added = 0
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        cutoff_date = datetime.fromtimestamp(cutoff).strftime('%Y-%m-%d %H:%M:%S UTC')
        after = None
        max_total = 500 # Safety cap to avoid infinite loops or massive scraping
        
        print(f"DEBUG: Starting deep sync for r/{subreddit_name} (Max {days} days | Cutoff: {cutoff_date})", flush=True)

        while posts_added < max_total:
            url = f"https://www.reddit.com/r/{subreddit_name}/new/.json?limit={limit}"
            if after:
                url += f"&after={after}"
            
            self._smart_delay()
            data = self._request_with_retry(url)

            if not data:
                print(f"DEBUG: Failed to fetch next page for r/{subreddit_name}. Ending sync early.", flush=True)
                break
                
            try:
                items = data.get('data', {}).get('children', [])
                current_after = data.get('data', {}).get('after')
            except Exception as e:
                print(f"DEBUG: Failed to parse JSON for r/{subreddit_name}: {e}", flush=True)
                break
            
            if not items:
                break
            
            page_processed = 0
            page_old_posts = 0
            
            for item_wrapper in items:
                item = item_wrapper.get('data', {})
                post_id = item.get('name')
                created_utc = item.get('created_utc', 0)
                
                if created_utc < cutoff:
                    page_old_posts += 1
                    continue
                    
                title = item.get('title')
                full_url = f"https://www.reddit.com{item.get('permalink')}"
                
                existing = get_post(post_id)
                score = item.get('score', 0)
                num_comments = item.get('num_comments', 0)

                if existing and existing.get('body'):
                    update_post_stats(post_id, score, num_comments)
                    self.stats["skipped_deep"] += 1
                    posts_added += 1
                    page_processed += 1
                    continue

                post_data = {
                    'id': post_id,
                    'platform': 'reddit',
                    'source': subreddit_name,
                    'url': full_url,
                    'title': title,
                    'body': item.get('selftext', "").strip(),
                    'author': item.get('author'),
                    'score': score,
                    'num_comments': num_comments,
                    'created_at': datetime.fromtimestamp(created_utc).isoformat(),
                    'ingestion_method': 'scraper'
                }
                save_post(post_data)
                
                # Fetch comments
                if num_comments > 0:
                    self._smart_delay()
                    self._scrape_comments_json(post_id, subreddit_name)

                posts_added += 1
                page_processed += 1
            
            print(f"DEBUG: [r/{subreddit_name}] Page processed: {page_processed} saved, {page_old_posts} beyond cutoff. Total: {posts_added}", flush=True)

            # Termination conditions
            if not current_after or page_old_posts > 0:
                # If we found posts older than our cutoff, we can stop
                if page_old_posts > 0:
                    print(f"DEBUG: Hitting date cutoff for r/{subreddit_name}. Stopping.", flush=True)
                break
                
            after = current_after
            
        return posts_added

    def _scrape_comments_json(self, post_id: str, subreddit_name: str):
        """Scrape comments from a post using JSON endpoint."""
        simple_id = post_id.split('_')[1] if '_' in post_id else post_id
        url = f"https://www.reddit.com/r/{subreddit_name}/comments/{simple_id}/.json"
        
        data = self._request_with_retry(url)
        if not data or not isinstance(data, list) or len(data) < 2:
            return
            
        try:
            comments_data = data[1].get('data', {}).get('children', [])
            self._parse_json_comments(comments_data, post_id)
        except Exception as e:
            print(f"DEBUG: Error parsing comments JSON: {e}", flush=True)

    def _parse_json_comments(self, children: list, post_id: str, depth: int = 0):
        """Recursively parse JSON comments."""
        for child in children:
            if child.get('kind') != 't1':
                continue
                
            data = child.get('data', {})
            c_id = data.get('name')
            body = data.get('body', '').strip()
            
            if not c_id or not body:
                continue
                
            save_comment({
                'id': c_id,
                'post_id': post_id,
                'author': data.get('author'),
                'body': body,
                'score': data.get('score', 0),
                'created_at': datetime.fromtimestamp(data.get('created_utc', time.time())).isoformat(),
                'depth': depth
            })
            
            replies = data.get('replies')
            if replies and isinstance(replies, dict):
                reply_children = replies.get('data', {}).get('children', [])
                self._parse_json_comments(reply_children, post_id, depth + 1)

    def _get_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        delay = self.backoff_base * (2 ** attempt)
        delay = min(delay, self.backoff_max)
        # Add jitter (0 to delay)
        delay = random.uniform(delay * 0.5, delay)
        return delay

    def get_stats(self) -> dict:
        """Return scraping statistics."""
        total = max(self.stats["requests"], 1)
        return {
            **self.stats,
            "success_rate": f"{(self.stats['success'] / total) * 100:.1f}%",
            "current_delays": f"{self.min_delay:.1f}s - {self.max_delay:.1f}s",
        }
