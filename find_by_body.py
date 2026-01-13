import sqlite3

DB_PATH = "data/radar.db"

def find_by_body():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    snippet = "sadly doesnt make it easy"
    print(f"\nSearching for body snippet: '{snippet}'")
    cursor.execute("SELECT id, title FROM posts WHERE body LIKE ?", (f"%{snippet}%",))
    row = cursor.fetchone()
    if row:
        print(f"FOUND! ID: {row['id']} | Title: {row['title']}")
    else:
        print("Not found in body. Searching in titles...")
        cursor.execute("SELECT id, title FROM posts WHERE title LIKE ?", (f"%{snippet}%",))
        row = cursor.fetchone()
        if row:
            print(f"FOUND! ID: {row['id']} | Title: {row['title']}")
        else:
            print("Still not found.")
            
    conn.close()

if __name__ == "__main__":
    find_by_body()
