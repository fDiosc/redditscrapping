import sqlite3

DB_PATH = "data/radar.db"

def inspect_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    ids = ["t3_1q97dvq", "t3_1q96fy4", "t3_1q8k3uh"]
    print(f"\n--- Detailed Inspection of {len(ids)} Posts ---")
    
    for pid in ids:
        print(f"\nPOST ID: {pid}")
        cursor.execute("SELECT * FROM post_analysis WHERE post_id = ?", (pid,))
        analyses = cursor.fetchall()
        for analysis in analyses:
            print(f"  Product: {analysis['product_id']} | User: {analysis['user_id']}")
            print(f"  Score: {analysis['relevance_score']} | Sim: {analysis['semantic_similarity']} | Community: {analysis['community_score']}")
            
    conn.close()

if __name__ == "__main__":
    inspect_data()
