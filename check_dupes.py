import sqlite3
from radar.config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

c.execute("""
    SELECT post_id, product_id, COUNT(*)
    FROM post_analysis
    GROUP BY post_id, product_id
    HAVING COUNT(*) > 1
""")

dupes = c.fetchall()
if dupes:
    print(f"Found {len(dupes)} duplicate pairs in post_analysis!")
    for d in dupes:
        print(f"Post: {d[0]} | Product: {d[1]} | Count: {d[2]}")
else:
    print("No duplicates found in post_analysis table.")

conn.close()
