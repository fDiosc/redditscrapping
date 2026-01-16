import sqlite3
from radar.config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

print("Cleaning up duplicates in post_analysis...")

# 1. Create a temporary table with unique rows (keeping the newest if we had a timestamp, but here we just keep one)
# Since we don't have a reliable primary key id in post_analysis, we'll use ROWID
c.execute("""
    DELETE FROM post_analysis
    WHERE ROWID NOT IN (
        SELECT MIN(ROWID)
        FROM post_analysis
        GROUP BY post_id, product_id
    )
""")

print(f"Removed {conn.total_changes} duplicate rows.")

# 2. Add UNIQUE constraint (via unique index in SQLite)
try:
    c.execute("CREATE UNIQUE INDEX idx_post_product_unique ON post_analysis(post_id, product_id)")
    print("Added UNIQUE index for (post_id, product_id).")
except sqlite3.OperationalError:
    print("UNIQUE index already exists (or failed to create).")

conn.commit()
conn.close()
print("Cleanup complete.")
