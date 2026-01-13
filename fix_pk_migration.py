import sqlite3
import os

db_path = "data/radar.db"

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting migration to fix primary key...")
    
    # 1. Start transaction
    cursor.execute("BEGIN TRANSACTION")
    
    try:
        # 2. Backup old table
        print("Backing up data...")
        cursor.execute("ALTER TABLE post_analysis RENAME TO post_analysis_old")
        
        # 3. Create new table with correct Primary Key
        print("Creating new table with correct schema...")
        cursor.execute("""
        CREATE TABLE post_analysis (
            post_id TEXT,
            product_id TEXT,
            user_id TEXT DEFAULT 'default_user',
            relevance_score REAL DEFAULT 0,
            semantic_similarity REAL DEFAULT 0,
            community_score REAL DEFAULT 0,
            ai_analysis TEXT,
            signals_json TEXT,
            last_processed_score INTEGER DEFAULT -1,
            last_processed_comments INTEGER DEFAULT -1,
            triage_status TEXT,
            triage_at TIMESTAMP,
            triage_relevance_snapshot REAL,
            triage_semantic_snapshot REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (post_id, product_id, user_id),
            FOREIGN KEY (post_id) REFERENCES posts(id)
        )
        """)
        
        # 4. Copy data
        print("Migrating data to new table...")
        cursor.execute("""
        INSERT INTO post_analysis (
            post_id, product_id, user_id, relevance_score, semantic_similarity,
            community_score, ai_analysis, signals_json, last_processed_score,
            last_processed_comments, triage_status, triage_at,
            triage_relevance_snapshot, triage_semantic_snapshot, updated_at
        )
        SELECT 
            post_id, product_id, user_id, relevance_score, semantic_similarity,
            community_score, ai_analysis, signals_json, last_processed_score,
            last_processed_comments, triage_status, triage_at,
            triage_relevance_snapshot, triage_semantic_snapshot, updated_at
        FROM post_analysis_old
        """)
        
        # 5. Drop old table
        print("Cleaning up old table...")
        cursor.execute("DROP TABLE post_analysis_old")
        
        conn.commit()
        print("MIGRATION SUCCESSFUL!")
        
    except Exception as e:
        print(f"MIGRATION FAILED: {e}")
        conn.rollback()
        raise
        
    conn.close()

if __name__ == "__main__":
    migrate()
