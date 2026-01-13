import sqlite3
import os

db_path = "data/radar.db"

def inspect_schema():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- post_analysis SQL ---")
    cursor.execute("SELECT sql FROM sqlite_master WHERE name='post_analysis'")
    print(cursor.fetchone()[0])
    
    print("\n--- post_analysis PRAGMA table_info ---")
    cursor.execute("PRAGMA table_info(post_analysis)")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    inspect_schema()
