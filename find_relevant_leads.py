import sqlite3

DB_PATH = "data/radar.db"

def find_truly_relevant():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Search for high intent keywords related to social media tools
    search_terms = ["ig", "instagram", "tiktok", "reels", "posts", "content", "schedule", "automate", "tool", "help"]
    
    print("\n--- Searching for Potentially Truly Relevant Leads ---")
    query = """
        SELECT id, title FROM posts 
        WHERE (title LIKE '%tiktok%' OR title LIKE '%instagram%' OR title LIKE '%ig %' OR title LIKE '%content%')
        AND (title LIKE '%how%' OR title LIKE '%help%' OR title LIKE '%recommend%' OR title LIKE '%tool%' OR title LIKE '%strategy%')
        LIMIT 20
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row['id']} | Title: {row['title'][:100]}")
            
    conn.close()

if __name__ == "__main__":
    find_truly_relevant()
