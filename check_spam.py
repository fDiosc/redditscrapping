from radar.storage.db import get_connection
import sqlite3, json

conn = get_connection()
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("""SELECT ai_analysis FROM post_analysis 
             WHERE product_id = 'sonarpro' 
             ORDER BY relevance_score DESC LIMIT 1""")
r = c.fetchone()
ai = json.loads(r[0])
print('is_spam_or_ad:', ai.get('is_spam_or_ad'))
print('spam_indicators:', ai.get('spam_indicators'))
conn.close()
