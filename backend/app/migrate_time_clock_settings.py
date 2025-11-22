"""
Database migration script to add enable_time_clock to restaurants
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base

def migrate():
    """Add enable_time_clock column to restaurants table"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    print("Adding enable_time_clock column to restaurants table...")
    
    with engine.connect() as conn:
        # Check if column exists first (SQLite doesn't support IF NOT EXISTS for columns easily in all versions, 
        # but we can try/except or just run it)
        try:
            conn.execute(text("ALTER TABLE restaurants ADD COLUMN enable_time_clock BOOLEAN DEFAULT 1"))
            print("✅ Added enable_time_clock column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ Column enable_time_clock already exists")
            else:
                print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    migrate()
