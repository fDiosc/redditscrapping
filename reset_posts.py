import sqlite3
import os

db_path = "data/radar.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Resetting socialmedia posts in {db_path}...")
cursor.execute("""
    UPDATE posts 
    SET last_processed_comments = -1, last_processed_score = -1 
    WHERE source = 'socialmedia'
""")
print(f"Rows affected: {cursor.rowcount}")

conn.commit()
conn.close()
