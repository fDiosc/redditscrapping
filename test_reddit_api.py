import os
import praw
from dotenv import load_dotenv

def test_reddit_api():
    # Load environment variables from .env
    load_dotenv()
    
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "python:radar_test:v0.1.0")
    
    print("--- Reddit API Connection Test ---")
    
    if not client_id or not client_secret:
        print("ERROR: REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET not found in .env file.")
        print("Please create an app at https://www.reddit.com/prefs/apps and add the details to .env")
        return

    print(f"Using Client ID: {client_id[:5]}***")
    print(f"User Agent: {user_agent}")
    
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Test fetching a few posts from a popular subreddit
        subreddit_name = "indiehackers"
        print(f"\nAttempting to fetch latest posts from r/{subreddit_name}...")
        
        subreddit = reddit.subreddit(subreddit_name)
        for i, submission in enumerate(subreddit.new(limit=5), 1):
            print(f"{i}. [{submission.id}] {submission.title[:60]}...")
            
        print("\nSUCCESS: Reddit API is working and authorized.")
        
    except Exception as e:
        print(f"\nFAILURE: Could not connect to Reddit API.")
        print(f"Error detail: {e}")
        print("\nPossible reasons:")
        print("1. Invalid Client ID or Secret")
        print("2. The IP is still being blocked even via API (unlikely for Cloudflare)")
        print("3. PRAW library is not installed (run: pip install praw)")

if __name__ == "__main__":
    test_reddit_api()
