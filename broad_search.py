import sqlite3

DB_PATH = "data/radar.db"

def search_broadly():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    terms = ["founders", "validating", "ideas", "building", "hire someone"]
    
    print("\n--- Broad Search Results ---")
    for term in terms:
        print(f"\nSearching for term: {term}")
        cursor.execute("SELECT id, title FROM posts WHERE title LIKE ? OR body LIKE ?", (f"%{term}%", f"%{term}%"))
        results = cursor.fetchall()
        print(f"  Found {len(results)} matches in posts.")
        for r in results[:5]: # Show first 5 matches for each term
            print(f"    ID: {r['id']} | Title: {r['title'][:70]}...")
            
    conn.close()

if __name__ == "__main__":
    search_broadly()
