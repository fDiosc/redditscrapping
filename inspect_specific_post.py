import sqlite3
import json

DB_PATH = "data/radar.db"
USER_ID = "user_38AZ6aLnRe6N9Oe22TjNdpn5DFF"

def inspect_post():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    pid = "t3_1q8a99r"
    print(f"\n--- Detailed Inspection for Post {pid} ---")
    cursor.execute("SELECT * FROM post_analysis WHERE post_id = ? AND user_id = ?", (pid, USER_ID))
    row = cursor.fetchone()
    if row:
        data = dict(row)
        print(f"Post ID: {data['post_id']}")
        print(f"Product ID: {data['product_id']}")
        print(f"User ID: {data['user_id']}")
        print(f"Relevance Score: {data['relevance_score']}")
        print(f"Semantic Similarity: {data['semantic_similarity']}")
        print(f"Community Score: {data['community_score']}")
        print(f"Signals JSON: {data['signals_json']}")
    else:
        print("Record not found.")
            
    conn.close()

if __name__ == "__main__":
    inspect_post()
