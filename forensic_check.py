import sqlite3
import os

db_path = "data/radar.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, source, score, last_processed_score, num_comments, last_processed_comments, embedding_id FROM posts WHERE source = 'socialmedia' LIMIT 5")
rows = cursor.fetchall()
print(f"Posts in DB ({db_path}):")
for r in rows:
    print(dict(r))

conn.close()
