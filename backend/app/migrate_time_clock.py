"""
Database migration script to add time_entries table
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base
from app.models import TimeEntry

def migrate():
    """Add time_entries table"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    print("Creating time_entries table...")
    
    # Create the table using SQLAlchemy ORM
    Base.metadata.tables['time_entries'].create(engine, checkfirst=True)
    
    print("✅ Migration completed successfully!")
    print("   - time_entries table created")

if __name__ == "__main__":
    migrate()
