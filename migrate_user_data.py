"""
Migration script to assign existing data to a default user.
Run this once after updating the schema to add user_id columns.
"""
import sqlite3
from radar.config import DATABASE_PATH

# Felipe Fernandes' Clerk user ID (from Clerk dashboard)
# This is the user who will own all existing data
DEFAULT_USER_ID = "user_2abc123"  # TODO: Replace with actual Clerk user ID

def migrate_data_to_user(user_id: str):
    """Migrate all existing data to a specific user."""
    print(f"Starting migration to user: {user_id}")
    
    conn = sqlite3.connect(DATABASE_PATH, timeout=30)
    cursor = conn.cursor()
    
    # First, run init_db to ensure all columns exist
    from radar.storage.db import init_db
    init_db()
    
    # 1. Update products table
    cursor.execute("UPDATE products SET user_id = ? WHERE user_id IS NULL", (user_id,))
    products_updated = cursor.rowcount
    print(f"Updated {products_updated} products")
    
    # 2. Update post_analysis table
    cursor.execute("UPDATE post_analysis SET user_id = ? WHERE user_id IS NULL", (user_id,))
    analysis_updated = cursor.rowcount
    print(f"Updated {analysis_updated} post analyses")
    
    # 3. Update generated_responses table
    cursor.execute("UPDATE generated_responses SET user_id = ? WHERE user_id IS NULL", (user_id,))
    responses_updated = cursor.rowcount
    print(f"Updated {responses_updated} generated responses")
    
    # 4. Update sync_runs table
    cursor.execute("UPDATE sync_runs SET user_id = ? WHERE user_id IS NULL", (user_id,))
    syncs_updated = cursor.rowcount
    print(f"Updated {syncs_updated} sync runs")
    
    conn.commit()
    conn.close()
    
    print(f"\nMigration complete!")
    print(f"Total records updated:")
    print(f"  Products: {products_updated}")
    print(f"  Post Analyses: {analysis_updated}")
    print(f"  Generated Responses: {responses_updated}")
    print(f"  Sync Runs: {syncs_updated}")

def get_clerk_user_id_from_email(email: str):
    """
    Placeholder: In production, you would call Clerk API to get user ID by email.
    For now, you need to get this from Clerk dashboard manually.
    """
    print(f"TODO: Get Clerk user ID for {email} from your Clerk dashboard")
    print("Go to: https://dashboard.clerk.com -> Users -> Click on user -> Copy user ID")
    return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrate_user_data.py <clerk_user_id>")
        print("\nTo get the Clerk user ID:")
        print("1. Go to https://dashboard.clerk.com")
        print("2. Click on 'Users' tab")
        print("3. Click on the user (e.g., Felipe Fernandes)")
        print("4. Copy the 'User ID' (starts with 'user_')")
        print("\nExample: python migrate_user_data.py user_2abc123xyz")
        sys.exit(1)
    
    user_id = sys.argv[1]
    
    if not user_id.startswith("user_"):
        print("Warning: Clerk user IDs typically start with 'user_'")
        confirm = input("Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            sys.exit(1)
    
    migrate_data_to_user(user_id)
