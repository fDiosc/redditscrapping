import sqlite3
from typing import List, Dict, Any, Optional
from radar.config import DATABASE_PATH

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def init_db():
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

def get_unprocessed_posts():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE embedding_id IS NULL")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
