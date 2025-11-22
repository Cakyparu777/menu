import sqlite3
from app.core.config import settings

DB_PATH = "./sql_app.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Creating employee_requests table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            restaurant_id INTEGER NOT NULL,
            type VARCHAR NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            status VARCHAR DEFAULT 'pending',
            note VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES users (id),
            FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
        )
        """)
        
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_employee_requests_id ON employee_requests (id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_employee_requests_employee_id ON employee_requests (employee_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_employee_requests_restaurant_id ON employee_requests (restaurant_id)")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
