import sqlite3
import json

DB_PATH = "data/radar.db"

def inspect_signals():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    ids = ["t3_1q97dvq", "t3_1q96fy4", "t3_1q8k3uh"]
    print(f"\n--- Signal Inspection for {len(ids)} Posts ---")
    
    for pid in ids:
        print(f"\nPOST ID: {pid}")
        cursor.execute("SELECT signals_json, relevance_score, semantic_similarity FROM post_analysis WHERE post_id = ? AND product_id = 'socialgenius' LIMIT 1", (pid,))
        row = cursor.fetchone()
        if row:
            signals = json.loads(row['signals_json'])
            print(f"  Score: {row['relevance_score']} | Sim: {row['semantic_similarity']}")
            print(f"  Detected Signals: {json.dumps(signals, indent=4)}")
            
    conn.close()

if __name__ == "__main__":
    inspect_signals()
