import sqlite3
import database as db
import bcrypt

def migrate():
    conn = db.get_connection()
    c = conn.cursor()
    
    # Check if a Master user already exists
    c.execute("SELECT count(*) FROM users WHERE role = 'Master'")
    master_count = c.fetchone()[0]
    
    if master_count == 0:
        print("Inserting default Master user...")
        pw_mst = bcrypt.hashpw("master1".encode(), bcrypt.gensalt()).decode()
        c.execute("INSERT INTO users (username, password, role, full_name, prodi) VALUES (?, ?, ?, ?, ?)",
                  ("master1", pw_mst, "Master", "Administrator Master", "Sistem Database"))
        conn.commit()
        print("Master user 'master1' created with password 'master1'.")
    else:
        print("Master user already exists.")
        
    conn.close()

if __name__ == "__main__":
    migrate()
