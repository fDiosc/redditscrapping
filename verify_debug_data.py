import sqlite3

DATABASE_PATH = "data/radar.db"
USER_ID = "user_38AZ6aLnRe6N9Oe22TjNdpn5DFF"

def verify_data():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    ids = ["t3_1q9xv0c", "t3_1q97dvq", "t3_1q96fy4", "t3_1q8k3uh"]
    print(f"--- Data Verification for {USER_ID} ---")
    
    for pid in ids:
        cursor.execute("""
            SELECT post_id, product_id, user_id, semantic_similarity, relevance_score 
            FROM post_analysis 
            WHERE post_id = ? AND user_id = ?
        """, (pid, USER_ID))
        rows = cursor.fetchall()
        print(f"\nPOST: {pid}")
        if not rows:
            print("  NO RECORDS FOUND IN post_analysis")
        for row in rows:
            print(f"  Product: {row['product_id']} | Sim: {row['semantic_similarity']} | Score: {row['relevance_score']}")
            
    conn.close()

if __name__ == "__main__":
    verify_data()
