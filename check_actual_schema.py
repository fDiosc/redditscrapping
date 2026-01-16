import sqlite3
from radar.config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

for table in ['posts', 'post_analysis']:
    print(f"\nSchema for {table}:")
    columns = c.execute(f"PRAGMA table_info({table})").fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

conn.close()
