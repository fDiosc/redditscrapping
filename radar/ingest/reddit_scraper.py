"""
Reddit Scraper with Anti-Ban Phase 1 MVP
- User-Agent rotation
- Complete browser headers
- Rate limiting with jitter
- Exponential backoff
- Retry handler
- JSON endpoint support for www.reddit.com
"""
import requests
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
    """Scraper with anti-ban protections for Reddit using JSON fallback."""
    
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
        """Generate headers compatible with JSON endpoint."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
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
        """Fetch posts from a subreddit using JSON endpoint with anti-ban protections."""
        url = f"https://www.reddit.com/r/{subreddit_name}/new/.json?limit={limit}"
        
        # Apply delay before initial request
        self._smart_delay()
        response = self._request_with_retry(url)

        if not response or response.status_code != 200:
            status_code = response.status_code if response else "NO_RESPONSE"
            print(f"DEBUG: Failed to fetch r/{subreddit_name} (Status: {status_code})", flush=True)
            return 0
            
        try:
            data = response.json()
            items = data.get('data', {}).get('children', [])
        except Exception as e:
            print(f"DEBUG: Failed to parse JSON for r/{subreddit_name}: {e}", flush=True)
            return 0
        
        posts_count = 0
        for item_wrapper in items:
            item = item_wrapper.get('data', {})
            post_id = item.get('name') # e.g., t3_...
            if not post_id:
                continue
                
            title = item.get('title')
            permalink = item.get('permalink')
            full_url = f"https://www.reddit.com{permalink}"
            
            # CHECK: If already indexed with content, skip deep scrape
            existing = get_post(post_id)
            score = item.get('score', 0)
            num_comments = item.get('num_comments', 0)

            if existing and existing.get('body'):
                print(f"DEBUG: [{subreddit_name}] Skipping deep scrape for existing post: {title[:40]}...", flush=True)
                update_post_stats(post_id, score, num_comments)
                self.stats["skipped_deep"] += 1
                posts_count += 1
                continue

            # For JSON, the body IS in the 'selftext' field
            body = item.get('selftext', "").strip()
            
            post_data = {
                'id': post_id,
                'platform': 'reddit',
                'source': subreddit_name,
                'url': full_url,
                'title': title,
                'body': body,
                'author': item.get('author'),
                'score': score,
                'num_comments': num_comments,
                'created_at': datetime.fromtimestamp(item.get('created_utc', time.time())).isoformat(),
                'ingestion_method': 'scraper'
            }
            save_post(post_data)
            
            # Fetch comments via .json
            if num_comments > 0:
                self._scrape_comments_json(post_id, subreddit_name)

            posts_count += 1
            print(f"DEBUG: [{subreddit_name}] Formally Scraped (JSON): {title[:40]}...", flush=True)
            
            if posts_count >= limit:
                break
            
        print(f"DEBUG: Scraper stats - {self.stats}", flush=True)
        return posts_count

    def _scrape_comments_json(self, post_id: str, subreddit_name: str):
        """Scrape comments from a post using JSON endpoint."""
        # Reddit post IDs for comments usually don't have the t3_ prefix in the URL
        simple_id = post_id.split('_')[1] if '_' in post_id else post_id
        url = f"https://www.reddit.com/r/{subreddit_name}/comments/{simple_id}/.json"
        
        self._smart_delay()
        response = self._request_with_retry(url)
        
        if not response or response.status_code != 200:
            return 0
            
        try:
            data = response.json()
            if not isinstance(data, list) or len(data) < 2:
                return 0
                
            comments_data = data[1].get('data', {}).get('children', [])
            return self._parse_json_comments(comments_data, post_id)
        except Exception as e:
            print(f"DEBUG: Error parsing comments JSON: {e}", flush=True)
            return 0

    def _parse_json_comments(self, children: list, post_id: str, depth: int = 0) -> int:
        """Recursively parse JSON comments."""
        saved_count = 0
        for child in children:
            if child.get('kind') != 't1':
                continue
                
            data = child.get('data', {})
            c_id = data.get('name')
            body = data.get('body', '').strip()
            
            if not c_id or len(body) < 5:
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
            saved_count += 1
            
            # Parse replies
            replies = data.get('replies')
            if replies and isinstance(replies, dict):
                reply_children = replies.get('data', {}).get('children', [])
                saved_count += self._parse_json_comments(reply_children, post_id, depth + 1)
        
        return saved_count
    
    def get_stats(self) -> dict:
        """Return scraping statistics."""
        total = max(self.stats["requests"], 1)
        return {
            **self.stats,
            "success_rate": f"{(self.stats['success'] / total) * 100:.1f}%",
            "current_delays": f"{self.min_delay:.1f}s - {self.max_delay:.1f}s",
        }
