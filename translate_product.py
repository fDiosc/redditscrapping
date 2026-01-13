import sqlite3
import json

DB_PATH = "data/radar.db"

def translate_socialgenius():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # New Specific English Keywords
    pain_en = [
        "social media burnout", "creating content takes forever", 
        "don't know what to post", "content ideas", "post calendar", 
        "low engagement", "instagram posts", "tiktok videos", 
        "reels content", "posting schedule", "captions", "hashtags", 
        "ig growth", "manage instagram", "manage tiktok"
    ]
    
    intent_en = [
        "scheduling tools", "automate instagram posts", 
        "social media planning", "post idea generator", 
        "how to grow on tiktok", "best tool for reels", 
        "social media planner", "creator productivity tool",
        "hire someone to run my", "looking for post tool",
        "automate my posts", "social media automation"
    ]
    
    cursor.execute("""
        UPDATE products 
        SET pain_signals = ?, intent_signals = ? 
        WHERE id = 'socialgenius'
    """, (json.dumps(pain_en), json.dumps(intent_en)))
    
    conn.commit()
    print(f"SocialGenius keywords translated to English for {cursor.rowcount} records.")
    conn.close()

if __name__ == "__main__":
    translate_socialgenius()
