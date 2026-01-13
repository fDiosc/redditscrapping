"""
Reddit Scraper with Anti-Ban Phase 1 MVP
- User-Agent rotation
- Complete browser headers
- Rate limiting with jitter
- Exponential backoff
- Retry handler
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from radar.storage.db import save_post, save_comment, get_post, update_post_stats


# Pool of modern browser User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]


class RedditScraper:
    """Scraper with anti-ban protections for Reddit."""
    
    def __init__(self):
        # Rate limiting config
        self.min_delay = 2.0
        self.max_delay = 5.0
        self.burst_probability = 0.15  # 15% chance of extra delay
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
    
    def _get_headers(self) -> dict:
        """Generate browser-like headers with random User-Agent."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
    
    def _smart_delay(self):
        """Apply human-like delay with jitter between requests."""
        base_delay = random.uniform(self.min_delay, self.max_delay)
        
        # Occasionally add extra delay (simulates human distraction)
        if random.random() < self.burst_probability:
            base_delay *= self.burst_multiplier
            print(f"DEBUG: Adding burst delay ({base_delay:.1f}s)", flush=True)
        
        # Add micro-jitter (±10%)
        jitter = base_delay * random.uniform(-0.1, 0.1)
        final_delay = base_delay + jitter
        
        time.sleep(final_delay)
    
    def _request_with_retry(self, url: str) -> requests.Response:
        """
        Make request with exponential backoff and retry.
        Returns response or None if all retries failed.
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                self.stats["requests"] += 1
                headers = self._get_headers()
                
                response = requests.get(url, headers=headers, timeout=15)
                
                # Handle rate limiting
                if response.status_code == 429:
                    self.stats["rate_limited"] += 1
                    wait_time = self._get_backoff_delay(attempt)
                    print(f"DEBUG: Rate limited (429). Waiting {wait_time:.1f}s before retry {attempt + 1}/{self.max_retries}", flush=True)
                    
                    # Increase future delays after rate limit
                    self.min_delay = min(self.min_delay * 1.5, 10.0)
                    self.max_delay = min(self.max_delay * 1.5, 20.0)
                    
                    time.sleep(wait_time)
                    self.stats["retries"] += 1
                    continue
                
                # Handle server errors (5xx)
                if response.status_code >= 500:
                    wait_time = self._get_backoff_delay(attempt)
                    print(f"DEBUG: Server error ({response.status_code}). Waiting {wait_time:.1f}s", flush=True)
                    time.sleep(wait_time)
                    self.stats["retries"] += 1
                    continue
                
                # Success or client error (don't retry 4xx except 429)
                if response.status_code == 200:
                    self.stats["success"] += 1
                return response
                
            except requests.exceptions.Timeout:
                wait_time = self._get_backoff_delay(attempt)
                print(f"DEBUG: Timeout. Waiting {wait_time:.1f}s before retry {attempt + 1}/{self.max_retries}", flush=True)
                time.sleep(wait_time)
                self.stats["retries"] += 1
                last_exception = "Timeout"
                
            except requests.exceptions.RequestException as e:
                wait_time = self._get_backoff_delay(attempt)
                print(f"DEBUG: Request error: {e}. Waiting {wait_time:.1f}s", flush=True)
                time.sleep(wait_time)
                self.stats["retries"] += 1
                last_exception = e
        
        self.stats["failed"] += 1
        print(f"DEBUG: All retries exhausted. Last error: {last_exception}", flush=True)
        return None
    
    def _get_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        delay = self.backoff_base * (2 ** attempt)
        delay = min(delay, self.backoff_max)
        # Add jitter (0 to delay)
        delay = random.uniform(delay * 0.5, delay)
        return delay
    
    def fetch_subreddit_posts(self, subreddit_name: str, days: int = 7, limit: int = 20):
        """Fetch posts from a subreddit with anti-ban protections."""
        url = f"https://old.reddit.com/r/{subreddit_name}/new/"
        
        # Apply delay before initial request
        self._smart_delay()
        response = self._request_with_retry(url)

        if not response or response.status_code != 200:
            status_code = response.status_code if response else "NO_RESPONSE"
            print(f"DEBUG: Failed to fetch r/{subreddit_name} (Status: {status_code})", flush=True)
            return 0
            
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', class_='thing')
        
        posts_count = 0
        for item in items[:limit]:
            post_id = item.get('data-fullname')
            title_elem = item.find('a', class_='title')
            if not title_elem:
                continue
                
            title = title_elem.text
            url = title_elem['href']
            
            # CHECK: If already indexed with content, skip deep scrape
            existing = get_post(post_id)
            score = int(item.get('data-score', 0))
            num_comments = int(item.get('data-comments-count', 0))
            full_url = f"https://reddit.com{url}" if url.startswith('/') else url.replace("old.reddit.com", "reddit.com")

            if existing and existing.get('body'):
                print(f"DEBUG: [{subreddit_name}] Skipping deep scrape for existing post: {title[:40]}...", flush=True)
                update_post_stats(post_id, score, num_comments)
                self.stats["skipped_deep"] += 1
                posts_count += 1
                continue

            # Deep scrape to get the body
            body = ""
            scrape_url = full_url.replace("reddit.com", "old.reddit.com")
            
            if "/comments/" in full_url:
                # Apply delay before detail page request
                self._smart_delay()
                
                detail_res = self._request_with_retry(scrape_url)
                if detail_res and detail_res.status_code == 200:
                    detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
                    body_div = detail_soup.find('div', class_='expando')
                    if body_div:
                        body = body_div.text.strip()
                        
                    # Scrape comments
                    self._scrape_comments(detail_soup, post_id)

            post_data = {
                'id': post_id,
                'platform': 'reddit',
                'source': subreddit_name,
                'url': full_url,
                'title': title,
                'body': body,
                'author': item.get('data-author'),
                'score': score,
                'num_comments': num_comments,
                'created_at': datetime.utcnow().isoformat(),
                'ingestion_method': 'scraper'
            }
            save_post(post_data)
            posts_count += 1
            print(f"DEBUG: [{subreddit_name}] Formally Scraped: {title[:40]}...", flush=True)
            
            # Apply delay between posts
            self._smart_delay()
            
        print(f"DEBUG: Scraper stats - {self.stats}", flush=True)
        return posts_count
    
    def _scrape_comments(self, soup: BeautifulSoup, post_id: str):
        """Scrape comments from a post detail page."""
        comment_items = soup.select('div.comment')
        comments_saved = 0
        
        for c_item in comment_items:
            try:
                c_id = c_item.get('data-fullname')
                if not c_id:
                    continue
                
                c_author = c_item.get('data-author')
                c_content_div = c_item.select_one('div.md')
                c_body = c_content_div.text.strip() if c_content_div else ""
                
                # Skip very short or empty comments
                if len(c_body) < 5:
                    continue
                
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
                comments_saved += 1
            except Exception as ce:
                pass
        
        return comments_saved
    
    def get_stats(self) -> dict:
        """Return scraping statistics."""
        total = max(self.stats["requests"], 1)
        return {
            **self.stats,
            "success_rate": f"{(self.stats['success'] / total) * 100:.1f}%",
            "current_delays": f"{self.min_delay:.1f}s - {self.max_delay:.1f}s",
        }
