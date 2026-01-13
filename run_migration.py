"""
Database Migration: Add user_id columns for multi-tenancy
Run this once to update the existing database schema.
"""
import sqlite3
import os

# Use the correct database path
DB_PATH = "data/radar.db"

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        return
    
    print(f"Migrating database: {os.path.abspath(DB_PATH)}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    migrations = [
        # Add user_id to products table
        ("products", "user_id", "ALTER TABLE products ADD COLUMN user_id TEXT DEFAULT 'default_user'"),
        
        # Add user_id to sync_runs table
        ("sync_runs", "user_id", "ALTER TABLE sync_runs ADD COLUMN user_id TEXT DEFAULT 'default_user'"),
        
        # Add user_id to post_analysis table
        ("post_analysis", "user_id", "ALTER TABLE post_analysis ADD COLUMN user_id TEXT DEFAULT 'default_user'"),
        
        # Add user_id to generated_responses table
        ("generated_responses", "user_id", "ALTER TABLE generated_responses ADD COLUMN user_id TEXT DEFAULT 'default_user'"),
    ]
    
    for table, column, sql in migrations:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            print(f"  ⚠ Table {table} does not exist, skipping")
            continue
            
        # Check if column exists
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        if column in columns:
            print(f"  ✓ {table}.{column} already exists")
        else:
            try:
                cursor.execute(sql)
                print(f"  ✓ Added {table}.{column}")
            except Exception as e:
                print(f"  ✗ Error adding {table}.{column}: {e}")
    
    # Create user_settings table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            PRIMARY KEY (user_id, key)
        )
    """)
    print("  ✓ user_settings table ready")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migration complete! Restart 'radar serve' now.")

if __name__ == "__main__":
    run_migration()
