import sqlite3

DB_PATH = "data/radar.db"

def find_posts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    titles = [
        "What makes a marketer more hireable - industry specialization or technical skills?",
        "Made $100k with my SaaS in 12 months. Here’s what worked and what didn’t",
        "I have been seeing many founders trying to get better at validating ideas before building"
    ]
    
    for title in titles:
        print(f"\nSearching for: {title[:50]}...")
        cursor.execute("SELECT id, title, score, num_comments FROM posts WHERE title LIKE ?", (f"%{title[:50]}%",))
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row['id']} | Title: {row['title']} | Score: {row['score']} | Comments: {row['num_comments']}")
            
    conn.close()

if __name__ == "__main__":
    find_posts()
