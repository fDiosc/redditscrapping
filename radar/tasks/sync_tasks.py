"""
Celery tasks for Reddit sync operations.
These tasks run asynchronously in the background, allowing the API to return immediately.
"""
from radar.celery_app import celery_app
from radar.storage.db import (
    add_sync_run, 
    update_sync_run_status, 
    close_thread_connection
)


@celery_app.task(bind=True, name="radar.tasks.sync_tasks.run_sync")
def run_sync_task(self, user_id: str, subreddits: list, days: int, product: str, run_id: int):
    """
    Async task to run Reddit sync.
    
    Args:
        user_id: The user's ID
        subreddits: List of subreddits to scrape
        days: Number of days to look back
        product: Product ID to analyze for
        run_id: The sync run ID for status updates
    """
    try:
        from radar.ingest.reddit_scraper import RedditScraper
        from radar.cli import process as cli_process
        
        # Update status: Ingesting
        update_sync_run_status(run_id, "Ingesting posts...", 10)
        
        # Scrape posts
        scraper = RedditScraper(use_proxy=False)
        total_posts = 0
        for i, sub in enumerate(subreddits):
            progress = 10 + int((i / len(subreddits)) * 40)  # 10-50%
            update_sync_run_status(run_id, f"Scraping r/{sub}...", progress)
            
            try:
                posts = scraper.get_subreddit_posts(sub, limit=50, days=days)
                total_posts += len(posts)
                
                for post in posts:
                    scraper.process_post(post)
            except Exception as e:
                print(f"Error scraping r/{sub}: {e}")
                continue
        
        # Update status: Processing
        update_sync_run_status(run_id, "Processing with AI...", 60)
        
        # Process posts
        cli_process(
            ai_analyze=True,
            batch=20,
            target_product=product,
            subreddit_filter=subreddits,
            user_id=user_id
        )
        
        # Update status: Complete
        update_sync_run_status(run_id, "Success", 100)
        
    except Exception as e:
        error_msg = f"Error: {str(e)[:100]}"
        update_sync_run_status(run_id, error_msg, 100)
        raise
    finally:
        # Clean up thread-local connection
        close_thread_connection()


@celery_app.task(name="radar.tasks.sync_tasks.refresh_product_embedding")
def refresh_product_embedding_task(product_id: str, user_id: str):
    """
    Async task to refresh a product's embedding after updates.
    """
    try:
        from radar.process.semantic import SemanticEngine
        
        engine = SemanticEngine(user_id=user_id)
        engine.refresh_product(product_id, user_id)
    finally:
        close_thread_connection()
