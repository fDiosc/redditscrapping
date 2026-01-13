import sqlite3
import os

DB_PATH = "data/radar.db"

def verify_multi_tenancy():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- Checking Post Analysis (User Isolation) ---")
    cursor.execute("SELECT user_id, COUNT(*) as count FROM post_analysis GROUP BY user_id")
    rows = cursor.fetchall()
    if not rows:
        print("No analysis records found.")
    for row in rows:
        print(f"User ID: {row['user_id']} | Analysis Count: {row['count']}")

    print("\n--- Checking Sync Runs (User Isolation) ---")
    cursor.execute("SELECT user_id, status, progress, timestamp FROM sync_runs ORDER BY timestamp DESC LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"User: {row['user_id']} | Status: {row['status']} | Progress: {row['progress']}% | Time: {row['timestamp']}")

    print("\n--- Checking Products (User Isolation) ---")
    cursor.execute("SELECT user_id, COUNT(*) as count FROM products GROUP BY user_id")
    rows = cursor.fetchall()
    for row in rows:
        print(f"User ID: {row['user_id']} | Product Count: {row['count']}")

    conn.close()

if __name__ == "__main__":
    verify_multi_tenancy()
