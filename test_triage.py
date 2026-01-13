from radar.storage.db import update_triage_status, get_connection
import sqlite3

def test_vibe():
    user_id = "user_2rhX9iR7I1j9f4N7oR5y7Q5u8kL" # Dummy or real user ID
    product_id = "socialgenius"
    post_id = "t3_1q9xv0c" # The one from the error logs
    
    print(f"Testing triage update for {post_id}...")
    try:
        # First ensure the row exists in post_analysis
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO post_analysis (post_id, product_id, user_id) VALUES (?, ?, ?)", (post_id, product_id, user_id))
        conn.commit()
        conn.close()
        
        update_triage_status(user_id, product_id, post_id, "agree")
        print("SUCCESS: update_triage_status executed without error.")
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vibe()
