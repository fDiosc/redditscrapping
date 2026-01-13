import sqlite3

DB_PATH = "data/radar.db"

def list_leads():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    with open("leads_full.txt", "w", encoding="utf-8") as f:
        f.write("\n--- Listing Top 100 SocialGenius Leads ---\n")
        cursor.execute("""
            SELECT p.id, p.title, pa.relevance_score, pa.semantic_similarity 
            FROM posts p 
            JOIN post_analysis pa ON p.id = pa.post_id 
            WHERE pa.product_id = 'socialgenius' 
            ORDER BY pa.relevance_score DESC 
            LIMIT 100
        """)
        rows = cursor.fetchall()
        for row in rows:
            f.write(f"ID: {row['id']} | Score: {row['relevance_score']:.2f} | Sim: {row['semantic_similarity']:.2f} | Title: {row['title']}\n")
            
    conn.close()

if __name__ == "__main__":
    list_leads()
