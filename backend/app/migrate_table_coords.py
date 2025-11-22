from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        # Check if columns exist
        result = connection.execute(text("PRAGMA table_info(tables)"))
        columns = [row[1] for row in result]
        
        new_columns = {
            'x': 'INTEGER DEFAULT 0',
            'y': 'INTEGER DEFAULT 0',
            'width': 'INTEGER DEFAULT 100',
            'height': 'INTEGER DEFAULT 100',
            'shape': 'VARCHAR DEFAULT "rectangle"',
            'rotation': 'INTEGER DEFAULT 0'
        }

        for col_name, col_def in new_columns.items():
            if col_name not in columns:
                print(f"Adding {col_name} column to tables table...")
                connection.execute(text(f"ALTER TABLE tables ADD COLUMN {col_name} {col_def}"))
                print(f"Column {col_name} added successfully.")
            else:
                print(f"Column {col_name} already exists.")

if __name__ == "__main__":
    migrate()
