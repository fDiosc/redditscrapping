import sqlite3
import json
import os
import threading
from typing import List, Dict, Any, Optional
from radar.config import DATABASE_PATH

# Lock for thread-safe database access
_db_lock = threading.Lock()

def get_connection():
    """
    Get a SQLite connection.
    NOTE: Each call returns a new connection. The caller should NOT close it
    if they want to keep using it within the same function.
    """
    # Ensure directory exists
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH, timeout=30, check_same_thread=False)
    # Enable Write-Ahead Logging for better concurrency
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")  # 30 second busy timeout
    except:
        pass
    
    return conn


def close_thread_connection():
    """Legacy function - no longer needed but kept for compatibility."""
    pass

def init_db():
    from radar.config import DATABASE_PATH
    print(f"DEBUG: Initializing database at {DATABASE_PATH}")
    conn = get_connection()
    cursor = conn.cursor()
    
    # Posts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        platform TEXT NOT NULL,
        source TEXT NOT NULL,
        url TEXT,
        title TEXT,
        body TEXT,
        author TEXT,
        score INTEGER DEFAULT 0,
        num_comments INTEGER DEFAULT 0,
        created_at TIMESTAMP,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ingestion_method TEXT,
        embedding_id TEXT,
        pain_signals TEXT,
        intent TEXT,
        relevance_score REAL DEFAULT 0,
        ai_analysis TEXT,
        semantic_similarity REAL DEFAULT 0,
        community_score REAL DEFAULT 0,
        last_processed_score INTEGER DEFAULT -1,
        last_processed_comments INTEGER DEFAULT -1
    )
    """)
    
    # Comments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id TEXT PRIMARY KEY,
        post_id TEXT NOT NULL,
        parent_id TEXT,
        body TEXT,
        author TEXT,
        score INTEGER DEFAULT 0,
        created_at TIMESTAMP,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        depth INTEGER DEFAULT 0,
        embedding_id TEXT,
        pain_signals TEXT,
        is_solution BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (post_id) REFERENCES posts(id)
    )
    """)
    
    # Post Analysis table (per-product, per-user)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS post_analysis (
        post_id TEXT,
        product_id TEXT,
        user_id TEXT DEFAULT 'default_user',
        relevance_score REAL DEFAULT 0,
        semantic_similarity REAL DEFAULT 0,
        community_score REAL DEFAULT 0,
        ai_analysis TEXT,
        signals_json TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (post_id, product_id, user_id),
        FOREIGN KEY (post_id) REFERENCES posts(id)
    )
    """)

    # Products table (per-user)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id TEXT,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        pain_signals TEXT NOT NULL,
        intent_signals TEXT NOT NULL,
        target_subreddits TEXT NOT NULL,
        embedding_context TEXT,
        embedding_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        website_url TEXT,
        default_response_style TEXT DEFAULT 'empathetic',
        PRIMARY KEY (id, user_id)
    )
    """)

    # Sync runs history (per-user)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sync_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        product TEXT,
        subreddits TEXT,
        days INTEGER,
        status TEXT,
        progress INTEGER DEFAULT 0
    )
    """)
    
    # Generated responses (per-user)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS generated_responses (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        post_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        style TEXT NOT NULL DEFAULT 'empathetic',
        response_text TEXT NOT NULL,
        tokens_used INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        feedback TEXT,
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    
    # Migration: add new columns if missing to post_analysis
    columns = [
        ("ai_analysis", "TEXT"),
        ("semantic_similarity", "REAL DEFAULT 0"),
        ("community_score", "REAL DEFAULT 0"),
        ("last_processed_score", "INTEGER DEFAULT -1"),
        ("last_processed_comments", "INTEGER DEFAULT -1"),
        ("triage_status", "TEXT"), # 'agree', 'disagree', NULL
        ("triage_at", "TIMESTAMP"),
        ("triage_relevance_snapshot", "REAL"),
        ("triage_semantic_snapshot", "REAL"),
        ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ]
    for col_name, col_type in columns:
        try:
            cursor.execute(f"ALTER TABLE post_analysis ADD COLUMN {col_name} {col_type}")
            conn.commit()
        except sqlite3.OperationalError:
            pass # Already exists

    # Triage History (per-user/product/post feedback log)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS triage_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        status TEXT NOT NULL,
        relevance_score REAL,
        semantic_similarity REAL,
        community_score REAL,
        ai_analysis_snapshot TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id)
    )
    """)
    conn.commit()
    # User Settings table (per-user)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        user_id TEXT NOT NULL,
        key TEXT NOT NULL,
        value TEXT,
        PRIMARY KEY (user_id, key)
    )
    """)
    
    # Migration: add user_id columns to existing tables
    user_id_migrations = [
        ("products", "user_id", "TEXT"),
        ("post_analysis", "user_id", "TEXT"),
        ("generated_responses", "user_id", "TEXT"),
        ("sync_runs", "user_id", "TEXT"),
    ]
    for table, col_name, col_type in user_id_migrations:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
            conn.commit()
            print(f"DEBUG: Added {col_name} column to {table}")
        except sqlite3.OperationalError:
            pass  # Already exists

    # Migration: add website_url to products
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN website_url TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # Migration: add default_response_style to products
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN default_response_style TEXT DEFAULT 'empathetic'")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # Migration: add embedding_vector to products (cached embedding as JSON)
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN embedding_vector TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.close()

def save_post(post_data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT OR REPLACE INTO posts (
        id, platform, source, url, title, body, author, 
        score, num_comments, created_at, ingestion_method
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        post_data['id'], post_data['platform'], post_data['source'],
        post_data.get('url'), post_data.get('title'), post_data.get('body'),
        post_data.get('author'), post_data.get('score', 0), 
        post_data.get('num_comments', 0), post_data.get('created_at'),
        post_data.get('ingestion_method')
    ))
    
    conn.commit()
    conn.close()

def update_post_stats(post_id: str, score: int, num_comments: int):
    """Surgical update for post metrics without overwriting body/content."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE posts 
        SET score = ?, num_comments = ?, scraped_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (score, num_comments, post_id))
    conn.commit()
    conn.close()

def save_comment(comment_data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT OR REPLACE INTO comments (
        id, post_id, parent_id, body, author, 
        score, created_at, depth
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        comment_data['id'], comment_data['post_id'], comment_data.get('parent_id'),
        comment_data.get('body'), comment_data.get('author'),
        comment_data.get('score', 0), comment_data.get('created_at'),
        comment_data.get('depth', 0)
    ))
    
    conn.commit()
    conn.close()

def save_analysis(post_id: str, product_id: str, user_id: str, data: Dict[str, Any], cursor=None):
    """Save post analysis for a specific user's product. Preserves triage status and existing AI on update."""
    # Use COALESCE to preserve existing ai_analysis when new value is NULL
    query = """
    INSERT INTO post_analysis (
        post_id, product_id, user_id, relevance_score, semantic_similarity, 
        community_score, ai_analysis, signals_json, updated_at,
        last_processed_score, last_processed_comments
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
    ON CONFLICT(post_id, product_id, user_id) DO UPDATE SET
        relevance_score = excluded.relevance_score,
        semantic_similarity = excluded.semantic_similarity,
        community_score = excluded.community_score,
        ai_analysis = COALESCE(excluded.ai_analysis, post_analysis.ai_analysis),
        signals_json = excluded.signals_json,
        last_processed_score = excluded.last_processed_score,
        last_processed_comments = excluded.last_processed_comments,
        updated_at = CURRENT_TIMESTAMP
    """
    params = (
        post_id, product_id, user_id, data.get('relevance_score', 0),
        data.get('semantic_similarity', 0), data.get('community_score', 0),
        data.get('ai_analysis'), data.get('signals_json'),
        data.get('last_processed_score', -1), data.get('last_processed_comments', -1)
    )
    
    if cursor:
        cursor.execute(query, params)
    else:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        conn.close()


def get_existing_analysis(post_id: str, product_id: str, user_id: str):
    """Get existing analysis for a post/product/user combo. Returns dict or None."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ai_analysis, relevance_score, semantic_similarity 
        FROM post_analysis 
        WHERE post_id = ? AND product_id = ? AND user_id = ?
    """, (post_id, product_id, user_id))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_triage_status(user_id: str, product_id: str, post_id: str, status: str):
    """Update triage status and record snapshots/history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Fetch current metrics and AI analysis for snapshot
    cursor.execute("""
        SELECT relevance_score, semantic_similarity, community_score, ai_analysis
        FROM post_analysis
        WHERE post_id = ? AND product_id = ? AND user_id = ?
    """, (post_id, product_id, user_id))
    current = cursor.fetchone()
    
    if current:
        rel, sem, com, ai = current
        # 2. Update post_analysis with status and snapshots
        cursor.execute("""
            UPDATE post_analysis 
            SET triage_status = ?, 
                triage_at = CURRENT_TIMESTAMP, 
                updated_at = CURRENT_TIMESTAMP,
                triage_relevance_snapshot = ?,
                triage_semantic_snapshot = ?
            WHERE post_id = ? AND product_id = ? AND user_id = ?
        """, (status, rel, sem, post_id, product_id, user_id))
        
        # 3. Log into triage_history for future AI training
        # Map None to 'null' for history because of NOT NULL constraint
        history_status = status if status is not None else "null"
        cursor.execute("""
            INSERT INTO triage_history (
                post_id, product_id, user_id, status, 
                relevance_score, semantic_similarity, community_score, ai_analysis_snapshot
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (post_id, product_id, user_id, history_status, rel, sem, com, ai))
        
    conn.commit()
    conn.close()

def get_post(post_id: str):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_analysis(post_id: str, product_id: str, user_id: str = None):
    """Get analysis for a post. If user_id provided, filter by user."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM post_analysis WHERE post_id = ? AND product_id = ? AND user_id = ?", (post_id, product_id, user_id))
    else:
        cursor.execute("SELECT * FROM post_analysis WHERE post_id = ? AND product_id = ?", (post_id, product_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_unprocessed_posts(subreddit_filter: List[str] = None, limit: int = None, force: bool = False, user_id: str = None, product_id: str = None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    params = []
    
    if force:
        query = "SELECT * FROM posts"
    elif user_id and product_id and product_id != "all":
        # Multi-tenant logic: Get posts that:
        # 1. Need global embedding (p.embedding_id IS NULL)
        # 2. Don't have an analysis for this SPECIFIC product/user (pa.post_id IS NULL)
        # 3. Metrics changed since THIS user last analyzed it 
        query = """
            SELECT p.* FROM posts p
            LEFT JOIN post_analysis pa ON p.id = pa.post_id 
                AND pa.product_id = ? AND pa.user_id = ?
            WHERE (p.embedding_id IS NULL 
            OR pa.post_id IS NULL 
            OR p.score != pa.last_processed_score 
            OR p.num_comments != pa.last_processed_comments)
        """
        params.extend([product_id, user_id])
    else:
        # Legacy/Global logic: Get posts that need embedding or global score update
        query = """
            SELECT * FROM posts 
            WHERE (embedding_id IS NULL 
            OR score != last_processed_score 
            OR num_comments != last_processed_comments)
        """
    
    # Subreddit filter
    if subreddit_filter:
        placeholders = ', '.join(['?'] * len(subreddit_filter))
        condition = f"source IN ({placeholders})"
        if "WHERE" in query:
            query += f" AND p.{condition}" if "p." in query else f" AND {condition}"
        else:
            query += f" WHERE p.{condition}" if "p." in query else f" WHERE {condition}"
        params.extend(subreddit_filter)
        
    # Limit
    if limit:
        query += " LIMIT ?"
        params.append(limit)
        
    try:
        cursor.execute(query, params)
    except sqlite3.OperationalError as e:
        # Fallback for older schemas or missing columns
        print(f"DEBUG: DB Query failed ({e}), falling back...")
        fallback_query = "SELECT * FROM posts WHERE embedding_id IS NULL"
        if force: fallback_query = "SELECT * FROM posts"
        cursor.execute(fallback_query)
    
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return [dict(row) for row in rows]

def add_sync_run(user_id: str, product: str, subreddits: List[str], days: int):
    """Add a sync run record for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sync_runs (user_id, product, subreddits, days, status, progress)
        VALUES (?, ?, ?, ?, 'Running', 0)
    """, (user_id, product, ', '.join(subreddits), days))
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id

def update_sync_run_status(run_id: int, status: str, progress: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sync_runs SET status = ?, progress = ? WHERE id = ?", (status, progress, run_id))
    conn.commit()
    conn.close()

def get_comments(post_id: str):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments WHERE post_id = ? ORDER BY score DESC", (post_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_comments_bulk(post_ids: List[str]) -> Dict[str, List[Dict]]:
    """
    Fetch comments for multiple posts in a single query.
    Returns a dict mapping post_id -> list of comments.
    
    This fixes the N+1 query problem when processing multiple posts.
    """
    if not post_ids:
        return {}
    
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    placeholders = ', '.join(['?'] * len(post_ids))
    cursor.execute(f"""
        SELECT * FROM comments 
        WHERE post_id IN ({placeholders})
        ORDER BY post_id, score DESC
    """, post_ids)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Group by post_id
    result = {pid: [] for pid in post_ids}
    for row in rows:
        row_dict = dict(row)
        post_id = row_dict['post_id']
        if post_id in result:
            result[post_id].append(row_dict)
    
    return result

def get_sync_history(user_id: str = None, limit: int = 10):
    """Get sync history. If user_id provided, filter by user."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM sync_runs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
    else:
        cursor.execute("SELECT * FROM sync_runs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_products(user_id: str = None) -> List[Dict[str, Any]]:
    """Get products. If user_id provided, filter by user."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM products WHERE user_id = ? ORDER BY name ASC", (user_id,))
    else:
        cursor.execute("SELECT * FROM products ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_product(product_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
    """Get a product by ID. If user_id provided, filter by user."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM products WHERE id = ? AND user_id = ?", (product_id, user_id))
    else:
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_product_record(product_data: Dict[str, Any]):
    """Save a product record. Requires user_id in product_data."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Handle array types by converting to JSON strings if they aren't already strings
    pain_signals = product_data['pain_signals']
    if not isinstance(pain_signals, str):
        pain_signals = json.dumps(pain_signals)
        
    intent_signals = product_data['intent_signals']
    if not isinstance(intent_signals, str):
        intent_signals = json.dumps(intent_signals)
        
    target_subreddits = product_data['target_subreddits']
    if not isinstance(target_subreddits, str):
        target_subreddits = json.dumps(target_subreddits)

    cursor.execute("""
    INSERT OR REPLACE INTO products (
        id, user_id, name, description, pain_signals, intent_signals, 
        target_subreddits, embedding_context, embedding_id, updated_at, website_url, default_response_style
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
    """, (
        product_data['id'],
        product_data['user_id'],
        product_data['name'],
        product_data['description'],
        pain_signals,
        intent_signals,
        target_subreddits,
        product_data.get('embedding_context'),
        product_data.get('embedding_id'),
        product_data.get('website_url'),
        product_data.get('default_response_style', 'empathetic')
    ))
    
    conn.commit()
    conn.close()

def delete_product(product_id: str, user_id: str):
    """Delete a product for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ? AND user_id = ?", (product_id, user_id))
    conn.commit()
    conn.close()


def update_product_embedding(product_id: str, user_id: str, embedding: List[float], context: str = None):
    """
    Update the cached embedding for a product.
    Stores the embedding as JSON for portability.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    embedding_json = json.dumps(embedding)
    
    if context:
        cursor.execute("""
            UPDATE products 
            SET embedding_vector = ?, embedding_context = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        """, (embedding_json, context, product_id, user_id))
    else:
        cursor.execute("""
            UPDATE products 
            SET embedding_vector = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        """, (embedding_json, product_id, user_id))
    
    conn.commit()
    conn.close()


def get_product_embedding(product_id: str, user_id: str) -> Optional[List[float]]:
    """
    Get the cached embedding for a product.
    Returns None if no cached embedding exists.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT embedding_vector FROM products 
        WHERE id = ? AND user_id = ?
    """, (product_id, user_id))
    
    row = cursor.fetchone()
    conn.close()
    
    if row and row['embedding_vector']:
        try:
            return json.loads(row['embedding_vector'])
        except (json.JSONDecodeError, TypeError):
            return None
    return None

def save_generated_response(user_id: str, post_id: str, product_id: str, style: str, response_text: str, tokens_used: int):
    """Save a generated response for a user."""
    import uuid
    conn = get_connection()
    cursor = conn.cursor()
    response_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO generated_responses (id, user_id, post_id, product_id, style, response_text, tokens_used)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (response_id, user_id, post_id, product_id, style, response_text, tokens_used))
    conn.commit()
    conn.close()
    return response_id

def get_generated_responses(user_id: str, post_id: str, product_id: str, limit: int = 5):
    """Get generated responses for a user's product."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM generated_responses 
        WHERE user_id = ? AND post_id = ? AND product_id = ? 
        ORDER BY created_at DESC LIMIT ?
    """, (user_id, post_id, product_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_response_feedback(response_id: str, feedback: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE generated_responses SET feedback = ? WHERE id = ?", (feedback, response_id))
    conn.commit()
    conn.close()

def get_user_setting(user_id: str, key: str, default: Any = None) -> Any:
    """Get a user setting by key for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM user_settings WHERE user_id = ? AND key = ?", (user_id, key))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            return json.loads(row[0])
        except:
            return row[0]
    return default

def save_user_setting(user_id: str, key: str, value: Any):
    """Save a user setting for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    val_str = json.dumps(value) if not isinstance(value, str) else value
    cursor.execute("INSERT OR REPLACE INTO user_settings (user_id, key, value) VALUES (?, ?, ?)", (user_id, key, val_str))
    conn.commit()
    conn.close()
