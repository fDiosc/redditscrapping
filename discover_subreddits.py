import sqlite3
import json
import praw
import csv
import time
import os
from radar.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, DATABASE_PATH

def get_socialgenius_keywords():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT pain_signals, intent_signals FROM products WHERE id = 'socialgenius'")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return []
        
    try:
        pain = json.loads(row['pain_signals'])
        intent = json.loads(row['intent_signals'])
        return list(set(pain + intent))
    except:
        return []

def run_discovery():
    print("--- SOCIALGENIUS SUBREDDIT DISCOVERY (API VERSION) ---")
    
    # Initialize PRAW
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    
    keywords = get_socialgenius_keywords()
    if not keywords:
        keywords = ["social media marketing", "instagram content", "tiktok growth", "content strategy"]
        print(f"Using fallback keywords: {keywords}")
    else:
        print(f"Loaded {len(keywords)} keywords from database.")

    discovered_subs = {}

    # Search for subreddits using each keyword
    for kw in keywords[:10]: # Limit keywords for the test
        print(f"Searching for '{kw}'...")
        try:
            for subreddit in reddit.subreddits.search(kw, limit=20):
                sub_name = subreddit.display_name
                if sub_name not in discovered_subs:
                    discovered_subs[sub_name] = {
                        "subreddit": f"r/{sub_name}",
                        "subscribers": subreddit.subscribers,
                        "description": subreddit.public_description[:500],
                        "keyword_match": kw,
                        "relevance_score": 0
                    }
        except Exception as e:
            print(f"Error searching for {kw}: {e}")
        time.sleep(1)

    # Calculate a simple relevance score for found subreddits
    for sub_name, data in discovered_subs.items():
        text_to_check = f"{sub_name} {data['description']}".lower()
        score = 0
        for kw in keywords:
            if kw.lower() in text_to_check:
                score += 1
        data['relevance_score'] = score

    # Sort and rank
    ranked = sorted(discovered_subs.values(), key=lambda x: (-x['relevance_score'], -x['subscribers']))
    
    output_file = "socialgenius_top_20_discovery.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["subreddit", "relevance_score", "subscribers", "keyword_match", "description"])
        w.writeheader()
        for r in ranked[:20]:
            w.writerow(r)

    print(f"\nSUCCESS: Top 20 subreddits saved to {output_file}")
    print("\nPREVIEW TOP 10:")
    print(f"{'Subreddit':<25} | {'Score':<5} | {'Subscribers':<12}")
    print("-" * 50)
    for r in ranked[:10]:
        print(f"{r['subreddit']:<25} | {r['relevance_score']:<5} | {r['subscribers']:<12,}")

if __name__ == "__main__":
    run_discovery()
