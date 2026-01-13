import sqlite3

DB_PATH = "data/radar.db"

def find_missing_lead():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n--- Searching for Founders/Validating Posts ---")
    cursor.execute("SELECT id, title FROM posts WHERE title LIKE '%founders%' OR title LIKE '%validating%'")
    rows = cursor.fetchall()
    with open("found_leads.txt", "w", encoding="utf-8") as f:
        for row in rows:
            f.write(f"ID: {row['id']} | Title: {row['title']}\n")
    print(f"Found {len(rows)} potential leads. Written to found_leads.txt")
            
    conn.close()

if __name__ == "__main__":
    find_missing_lead()
