import sqlite3
import os

db_path = "data/radar.db"

def fix_db():
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check existing columns
    cursor.execute("PRAGMA table_info(post_analysis)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {existing_cols}")
    
    required_columns = [
        ("ai_analysis", "TEXT"),
        ("semantic_similarity", "REAL DEFAULT 0"),
        ("community_score", "REAL DEFAULT 0"),
        ("last_processed_score", "INTEGER DEFAULT -1"),
        ("last_processed_comments", "INTEGER DEFAULT -1"),
        ("triage_status", "TEXT"),
        ("triage_at", "TIMESTAMP"),
        ("triage_relevance_snapshot", "REAL"),
        ("triage_semantic_snapshot", "REAL"),
        ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ]
    
    for col_name, col_type in required_columns:
        if col_name not in existing_cols:
            print(f"Adding column {col_name} to post_analysis...")
            try:
                cursor.execute(f"ALTER TABLE post_analysis ADD COLUMN {col_name} {col_type}")
                conn.commit()
                print(f"Successfully added {col_name}")
            except Exception as e:
                print(f"FAILED to add {col_name}: {e}")
        else:
            print(f"Column {col_name} already exists.")
            
    # Verify again
    cursor.execute("PRAGMA table_info(post_analysis)")
    final_cols = [row[1] for row in cursor.fetchall()]
    print(f"Final columns: {final_cols}")
    
    if "updated_at" in final_cols:
        print("VERIFICATION SUCCESS: updated_at is present.")
    else:
        print("VERIFICATION FAILURE: updated_at is still missing.")
        
    conn.close()

if __name__ == "__main__":
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
    else:
        fix_db()
