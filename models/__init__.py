import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'healthcare.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cur  = conn.cursor()

    cur.executescript('''
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            specialty  TEXT NOT NULL,
            available  INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS patients (
            patient_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT NOT NULL,
            age              INTEGER NOT NULL,
            gender           TEXT NOT NULL,
            contact          TEXT NOT NULL,
            email            TEXT UNIQUE NOT NULL,
            password         TEXT NOT NULL,
            previous_noshows INTEGER DEFAULT 0,
            distance_km      REAL DEFAULT 5.0,
            created_at       TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS time_slots (
            slot_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id    INTEGER NOT NULL,
            slot_date    TEXT NOT NULL,
            start_time   TEXT NOT NULL,
            end_time     TEXT NOT NULL,
            is_available INTEGER DEFAULT 1,
            can_overbook INTEGER DEFAULT 0,
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        );

        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id       INTEGER NOT NULL,
            doctor_id        INTEGER NOT NULL,
            slot_id          INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            status           TEXT DEFAULT 'scheduled',
            no_show_prob     REAL DEFAULT 0.0,
            urgency_level    INTEGER DEFAULT 1,
            priority_score   REAL DEFAULT 0.0,
            created_at       TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id),
            FOREIGN KEY (slot_id)    REFERENCES time_slots(slot_id)
        );
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")
