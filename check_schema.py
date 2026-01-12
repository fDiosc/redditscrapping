import sqlite3
import os

db_path = "data/radar.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(posts)")
columns = cursor.fetchall()
print("Columns in 'posts':")
for col in columns:
    print(col)

conn.close()
