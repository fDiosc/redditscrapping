import sqlite3
from typing import List

def get_unprocessed_posts(db_path, subreddit_filter=None):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT id, source, last_processed_comments, num_comments, embedding_id FROM posts 
        WHERE (embedding_id IS NULL 
        OR score != last_processed_score 
        OR num_comments != last_processed_comments)
    """
    params = []
    
    if subreddit_filter:
        placeholders = ', '.join(['?'] * len(subreddit_filter))
        query += f" AND source IN ({placeholders})"
        params.extend(subreddit_filter)
        
    print(f"Running query: {query}")
    print(f"With params: {params}")
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

db_path = "data/radar.db"
pending = get_unprocessed_posts(db_path, ["socialmedia"])
print(f"Found {len(pending)} pending posts for socialmedia.")
for p in pending[:3]:
    print(p)
