"""Check data/radar.db tables"""
import sqlite3
import os

db_path = 'data/radar.db'
if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("Tables:", tables)

for table in tables:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cursor.fetchall()]
    print(f"\n{table}: {cols}")
