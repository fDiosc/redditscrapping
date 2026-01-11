from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import json
from radar.storage.db import get_connection
from radar.products import PRODUCTS
from radar.config import SUBREDDITS
from radar.ingest.reddit_scraper import RedditScraper
from radar.process.ai_analysis import analyze_post_with_ai
# Import other CLI logics directly if possible, or wrap them
from radar.cli import process as cli_process

app = FastAPI(title="Radar AI API")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/config")
async def get_config():
    return {
        "products": list(PRODUCTS.keys()),
        "subreddits": list(SUBREDDITS.keys())
    }

@app.get("/threads")
async def get_threads(product: str = "profitdoctor", limit: int = 50):
    conn = get_connection()
    conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
    cursor = conn.cursor()
    
    # We show threads ordered by relevance for the chosen product
    cursor.execute("""
        SELECT * FROM posts 
        WHERE relevance_score > 0 
        ORDER BY relevance_score DESC 
        LIMIT ?
    """, (limit,))
    threads = cursor.fetchall()
    conn.close()
    return threads

@app.post("/sync")
async def sync_data(
    background_tasks: BackgroundTasks,
    subreddits: List[str] = Query(...),
    days: int = 3,
    reports: List[str] = Query(["DIRECT_FIT"])
):
    """Trigger ingestion, processing, and selective report generation."""
    from radar.ingest.reddit_scraper import RedditScraper
    from radar.cli import process as cli_process
    from radar.cli import report as cli_report

    def run_sync():
        scraper_tool = RedditScraper()
        # 1. Ingest
        for sub in subreddits:
            scraper_tool.fetch_subreddit_posts(sub, limit=15, days=days)
        
        # 2. Process (includes change detection logic inside if updated)
        cli_process()

        # 3. Generate Selected Reports
        for report_type in reports:
            # We assume profitdoctor for now or iterate over all products
            for product in PRODUCTS.keys():
                try:
                    cli_report(product, mode=report_type)
                except:
                    pass

    background_tasks.add_task(run_sync)
    return {"status": "Sync and Report generation started"}

@app.get("/reports/download/{filename}")
async def download_report(filename: str):
    from fastapi.responses import FileResponse
    path = os.path.join("outputs/reports", filename)
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "File not found"}

@app.get("/reports")
async def list_reports():
    reports_dir = "outputs/reports"
    if not os.path.exists(reports_dir):
        return []
    return [f for f in os.listdir(reports_dir) if f.endswith(".md")]
