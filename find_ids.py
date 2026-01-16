import sqlite3
from radar.config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

c.execute("""
    SELECT post_id, relevance_score
    FROM post_analysis 
    WHERE product_id = 'sonarpro'
    AND post_id IN (SELECT id FROM posts WHERE title = 'How do you find actionable feedback and demand before building?')
    ORDER BY relevance_score DESC
""")

rows = c.fetchall()
for r in rows:
    print(f"ID: {r[0]} | Score: {r[1]}")

conn.close()
