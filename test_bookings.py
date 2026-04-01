import database as db

try:
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(255),
                    lab_id INTEGER,
                    mata_kuliah TEXT,
                    kelas TEXT,
                    dosen_id INTEGER,
                    program_studi TEXT,
                    start_date DATE,
                    end_date DATE,
                    start_time TEXT,
                    end_time TEXT,
                    status TEXT DEFAULT 'MENUNGGU',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users(username),
                    FOREIGN KEY (lab_id) REFERENCES labs(id),
                    FOREIGN KEY (dosen_id) REFERENCES lecturers(id)
                )""")
    conn.commit()
    conn.close()
    print("Berhasil membuat tabel bookings!")
except Exception as e:
    print("Error:", e)
