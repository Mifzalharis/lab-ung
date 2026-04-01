import sqlite3
import database as db

def migrate():
    conn = db.get_connection()
    c = conn.cursor()
    
    try:
        print("Attempting to rename 'booking_date' to 'start_date'...")
        c.execute("ALTER TABLE bookings RENAME COLUMN booking_date TO start_date")
        print("Column renamed successfully.")
    except sqlite3.OperationalError as e:
        print(f"Rename Error (maybe already renamed?): {e}")

    try:
        print("Attempting to add 'end_date' column...")
        c.execute("ALTER TABLE bookings ADD COLUMN end_date DATE")
        print("Column added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Add Error (maybe already exists?): {e}")

    try:
        print("Updating existing records to set end_date = start_date where end_date is null...")
        c.execute("UPDATE bookings SET end_date = start_date WHERE end_date IS NULL")
        print("Update successful.")
    except Exception as e:
        print(f"Update Error: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
