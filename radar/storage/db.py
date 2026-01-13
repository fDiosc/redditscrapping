import sqlite3
import json
from typing import List, Dict, Any, Optional
from radar.config import DATABASE_PATH

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH, timeout=30)
    # Enable Write-Ahead Logging for better concurrency
    try:
        conn.execute("PRAGMA journal_mode=WAL")
    except:
        pass
    return conn

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
        user_id TEXT,
        relevance_score REAL DEFAULT 0,
        semantic_similarity REAL DEFAULT 0,
        community_score REAL DEFAULT 0,
        ai_analysis TEXT,
        signals_json TEXT,
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
    
    # Migration: add new columns if missing
    columns = [
        ("ai_analysis", "TEXT"),
        ("semantic_similarity", "REAL DEFAULT 0"),
        ("community_score", "REAL DEFAULT 0"),
        ("last_processed_score", "INTEGER DEFAULT -1"),
        ("last_processed_comments", "INTEGER DEFAULT -1")
    ]
    for col_name, col_type in columns:
        try:
            cursor.execute(f"ALTER TABLE posts ADD COLUMN {col_name} {col_type}")
            conn.commit()
        except sqlite3.OperationalError:
            pass # Already exists
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
    """Save post analysis for a specific user's product."""
    if cursor:
        cursor.execute("""
        INSERT OR REPLACE INTO post_analysis (
            post_id, product_id, user_id, relevance_score, semantic_similarity, 
            community_score, ai_analysis, signals_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post_id, product_id, user_id, data.get('relevance_score', 0),
            data.get('semantic_similarity', 0), data.get('community_score', 0),
            data.get('ai_analysis'), data.get('signals_json')
        ))
    else:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT OR REPLACE INTO post_analysis (
            post_id, product_id, user_id, relevance_score, semantic_similarity, 
            community_score, ai_analysis, signals_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post_id, product_id, user_id, data.get('relevance_score', 0),
            data.get('semantic_similarity', 0), data.get('community_score', 0),
            data.get('ai_analysis'), data.get('signals_json')
        ))
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

def get_unprocessed_posts(subreddit_filter: List[str] = None, limit: int = None, force: bool = False):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if force:
        query = "SELECT * FROM posts"
    else:
        query = """
            SELECT * FROM posts 
            WHERE (embedding_id IS NULL 
            OR score != last_processed_score 
            OR num_comments != last_processed_comments)
        """
    
    params = []
    
    # Subreddit filter
    if subreddit_filter:
        placeholders = ', '.join(['?'] * len(subreddit_filter))
        if "WHERE" in query:
            query += f" AND source IN ({placeholders})"
        else:
            query += f" WHERE source IN ({placeholders})"
        params.extend(subreddit_filter)
        
    # Limit
    if limit:
        query += " LIMIT ?"
        params.append(limit)
        
    try:
        cursor.execute(query, params)
    except sqlite3.OperationalError:
        # Fallback if columns don't exist yet
        fallback_query = "SELECT * FROM posts WHERE embedding_id IS NULL"
        if force: fallback_query = "SELECT * FROM posts"
        
        if subreddit_filter:
            placeholders = ', '.join(['?'] * len(subreddit_filter))
            fallback_query += f" AND source IN ({placeholders})"
            if limit:
                fallback_query += " LIMIT ?"
                cursor.execute(fallback_query, params)
            else:
                cursor.execute(fallback_query, params)
        else:
            if limit:
                fallback_query += " LIMIT ?"
                cursor.execute(fallback_query, (limit,))
            else:
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
        target_subreddits, embedding_context, embedding_id, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        product_data['id'],
        product_data['user_id'],
        product_data['name'],
        product_data['description'],
        pain_signals,
        intent_signals,
        target_subreddits,
        product_data.get('embedding_context'),
        product_data.get('embedding_id')
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
