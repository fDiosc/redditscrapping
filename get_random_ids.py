import sqlite3

DB_PATH = "data/radar.db"
USER_ID = "user_38AZ6aLnRe6N9Oe22TjNdpn5DFF"

def get_random_ids():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT post_id 
        FROM post_analysis 
        WHERE product_id = 'socialgenius' AND user_id = ? 
        ORDER BY RANDOM() LIMIT 5
    """, (USER_ID,))
    
    ids = [row['post_id'] for row in cursor.fetchall()]
    print(",".join(ids))
    conn.close()

if __name__ == "__main__":
    get_random_ids()
