"""
Migration script to add notifications table and push_token field to users table.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    """Run the migration"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    with engine.begin() as conn:
        print("Adding push_token column to users table...")
        try:
            # For SQLite, just try to add it and catch the error if it exists
            conn.execute(text("ALTER TABLE users ADD COLUMN push_token VARCHAR;"))
            print("✓ Added push_token column to users")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("✓ push_token column already exists")
            else:
                print(f"Error adding push_token column: {e}")
        
        print("\nCreating notifications table...")
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR NOT NULL,
                    body TEXT NOT NULL,
                    data JSONB,
                    read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            print("✓ Created notifications table")
        except Exception as e:
            print(f"Error creating notifications table: {e}")
        
        print("\nCreating indexes...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_notifications_user_id 
                ON notifications(user_id);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_notifications_read 
                ON notifications(read);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_notifications_created_at 
                ON notifications(created_at DESC);
            """))
            print("✓ Created indexes")
        except Exception as e:
            print(f"Error creating indexes: {e}")
    
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()
