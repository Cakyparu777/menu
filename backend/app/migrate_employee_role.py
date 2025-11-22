"""
Migration script to add employee-related columns to the users table.
"""
import sqlite3
import os

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
        if 'restaurant_id' not in columns:
            print("Adding restaurant_id column...")
            cursor.execute("ALTER TABLE users ADD COLUMN restaurant_id INTEGER REFERENCES restaurants(id)")
        
        if 'force_password_change' not in columns:
            print("Adding force_password_change column...")
            cursor.execute("ALTER TABLE users ADD COLUMN force_password_change INTEGER DEFAULT 0")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
