import sys
import os

# Add the project root to sys.path so we can import radar modules
sys.path.append(os.getcwd())

try:
    from radar.ingest.reddit_scraper import RedditScraper
    print("--- Local Scraper Diagnostic ---")
    
    scraper = RedditScraper()
    # Testing with r/aitools as seen in your production logs
    subreddit = "aitools"
    print(f"Attempting to fetch r/{subreddit} from local IP...")
    
    # fetch_subreddit_posts returns the count of posts found
    count = scraper.fetch_subreddit_posts(subreddit, days=1, limit=5)
    
    if count > 0:
        print(f"\nSUCCESS: Local IP worked! Found {count} posts.")
        print("This confirms the logic is fine, but Reddit is blocking your EC2 IP.")
    else:
        print(f"\nFAILURE: Local IP also returned 0 posts.")
        print("Check if r/{subreddit} has any new posts in the last 1 day.")
        
    print("\nScraper Stats:")
    print(scraper.get_stats())

except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure to run this script from the project root directory.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
