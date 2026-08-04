import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'jony_data.db'))

def init_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  command TEXT,
                  timestamp TEXT)''')

    conn.commit()
    conn.close()


def save_command(command):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    timestamp = datetime.now().strftime("%H:%M:%S")
    c.execute("INSERT INTO history (command, timestamp) VALUES (?, ?)", (command, timestamp))

    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT command, timestamp FROM history ORDER BY id DESC LIMIT 30")
    data = c.fetchall()

    conn.close()
    return data