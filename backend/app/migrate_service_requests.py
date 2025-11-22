"""
Database migration script to add service_requests table
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base
from app.models import ServiceRequest

def migrate():
    """Add service_requests table"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    print("Creating service_requests table...")
    
    # Create the table using SQLAlchemy ORM
    Base.metadata.tables['service_requests'].create(engine, checkfirst=True)
    
    print("✅ Migration completed successfully!")
    print("   - service_requests table created")

if __name__ == "__main__":
    migrate()
