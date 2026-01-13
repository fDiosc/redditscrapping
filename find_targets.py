import sqlite3

DB_PATH = "data/radar.db"

def find_target_posts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    target_patterns = [
        "%marketer more hireable%",
        "%Made $100k with my SaaS%",
        "%founders trying to get better at validating%",
        "%validating ideas before building%",
        "%founders %validating%"
    ]
    
    print("\n--- Searching for Problematic Posts ---")
    for pattern in target_patterns:
        cursor.execute("SELECT id, title FROM posts WHERE title LIKE ?", (pattern,))
        rows = cursor.fetchall()
        if not rows:
            print(f"NOT FOUND: {pattern}")
        for row in rows:
            print(f"ID: {row['id']} | Title: {row['title']}")
            
    conn.close()

if __name__ == "__main__":
    find_target_posts()
