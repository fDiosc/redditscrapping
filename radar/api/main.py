from fastapi import FastAPI, BackgroundTasks, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Any
from pydantic import BaseModel
from radar.models.response import GenerateResponseRequest, FeedbackRequest
from radar.services.response_service import ResponseGenerator
from radar.api.auth import get_current_user
import os
import json
from radar.storage.db import get_connection
from radar.products import PRODUCTS
from radar.config import SUBREDDITS
from radar.ingest.reddit_scraper import RedditScraper
from radar.process.ai_analysis import analyze_post_with_ai
# Import other CLI logics directly if possible, or wrap them
from radar.cli import process as cli_process

app = FastAPI(title="SonarPro AI API")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/config")
async def get_config(user_id: str = Depends(get_current_user)):
    from radar.storage.db import get_products
    products = get_products(user_id)
    
    # Extract unique subreddits from user's products
    all_subs = set()
    for p in products:
        try:
            subs = json.loads(p['target_subreddits'])
            all_subs.update(subs)
        except:
            pass
            
    return {
        "products": [p['id'] for p in products],
        "subreddits": sorted(list(all_subs))
    }

@app.get("/threads")
async def get_threads(user_id: str = Depends(get_current_user), product: str = None, limit: int = 50):
    conn = get_connection()
    conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
    cursor = conn.cursor()
    
    # We show threads joined with their product-specific analysis and latest generated response
    # Filter by user_id to only show user's analysis
    cursor.execute("""
        SELECT p.*, pa.relevance_score, pa.semantic_similarity, pa.community_score, pa.ai_analysis, pa.signals_json,
               r.id as res_id, r.response_text as res_text, r.style as res_style, r.tokens_used as res_tokens
        FROM posts p
        JOIN post_analysis pa ON p.id = pa.post_id
        LEFT JOIN (
            SELECT id, post_id, product_id, user_id, response_text, style, tokens_used,
                   row_number() OVER (PARTITION BY post_id, product_id, user_id ORDER BY created_at DESC) as rn
            FROM generated_responses
            WHERE user_id = ?
        ) r ON p.id = r.post_id AND pa.product_id = r.product_id AND r.rn = 1
        WHERE pa.product_id = ? AND pa.user_id = ? AND pa.relevance_score > 0 
        ORDER BY pa.relevance_score DESC 
        LIMIT ?
    """, (user_id, product, user_id, limit))
    rows = cursor.fetchall()
    
    threads = []
    for row in rows:
        thread = dict(row)
        # Format the response if it exists
        if thread.get('res_id'):
            thread['generatedResponse'] = {
                "id": thread['res_id'],
                "response_text": thread['res_text'],
                "style": thread['res_style'],
                "tokens_used": thread['res_tokens']
            }
        threads.append(thread)
        
    conn.close()
    return threads

# Global state for sync tracking
SYNC_STATE = {
    "is_running": False,
    "last_sync": None,
    "current_step": "Idle",
    "progress": 0
}

@app.get("/sync/status")
async def get_sync_status():
    return SYNC_STATE

@app.get("/threads/{post_id}/comments")
async def get_post_comments(post_id: str):
    from radar.storage.db import get_comments
    return get_comments(post_id)

@app.get("/sync/history")
async def get_sync_history_api(user_id: str = Depends(get_current_user), limit: int = 10):
    from radar.storage.db import get_sync_history
    return get_sync_history(user_id, limit)

@app.post("/sync")
async def sync_data(
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    subreddits: List[str] = Query(...),
    days: int = 3,
    reports: List[str] = Query(["DIRECT_FIT"]),
    product: Optional[str] = None
):
    """Trigger ingestion, processing, and selective report generation for a user."""
    print(f"DEBUG: [API] Received sync request. User: {user_id}, Product: {product}, Subs: {subreddits}, Days: {days}", flush=True)
    if SYNC_STATE["is_running"]:
        print("DEBUG: [API] Rejecting sync - already in progress.", flush=True)
        return {"error": "Sync already in progress", "status": SYNC_STATE}

    from radar.storage.db import init_db, add_sync_run, update_sync_run_status
    from radar.ingest.reddit_scraper import RedditScraper
    from radar.cli import process as cli_process
    from radar.cli import report as cli_report
    from datetime import datetime

    run_id = add_sync_run(user_id, product or "all", subreddits, days)

    def run_sync():
        print("DEBUG: [Worker] Background sync started.", flush=True)
        try:
            # Ensure DB schema is up to date
            init_db()
            import time
            time.sleep(1)
            
            SYNC_STATE["progress"] = 0
            update_sync_run_status(run_id, "Ingesting", 10)
            
            scraper_tool = RedditScraper()
            # 1. Ingest
            for i, sub in enumerate(subreddits):
                print(f"DEBUG: [Worker] Ingesting r/{sub}...", flush=True)
                SYNC_STATE["current_step"] = f"Ingesting r/{sub}..."
                SYNC_STATE["progress"] = int((i / len(subreddits)) * 40)
                scraper_tool.fetch_subreddit_posts(sub, limit=15, days=days)
                import time
                time.sleep(0.5)
            
            # 2. Process
            print("DEBUG: [Worker] Starting processing/scoring.", flush=True)
            SYNC_STATE["current_step"] = "Analyzing and Scoring threads..."
            SYNC_STATE["progress"] = 60
            update_sync_run_status(run_id, "Processing", 60)
            import time
            time.sleep(1)
            cli_process(ai_analyze=True, target_product=product, subreddit_filter=subreddits, user_id=user_id)

            # 3. Generate Selected Reports
            print(f"DEBUG: [Worker] Generating reports for {product or 'all'}...", flush=True)
            SYNC_STATE["current_step"] = f"Generating reports for {product or 'all products'}..."
            SYNC_STATE["progress"] = 80
            update_sync_run_status(run_id, "Reporting", 80)
            import time
            time.sleep(1)
            
            from radar.storage.db import get_products
            all_db_products = get_products(user_id=user_id)
            target_products = [product] if product else [p['id'] for p in all_db_products]
            
            for report_type in reports:
                for p_key in target_products:
                    try:
                        cli_report(p_key, mode=report_type)
                    except Exception as re:
                        print(f"DEBUG: [Worker] Report error for {p_key}: {re}", flush=True)
            
            SYNC_STATE["last_sync"] = datetime.now().isoformat()
            SYNC_STATE["current_step"] = "Success"
            SYNC_STATE["progress"] = 100
            update_sync_run_status(run_id, "Success", 100)
            print("DEBUG: [Worker] Sync completed successfully.", flush=True)
        except Exception as e:
            print(f"DEBUG: [Worker] Sync failed with error: {e}", flush=True)
            SYNC_STATE["current_step"] = f"Error: {str(e)}"
            update_sync_run_status(run_id, f"Error: {str(e)[:50]}", SYNC_STATE["progress"])
        finally:
            # Keep the 100% or error message for a few seconds if polled, 
            # but we allow new syncs after a reset or in the next call
            import time
            time.sleep(2) 
            SYNC_STATE["is_running"] = False
            print("DEBUG: [Worker] Sync background task finalized.", flush=True)

    SYNC_STATE["is_running"] = True
    SYNC_STATE["progress"] = 0
    SYNC_STATE["current_step"] = "Initializing..."
    background_tasks.add_task(run_sync)
    return {"status": "Sync and Report generation started"}

@app.get("/api/products")
async def list_products_api(user_id: str = Depends(get_current_user)):
    from radar.storage.db import get_products
    return get_products(user_id)

@app.get("/api/products/{product_id}")
async def get_product_api(product_id: str, user_id: str = Depends(get_current_user)):
    from radar.storage.db import get_product
    product = get_product(product_id, user_id)
    if not product:
        return {"error": "Product not found"}
    return product

@app.post("/api/products")
async def create_product_api(product_data: dict, user_id: str = Depends(get_current_user)):
    from radar.services.product_service import upsert_product
    # Generate ID from name if not provided
    if 'id' not in product_data:
        product_data['id'] = product_data['name'].lower().replace(" ", "")
    
    product_data['user_id'] = user_id
    upsert_product(product_data)
    return {"id": product_data['id'], "status": "saved"}

@app.put("/api/products/{product_id}")
async def update_product_api(product_id: str, product_data: dict, user_id: str = Depends(get_current_user)):
    from radar.services.product_service import upsert_product
    from radar.storage.db import get_product
    existing = get_product(product_id, user_id)
    if not existing:
        return {"error": "Product not found"}
    
    product_data['id'] = product_id
    product_data['user_id'] = user_id
    upsert_product(product_data)
    return {"id": product_id, "status": "updated"}

@app.delete("/api/products/{product_id}")
async def delete_product_api(product_id: str, user_id: str = Depends(get_current_user)):
    from radar.storage.db import delete_product
    delete_product(product_id, user_id)
    return {"status": "deleted"}

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

# RGIG Phase 1: Response Generation
@app.post("/api/responses/generate/{post_id}")
async def generate_response_api(post_id: str, request: GenerateResponseRequest, user_id: str = Depends(get_current_user)):
    generator = ResponseGenerator()
    try:
        result = generator.generate_response(user_id, post_id, request.product_id, request.style)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/responses/history/{post_id}")
async def get_response_history_api(post_id: str, product_id: str, user_id: str = Depends(get_current_user), limit: int = 5):
    from radar.storage.db import get_generated_responses
    return get_generated_responses(user_id, post_id, product_id, limit)

@app.post("/api/responses/{response_id}/feedback")
async def submit_feedback_api(response_id: str, request: FeedbackRequest):
    from radar.storage.db import update_response_feedback
    update_response_feedback(response_id, request.feedback)
    return {"status": "ok"}

@app.get("/api/settings/{key}")
async def get_setting_api(key: str, user_id: str = Depends(get_current_user)):
    from radar.storage.db import get_user_setting
    return {"key": key, "value": get_user_setting(user_id, key)}

class SettingRequest(BaseModel):
    key: str
    value: Any

@app.post("/api/settings")
async def save_setting_api(req: SettingRequest, user_id: str = Depends(get_current_user)):
    from radar.storage.db import save_user_setting
    save_user_setting(user_id, req.key, req.value)
    return {"status": "ok"}
