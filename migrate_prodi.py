import sqlite3
import database as db

def migrate():
    conn = db.get_connection()
    c = conn.cursor()
    
    try:
        print("Attempting to add 'program_studi' column to bookings table...")
        c.execute("ALTER TABLE bookings ADD COLUMN program_studi TEXT")
        print("Column added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'program_studi' already exists.")
        else:
            print(f"Error: {e}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
