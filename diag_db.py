import sqlite3
import os

db_path = "data/radar.db"

def diag():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Current Schema for post_analysis ---")
    cursor.execute("PRAGMA table_info(post_analysis)")
    for row in cursor.fetchall():
        print(row)
        
    print("\nAttempting to add updated_at column...")
    try:
        # Try a simpler form first
        cursor.execute("ALTER TABLE post_analysis ADD COLUMN updated_at TIMESTAMP")
        conn.commit()
        print("SUCCESS: Added updated_at (simple)")
    except Exception as e:
        print(f"ERROR (simple): {e}")

    # Check again
    cursor.execute("PRAGMA table_info(post_analysis)")
    cols = [row[1] for row in cursor.fetchall()]
    if "updated_at" in cols:
        print("VERIFIED: updated_at exists.")
    else:
        print("STILL MISSING: updated_at.")
        
    conn.close()

if __name__ == "__main__":
    diag()
