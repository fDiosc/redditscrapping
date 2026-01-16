from radar.storage.db import get_connection
import sqlite3

conn = get_connection()
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute('''SELECT post_id, relevance_score, semantic_similarity 
             FROM post_analysis 
             WHERE product_id = 'sonarpro' 
             ORDER BY post_id LIMIT 10''')
rows = c.fetchall()
for r in rows:
    print(f"Score={r['relevance_score']:.1f} Fit={r['semantic_similarity']:.2f}")
conn.close()
