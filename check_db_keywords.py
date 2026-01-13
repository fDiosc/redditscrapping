import sqlite3
import json

DB_PATH = "data/radar.db"

def check_db_keywords():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, user_id, pain_signals, intent_signals FROM products WHERE id = 'socialgenius'")
    rows = cursor.fetchall()
    print(f"\n--- Database Keywords for SocialGenius ---")
    for row in rows:
        print(f"Product: {row['id']} | User: {row['user_id']}")
        pain = json.loads(row['pain_signals'])
        intent = json.loads(row['intent_signals'])
        print(f"  Pain Keywords ({len(pain)}): {pain}")
        print(f"  Intent Keywords ({len(intent)}): {intent}")
            
    conn.close()

if __name__ == "__main__":
    check_db_keywords()
