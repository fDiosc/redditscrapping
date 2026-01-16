import sqlite3
import os

db_path = 'radar.db'
if not os.path.exists(db_path):
    # Try to find the DB path from environment or config
    from radar.config import DATABASE_PATH
    db_path = DATABASE_PATH

conn = sqlite3.connect(db_path)
c = conn.cursor()
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    table_name = t[0]
    columns = c.execute(f"PRAGMA table_info({table_name})").fetchall()
    print(f"Table {table_name}: {[col[1] for col in columns]}")
conn.close()
