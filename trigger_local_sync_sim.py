import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from radar.storage.db import init_db, add_sync_run, update_sync_run_status
from radar.ingest.reddit_scraper import RedditScraper
from radar.cli import process as cli_process
from radar.cli import report as cli_report

def trigger_local_sync():
    user_id = "default_user"
    product = "sonarpro"
    subreddits = ["aitools"]
    days = 1
    reports = ["DIRECT_FIT"]

    print(f"--- Triggering Local Sync Simulation ---")
    print(f"User: {user_id}")
    print(f"Product: {product}")
    print(f"Subreddits: {subreddits}")
    
    init_db()
    run_id = add_sync_run(user_id, product, subreddits, days)
    print(f"Sync Run ID: {run_id}")

    try:
        # 1. Ingest
        update_sync_run_status(run_id, "Ingesting", 10)
        scraper = RedditScraper()
        total_ingested = 0
        for sub in subreddits:
            print(f"Ingesting r/{sub}...")
            count = scraper.fetch_subreddit_posts(sub, limit=15, days=days)
            total_ingested += count
            print(f"Found {count} posts in r/{sub}")

        # 2. Process
        update_sync_run_status(run_id, "Processing", 60)
        print("Starting processing/scoring...")
        cli_process(ai_analyze=True, target_product=product, subreddit_filter=subreddits, user_id=user_id)

        # 3. Report
        update_sync_run_status(run_id, "Reporting", 80)
        for report_type in reports:
            print(f"Generating {report_type} report...")
            cli_report(product, mode=report_type)

        update_sync_run_status(run_id, "Success", 100)
        print("\n--- Sync Completed Successfully ---")

    except Exception as e:
        print(f"\n--- Sync Failed ---")
        print(f"Error: {e}")
        update_sync_run_status(run_id, f"Error: {str(e)[:50]}", 0)

if __name__ == "__main__":
    trigger_local_sync()
