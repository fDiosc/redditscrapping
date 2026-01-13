from radar.storage.db import init_db
import sqlite3
import os

if __name__ == "__main__":
    db_path = "data/radar.db"
    print(f"Forcing database migration on {db_path}...")
    init_db()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(post_analysis)")
    cols = [row[1] for row in cursor.fetchall()]
    print(f"Columns in post_analysis: {cols}")
    
    if "updated_at" in cols:
        print("SUCCESS: updated_at column found.")
    else:
        print("ERROR: updated_at column MISSING.")
        
    conn.close()
