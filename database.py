import mysql.connector
from sqlalchemy import create_engine
import pandas as pd
import bcrypt
import datetime

# We need SQLAlchemy engine for pandas to read from MySQL efficiently
engine = create_engine("mysql+mysqlconnector://root:@localhost/lab_booking_ung")

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", # Sesuai default XAMPP
        database="lab_booking_ung"
    )

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # In MySQL, foreign keys are usually enabled by default when using InnoDB.
    # We don't need PRAGMA foreign_keys = ON;


    # 1. Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username VARCHAR(255) PRIMARY KEY,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    prodi TEXT
                )''')

    # 1.5 Lecturers Table
    c.execute('''CREATE TABLE IF NOT EXISTS lecturers (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    name TEXT NOT NULL,
                    nidn TEXT
                )''')

    # 2. Labs Table
    c.execute('''CREATE TABLE IF NOT EXISTS labs (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    capacity INTEGER
                )''')

    # 3. Bookings Table
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(255),
                    lab_id INTEGER,
                    mata_kuliah VARCHAR(255),
                    kelas VARCHAR(100),
                    dosen_id INTEGER,
                    program_studi VARCHAR(255),
                    start_date DATE,
                    end_date DATE,
                    start_time VARCHAR(50),
                    end_time VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'MENUNGGU',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users(username),
                    FOREIGN KEY (lab_id) REFERENCES labs(id),
                    FOREIGN KEY (dosen_id) REFERENCES lecturers(id)
                )''')

    conn.commit()
    conn.close()
    seed_data()

def seed_data():
    conn = get_connection()
    c = conn.cursor()

    # Check if labs exist
    c.execute("SELECT count(*) FROM labs")
    if c.fetchone()[0] == 0:
        labs = [
            ("Lab. APK & Ergonomi", 30),
            ("Lab. Simulasi & Komputasi", 25),
            ("Lab. Konversi Energi", 20),
            ("Lab. Metalurgi", 25),
            ("Lab. Manufaktur", 30),
            ("Lab. Otomotif", 20)
        ]
        c.executemany("INSERT INTO labs (name, capacity) VALUES (%s, %s)", labs)
        print("Data dummy Lab berhasil dibuat.")

    # Check if lecturers exist
    c.execute("SELECT count(*) FROM lecturers")
    if c.fetchone()[0] == 0:
        lecturers = [
            ("Prof. Dr. Ir. Eduart Wolok, S.T., M.T., IPU., ASEAN., Eng.", "-"),
            ("Dr. Ir. Trifandi Lasalewo. S.T., M.T.", "-"),
            ("Dr. Ir. Stella Junus, S.T., M.T, IPM.", "-"),
            ("Dr. Ir. Buyung R. Machmoed, S,T., M.Eng.", "-"),
            ("Ir. Rudolf Simatupang, S.T., M.T.", "-"),
            ("Ir. Silvana Mohamad, ST., M.T.", "-"),
            ("Idham Halid Lahay, S.T., M.Sc., IPM", "-"),
            ("Hasanuddin, S.T., M.Si.", "-"),
            ("Hendra Uloli, S.T., M.T.", "-"),
            ("Sunardi, S.Pd., M.Pd.", "-"),
            ("Muh. Yasser Arafat, S.Pd., M.Pd.", "-"),
            ("Jamal Darussalam Giu, S.T., M.T.", "-"),
            ("Monica Pratiwi, S.Pd.,M.Pd, T.", "-"),
            ("Esta Larosa, S.Pd., M.Pd.", "-"),
            ("Sugeng Pramudibyo, S.Pd., M.Pd.", "-"),
            ("Hafid Rahmandan, S.Pd., M.Pd.", "-"),
            ("Andi Maga Umara, S.Pd., M.Pd.", "-"),
            ("Mohamad Riyandi Badu, S.Pd, M.Pd.", "-"),
            ("Aqfi Nur Firdaus, ST.,MT.", "-")
        ]
        c.executemany("INSERT INTO lecturers (name, nidn) VALUES (%s, %s)", lecturers)
        print("Data dummy Lecturer berhasil dibuat.")

    # Check if users exist
    c.execute("SELECT count(*) FROM users")
    if c.fetchone()[0] == 0:
        # Password hashing
        pw_mhs = bcrypt.hashpw("mahasiswa123".encode(), bcrypt.gensalt()).decode()
        pw_lab = bcrypt.hashpw("laboran123".encode(), bcrypt.gensalt()).decode()
        pw_mst = bcrypt.hashpw("master123".encode(), bcrypt.gensalt()).decode()
        
        users = [
            ("mahasiswa1", pw_mhs, "Mahasiswa", "Budi Santoso", "Pendidikan Teknik Mesin"),
            ("laboran1", pw_lab, "Laboran", "Pak Asep", "Admin Lab"),
            ("master1", pw_mst, "Master", "Admin Master", "Sistem Database")
        ]
        c.executemany("INSERT INTO users (username, password, role, full_name, prodi) VALUES (%s, %s, %s, %s, %s)", users)
        print("Data dummy User berhasil dibuat.")

    conn.commit()
    conn.close()

# --- Helper Functions ---

def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT password, role, full_name, prodi FROM users WHERE username = %s", (username,))
    data = c.fetchone()
    conn.close()
    
    if data:
        stored_pw, role, full_name, prodi = data
        if bcrypt.checkpw(password.encode(), stored_pw.encode()):
            return {"username": username, "role": role, "full_name": full_name, "prodi": prodi}
    return None

def get_user(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT role, full_name, prodi FROM users WHERE username = %s", (username,))
    data = c.fetchone()
    conn.close()
    
    if data:
        role, full_name, prodi = data
        return {"username": username, "role": role, "full_name": full_name, "prodi": prodi}
    return None

def get_user_details(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT full_name, prodi FROM users WHERE username = %s", (username,))
    data = c.fetchone()
    conn.close()
    if data:
        return {"full_name": data[0], "prodi": data[1]}
    return {"full_name": username, "prodi": "-"}

def get_labs():
    df = pd.read_sql("SELECT id, name FROM labs", engine)
    return df

def get_lecturers():
    df = pd.read_sql("SELECT id, name FROM lecturers ORDER BY name", engine)
    return df

def create_booking(username, lab_id, matkul, kelas, dosen_id, prodi, start_date, end_date, time_slot):
    conn = get_connection()
    c = conn.cursor()
    
    start, end = time_slot.split(' - ')
    
    # Check conflict
    c.execute("""SELECT count(*) FROM bookings 
                 WHERE lab_id = %s 
                 AND start_date <= %s AND end_date >= %s
                 AND start_time = %s AND status != 'DITOLAK'""", 
                 (lab_id, end_date, start_date, start))
    
    if c.fetchone()[0] > 0:
        conn.close()
        return False, "Jadwal bentrok! Silakan pilih rentang waktu atau lab lain."
        
    try:
        c.execute("""INSERT INTO bookings 
                     (username, lab_id, mata_kuliah, kelas, dosen_id, program_studi, start_date, end_date, start_time, end_time) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                     (username, lab_id, matkul, kelas, dosen_id, prodi, start_date, end_date, start, end))
        conn.commit()
        conn.close()
        return True, "Peminjaman berhasil dibuat! Menunggu persetujuan Laboran."
    except Exception as e:
        conn.close()
        return False, str(e)

def get_user_bookings(username):
    conn = get_connection()
    query = """
    SELECT b.*, l.name as lab_name, d.name as dosen_pengampu 
    FROM bookings b
    LEFT JOIN labs l ON b.lab_id = l.id
    LEFT JOIN lecturers d ON b.dosen_id = d.id
    WHERE b.username = %(username)s 
    ORDER BY b.start_date DESC
    """
    df = pd.read_sql(query, engine, params={"username": username})
    return df

def get_all_bookings():
    query = """
    SELECT b.*, u.full_name, l.name as lab_name, d.name as dosen_pengampu 
    FROM bookings b
    LEFT JOIN users u ON b.username = u.username
    LEFT JOIN labs l ON b.lab_id = l.id
    LEFT JOIN lecturers d ON b.dosen_id = d.id
    ORDER BY b.start_date DESC, b.start_time ASC
    """
    df = pd.read_sql(query, engine)
    return df

def update_booking_status(booking_id, new_status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE bookings SET status = %s WHERE id = %s", (new_status, booking_id))
    conn.commit()
    conn.close()

# --- User Management Functions ---

def get_all_users(role_filter=None):
    if role_filter:
        df = pd.read_sql("SELECT username, role, full_name, prodi FROM users WHERE role = %(role_filter)s ORDER BY role, username", engine, params={"role_filter": role_filter})
    else:
        df = pd.read_sql("SELECT username, role, full_name, prodi FROM users ORDER BY role, username", engine)
    return df

def add_user(username, password, role, full_name, prodi):
    conn = get_connection()
    c = conn.cursor()
    
    # Check if username exists
    c.execute("SELECT count(*) FROM users WHERE username = %s", (username,))
    if c.fetchone()[0] > 0:
        conn.close()
        return False, "Username sudah digunakan!"
        
    try:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        c.execute("INSERT INTO users (username, password, role, full_name, prodi) VALUES (%s, %s, %s, %s, %s)",
                  (username, hashed_pw, role, full_name, prodi))
        conn.commit()
        conn.close()
        return True, "User berhasil ditambahkan!"
    except Exception as e:
        conn.close()
        return False, str(e)

def edit_user(username, password, role, full_name, prodi):
    conn = get_connection()
    c = conn.cursor()
    
    try:
        if password:
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            c.execute("UPDATE users SET password = %s, role = %s, full_name = %s, prodi = %s WHERE username = %s",
                      (hashed_pw, role, full_name, prodi, username))
        else:
            c.execute("UPDATE users SET role = %s, full_name = %s, prodi = %s WHERE username = %s",
                      (role, full_name, prodi, username))
        
        conn.commit()
        conn.close()
        return True, "Data user berhasil diperbarui!"
    except Exception as e:
        conn.close()
        return False, str(e)

def delete_user(username):
    conn = get_connection()
    c = conn.cursor()
    
    # Prevent deleting the last Laboran or Master
    c.execute("SELECT count(*) FROM users WHERE role = 'Laboran'")
    laboran_count = c.fetchone()[0]
    
    c.execute("SELECT count(*) FROM users WHERE role = 'Master'")
    master_count = c.fetchone()[0]
    
    c.execute("SELECT role FROM users WHERE username = %s", (username,))
    user_role = c.fetchone()
    
    if user_role:
        if user_role[0] == 'Laboran' and laboran_count <= 1:
            conn.close()
            return False, "Tidak bisa menghapus Laboran terakhir!"
        if user_role[0] == 'Master' and master_count <= 1:
            conn.close()
            return False, "Tidak bisa menghapus Master terakhir!"
        
    try:
        c.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        conn.close()
        return True, "User berhasil dihapus!"
    except Exception as e:
        conn.close()
        return False, str(e)
