import os
import sqlite3
from radar.config import DATABASE_PATH, CHROMA_PATH
from radar.storage.db import init_db

def check():
    print(f"--- Radar Health Check ---")
    print(f"DB Path: {os.path.abspath(DATABASE_PATH)}")
    print(f"Chroma Path: {os.path.abspath(CHROMA_PATH)}")
    
    if not os.path.exists(os.path.dirname(DATABASE_PATH)):
        print(f"Error: Database directory missing!")
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # Run Init
    print("Running init_db()...")
    init_db()
    
    # Verify Columns
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(posts)")
    cols = [r[1] for r in cursor.fetchall()]
    conn.close()
    
    required = ["last_processed_score", "last_processed_comments", "semantic_similarity"]
    missing = [c for c in required if c not in cols]
    
    if missing:
        print(f"CRITICAL: Missing columns: {missing}")
    else:
        print("Success: Database schema is correct.")

if __name__ == "__main__":
    check()
