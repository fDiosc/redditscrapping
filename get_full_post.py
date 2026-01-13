import sqlite3

DB_PATH = "data/radar.db"

def get_post_content():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    pid = "t3_1q8a99r"
    cursor.execute("SELECT title, body FROM posts WHERE id = ?", (pid,))
    row = cursor.fetchone()
    if row:
        print(f"Title: {row['title']}")
        print(f"\nBody:\n{row['body']}")
    else:
        print("Post not found.")
            
    conn.close()

if __name__ == "__main__":
    get_post_content()
