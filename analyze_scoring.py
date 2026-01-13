import sqlite3
import json

DB_PATH = "data/radar.db"

def analyze_scoring():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    titles = [
        "What makes a marketer more hireable - industry specialization or technical skills?",
        "Want to hire someone to run my IG/TIKTOK"
    ]
    
    print("--- SCORING CALIBRATION AUDIT ---")
    for title in titles:
        cursor.execute("""
            SELECT p.id, p.title, p.body, pa.relevance_score, pa.semantic_similarity, pa.community_score, pa.signals_json, pa.ai_analysis, pa.product_id
            FROM posts p
            JOIN post_analysis pa ON p.id = pa.post_id
            WHERE p.title = ?
        """, (title,))
        
        rows = cursor.fetchall()
        if not rows:
            print(f"\n[NOT FOUND] {title}")
            continue
            
        for row in rows:
            print(f"\n{'='*60}")
            print(f"[POST] {row['title']}")
            print(f"Product ID: {row['product_id']}")
            print(f"Total Score: {row['relevance_score']:.2f}")
            print(f"Fit (Similarity): {row['semantic_similarity'] * 100:.1f}%")
            print(f"Intensity (Community): {row['community_score']:.2f}")
            print(f"Signals Detected: {row['signals_json']}")
            print("-" * 30)
            print(f"BODY SNIPPET:\n{row['body'][:1000]}")
            print('='*60)

    conn.close()

if __name__ == "__main__":
    analyze_scoring()
