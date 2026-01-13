import sqlite3

DB_PATH = "data/radar.db"

def list_top_socialgenius_leads():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n--- Top 10 SocialGenius Leads ---")
    cursor.execute("""
        SELECT p.id, p.title, pa.relevance_score, pa.semantic_similarity 
        FROM posts p 
        JOIN post_analysis pa ON p.id = pa.post_id 
        WHERE pa.product_id = 'socialgenius' 
        ORDER BY pa.relevance_score DESC 
        LIMIT 10
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row['id']} | Score: {row['relevance_score']:.2f} | Sim: {row['semantic_similarity']:.2f} | Title: {row['title'][:100]}")
            
    conn.close()

if __name__ == "__main__":
    list_top_socialgenius_leads()
