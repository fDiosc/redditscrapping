import sqlite3
import os

db_path = "radar_data.db"
if not os.path.exists(db_path):
    # Try alternate path if config.py says so
    db_path = "data/radar.db"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print(f"Checking {db_path}...")

# Check posts from socialmedia
cursor.execute("SELECT id, title, embedding_id, last_processed_comments FROM posts WHERE source = 'socialmedia' LIMIT 5")
rows = cursor.fetchall()
print(f"\nSocialMedia Posts ({len(rows)}):")
for r in rows:
    print(dict(r))

# Check comments for a post
if rows:
    p_id = rows[0]['id']
    cursor.execute("SELECT count(*) as count FROM comments WHERE post_id = ?", (p_id,))
    c_count = cursor.fetchone()['count']
    print(f"\nComments for {p_id}: {c_count}")

conn.close()
