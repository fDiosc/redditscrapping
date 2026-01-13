import sqlite3

DB_PATH = "data/radar.db"

def find_specific_leadbody():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Looking for 'IG/TIKTOK' mentions
    print("\n--- Searching for 'IG/TIKTOK' mentions ---")
    cursor.execute("SELECT id, title, body FROM posts WHERE body LIKE '%TIKTOK%' OR title LIKE '%TIKTOK%'")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row['id']} | Title: {row['title']}")
            
    conn.close()

if __name__ == "__main__":
    find_specific_leadbody()
