import sqlite3
import os
import json
from radar.config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

title = "How do you find actionable feedback and demand before building?"
print(f"Investigating title: {title}\n")

c.execute("""
    SELECT p.id, p.source, p.author, length(p.body) as body_len, 
           pa.relevance_score, pa.ai_analysis, p.body
    FROM posts p
    JOIN post_analysis pa ON p.id = pa.post_id
    WHERE p.title = ? AND pa.product_id = 'sonarpro'
""", (title,))

rows = c.fetchall()
for i, r in enumerate(rows, 1):
    print(f"--- Post {i} ---")
    print(f"ID: {r['id']}")
    print(f"Source: {r['source']}")
    print(f"Author: u/{r['author']}")
    print(f"Body Length: {r['body_len']} chars")
    
    # Check if body starts with different text
    body_preview = r['body'][:100].replace('\n', ' ')
    print(f"Body Preview: {body_preview}...")
    
    try:
        ai = json.loads(r['ai_analysis']) if r['ai_analysis'] else {}
        print(f"Result (DB): {'🚨 SPAM/AD' if ai.get('is_spam_or_ad') else '✅ OK'}")
        if ai.get('is_spam_or_ad'):
            print(f"Indicators: {ai.get('spam_indicators')}")
    except:
        print("AI Analysis: Error parsing JSON")
    print("-" * 30)

conn.close()
