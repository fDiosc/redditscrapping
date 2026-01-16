import sqlite3
import os

from radar.config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()
r = c.execute("SELECT body, length(body) as len FROM posts WHERE title LIKE '%actionable feedback%'").fetchone()
if r:
    print(f"Length: {r['len']}")
    print("-" * 20)
    print(r['body'])
    print("-" * 20)
else:
    print("Post not found")
conn.close()
