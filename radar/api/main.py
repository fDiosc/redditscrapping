from fastapi import FastAPI, BackgroundTasks, Query, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Any
from pydantic import BaseModel
from radar.models.response import GenerateResponseRequest, FeedbackRequest
from radar.services.response_service import ResponseGenerator
from radar.api.auth import get_current_user, get_optional_user
import os
import json
from radar.storage.db import get_connection
from radar.products import PRODUCTS
from radar.config import SUBREDDITS
from radar.ingest.reddit_scraper import RedditScraper
from radar.process.ai_analysis import analyze_post_with_ai
# Import other CLI logics directly if possible, or wrap them
from radar.cli import process as cli_process

# Rate Limiting with slowapi
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address)
    RATE_LIMITING_ENABLED = True
except ImportError:
    # slowapi not installed, disable rate limiting
    limiter = None
    RATE_LIMITING_ENABLED = False

app = FastAPI(title="SonarPro AI API")

# Configure rate limiting if available
if RATE_LIMITING_ENABLED:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    from radar.storage.db import init_db
    init_db()
    

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/config")
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

@app.get("/api/threads")
async def get_threads(user_id: str = Depends(get_current_user), product: str = None, limit: int = 50):
    conn = get_connection()
    conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
    cursor = conn.cursor()
    
    # Filter by user_id to only show user's analysis
    cursor.execute("""
        SELECT p.*, pa.relevance_score, pa.semantic_similarity, pa.community_score, pa.ai_analysis, pa.signals_json, 
               pa.triage_status, pa.triage_relevance_snapshot,
               CASE 
                 WHEN pa.triage_status IS NOT NULL 
                      AND ABS(pa.relevance_score - IFNULL(pa.triage_relevance_snapshot, 0)) > 1.0 
                 THEN 1 ELSE 0 
               END as is_stale,
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

@app.post("/api/threads/{post_id}/triage")
async def triage_thread(
    post_id: str, 
    status: str = Query(..., pattern="^(agree|disagree|null)$"),
    product_id: str = Query(...),
    user_id: str = Depends(get_current_user)
):
    """Save user feedback for a lead."""
    from radar.storage.db import update_triage_status
    # Map 'null' string to None for DB
    db_status = None if status == "null" else status
    update_triage_status(user_id, product_id, post_id, db_status)
    return {"status": "success", "triage": status}

@app.get("/api/sync/status")
async def get_sync_status(user_id: Optional[str] = Depends(get_optional_user)):
    if not user_id:
        # Check if there's any active run globally just for debug, 
        # but normally we want this to be per-user.
        return {
            "is_running": False, 
            "current_step": "Authentication required", 
            "progress": 0,
            "error": "Unauthorized"
        }
        
    from radar.storage.db import get_sync_history, update_sync_run_status
    from datetime import datetime, timedelta
    
    history = get_sync_history(user_id, limit=1)
    if not history:
        return {"is_running": False, "current_step": "Idle", "progress": 0}
    
    latest = history[0]
    status = latest['status']
    is_running = status != 'Success' and not status.startswith('Error')
    
    # STUCK SYNC DETECTION: If running for more than 15 minutes, consider it stuck
    if is_running:
        try:
            # Parse timestamp and check if it's older than 15 minutes
            sync_time = datetime.fromisoformat(latest['timestamp'].replace('Z', '+00:00'))
            now = datetime.now(sync_time.tzinfo) if sync_time.tzinfo else datetime.now()
            
            if now - sync_time > timedelta(minutes=15):
                # Mark as timed out
                update_sync_run_status(latest['id'], "Error: Sync timed out", 0)
                return {
                    "is_running": False,
                    "current_step": "Sync timed out - try again",
                    "progress": 0,
                    "was_stuck": True
                }
        except (ValueError, TypeError, KeyError):
            # If we can't parse the timestamp, just continue
            pass
    
    return {
        "is_running": is_running,
        "last_sync": latest['timestamp'] if not is_running else None,
        "current_step": latest['status'],
        "progress": latest['progress']
    }

@app.get("/api/threads/{post_id}/comments")
async def get_post_comments(post_id: str):
    from radar.storage.db import get_comments
    return get_comments(post_id)

@app.get("/api/sync/history")
async def get_sync_history_api(user_id: str = Depends(get_current_user), limit: int = 10):
    from radar.storage.db import get_sync_history
    return get_sync_history(user_id, limit)

@app.post("/api/sync")
async def sync_data(
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    subreddits: List[str] = Query(...),
    days: int = 3,
    product: Optional[str] = None
):
    from radar.storage.db import add_sync_run, update_sync_run_status, get_sync_history
    from radar.ingest.reddit_scraper import RedditScraper
    from radar.cli import process as cli_process
    from datetime import datetime

    # Check if this specific user has a run in progress
    history = get_sync_history(user_id, limit=1)
    if history:
        status = history[0]['status']
        is_active = status != 'Success' and not status.startswith('Error')
        if is_active:
            return {"error": "Sync already in progress for your account", "status": history[0]}

    run_id = add_sync_run(user_id, product or "all", subreddits, days)

    def run_sync():
        try:
            update_sync_run_status(run_id, "Ingesting", 10)
            
            scraper_tool = RedditScraper(user_id=user_id)
            for i, sub in enumerate(subreddits):
                progress = 10 + int((i / len(subreddits)) * 40)
                update_sync_run_status(run_id, f"Ingesting r/{sub}...", progress)
                scraper_tool.fetch_subreddit_posts(sub, days=days)
                import time
                time.sleep(0.5)
            
            # 2. Process
            update_sync_run_status(run_id, "Analyzing and Scoring threads...", 60)
            cli_process(ai_analyze=True, target_product=product, subreddit_filter=subreddits, user_id=user_id)

            update_sync_run_status(run_id, "Success", 100)
        except Exception as e:
            update_sync_run_status(run_id, f"Error: {str(e)[:100]}", 0)
        finally:
            # No global variable to reset!
            pass

    update_sync_run_status(run_id, "Initializing...", 5)
    background_tasks.add_task(run_sync)
    return {"status": "Sync started", "run_id": run_id}

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

@app.get("/api/reports/download/{filename}")
async def download_report(filename: str):
    from fastapi.responses import FileResponse
    path = os.path.join("outputs/reports", filename)
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "File not found"}

@app.get("/api/reports")
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


# ============================================
# Smart Product Setup Endpoints
# ============================================

class URLExtractionRequest(BaseModel):
    url: str

@app.post("/api/extract/url")
async def extract_product_from_url(request: Request, url_request: URLExtractionRequest, user_id: str = Depends(get_current_user)):
    """Extract product information from a website URL using AI."""
    from radar.services.product_extractor import ProductExtractor
    
    extractor = ProductExtractor()
    try:
        result = await extractor.extract_from_url(url_request.url)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


class SubredditSuggestionRequest(BaseModel):
    category: str
    pain_signals: Optional[List[str]] = None
    intent_signals: Optional[List[str]] = None

@app.post("/api/subreddits/suggest")
async def suggest_subreddits_api(request: SubredditSuggestionRequest, user_id: str = Depends(get_current_user)):
    """Suggest relevant subreddits based on product category and signals."""
    from radar.services.product_extractor import suggest_subreddits
    
    suggestions = suggest_subreddits(
        request.category,
        request.pain_signals,
        request.intent_signals
    )
    
    return {"suggestions": suggestions}


# ============================================
# Infrastructure Endpoints
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    from datetime import datetime
    
    # Check database connection
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }
