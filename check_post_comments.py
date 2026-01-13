import sqlite3

DB_PATH = "data/radar.db"

def check_comments():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    pid = "t3_1q8a99r"
    cursor.execute("SELECT body FROM comments WHERE post_id = ? AND body LIKE '%instagram%'", (pid,))
    rows = cursor.fetchall()
    print(f"Post {pid} has {len(rows)} comments mentioning instagram.")
    for row in rows:
        print(f"\nComment:\n{row['body']}\n")
            
    conn.close()

if __name__ == "__main__":
    check_comments()
