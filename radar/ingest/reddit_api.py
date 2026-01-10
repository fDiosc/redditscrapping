import praw
from datetime import datetime, timedelta
from typing import List, Dict, Any
from radar.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from radar.storage.db import save_post, save_comment

class RedditAPI:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )

    def fetch_subreddit_posts(self, subreddit_name: str, days: int = 7, limit: int = 100):
        subreddit = self.reddit.subreddit(subreddit_name)
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        posts_count = 0
        for submission in subreddit.new(limit=limit):
            if datetime.fromtimestamp(submission.created_utc) < cutoff:
                break
            
            post_data = {
                'id': f"reddit_{submission.id}",
                'platform': 'reddit',
                'source': subreddit_name,
                'url': submission.url,
                'title': submission.title,
                'body': submission.selftext,
                'author': str(submission.author),
                'score': submission.score,
                'num_comments': submission.num_comments,
                'created_at': datetime.fromtimestamp(submission.created_utc).isoformat(),
                'ingestion_method': 'api'
            }
            save_post(post_data)
            posts_count += 1
            
        return posts_count

    def fetch_post_comments(self, post_id: str, limit: int = 50):
        # post_id here is the internal one, e.g. "reddit_abc123"
        reddit_id = post_id.split('_')[1]
        submission = self.reddit.submission(id=reddit_id)
        submission.comments.replace_more(limit=0)
        
        comments_count = 0
        for comment in submission.comments.list()[:limit]:
            comment_data = {
                'id': f"comment_{comment.id}",
                'post_id': post_id,
                'parent_id': f"comment_{comment.parent_id.split('_')[1]}" if comment.parent_id.startswith('t1_') else None,
                'body': comment.body,
                'author': str(comment.author),
                'score': comment.score,
                'created_at': datetime.fromtimestamp(comment.created_utc).isoformat(),
                'depth': comment.depth
            }
            save_comment(comment_data)
            comments_count += 1
            
        return comments_count
