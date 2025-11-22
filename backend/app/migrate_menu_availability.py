from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        # Check if column exists
        result = connection.execute(text("PRAGMA table_info(menu_items)"))
        columns = [row[1] for row in result]
        
        if 'is_available' not in columns:
            print("Adding is_available column to menu_items table...")
            connection.execute(text("ALTER TABLE menu_items ADD COLUMN is_available BOOLEAN DEFAULT 1"))
            print("Column added successfully.")
        else:
            print("Column is_available already exists.")

if __name__ == "__main__":
    migrate()
