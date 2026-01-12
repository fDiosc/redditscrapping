import sqlite3
import os

db_path = "data/radar.db"
conn = sqlite3.connect(db_path)
cursor = conn.row_factory = sqlite3.Row
cursor = conn.cursor()

columns = [
    ("ai_analysis", "TEXT"),
    ("semantic_similarity", "REAL DEFAULT 0"),
    ("community_score", "REAL DEFAULT 0"),
    ("last_processed_score", "INTEGER DEFAULT -1"),
    ("last_processed_comments", "INTEGER DEFAULT -1")
]

for col_name, col_type in columns:
    try:
        print(f"Adding {col_name}...")
        cursor.execute(f"ALTER TABLE posts ADD COLUMN {col_name} {col_type}")
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Error adding {col_name}: {e}")

conn.close()
