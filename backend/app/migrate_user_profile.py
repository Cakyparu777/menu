"""
Simple migration script to add new columns to the users table.
Run this script to update the existing database with new profile fields.
"""
import sqlite3
import os
from datetime import datetime

# Path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'sql_app.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'avatar_url' not in columns:
            print("Adding avatar_url column...")
            cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
        
        if 'dietary_preferences' not in columns:
            print("Adding dietary_preferences column...")
            cursor.execute("ALTER TABLE users ADD COLUMN dietary_preferences TEXT DEFAULT '[]'")
        
        if 'notification_enabled' not in columns:
            print("Adding notification_enabled column...")
            cursor.execute("ALTER TABLE users ADD COLUMN notification_enabled INTEGER DEFAULT 1")
        
        if 'preferred_language' not in columns:
            print("Adding preferred_language column...")
            cursor.execute("ALTER TABLE users ADD COLUMN preferred_language TEXT DEFAULT 'en'")
        
        if 'created_at' not in columns:
            print("Adding created_at column...")
            # SQLite doesn't support CURRENT_TIMESTAMP in ALTER TABLE, so we add it without default
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
            # Update existing rows with current timestamp
            cursor.execute("UPDATE users SET created_at = ? WHERE created_at IS NULL", (datetime.now().isoformat(),))
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
