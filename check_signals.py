import sqlite3
conn = sqlite3.connect('data/radar.db')
c = conn.cursor()
c.execute("""
    SELECT relevance_score, signals_json 
    FROM post_analysis 
    WHERE product_id = 'sonarpro' 
    ORDER BY relevance_score DESC 
    LIMIT 10
""")
for r in c.fetchall():
    score = r[0]
    signals = r[1] if r[1] else "NULL"
    print(f"{score:.1f} | {signals[:80]}")
conn.close()
