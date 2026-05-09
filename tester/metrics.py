import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "metrics.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT,
            latency REAL,
            status TEXT,
            retries INTEGER,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_metric(endpoint, latency, status, retries):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO metrics(endpoint, latency, status, retries, timestamp) VALUES (?, ?, ?, ?, ?)",
        (endpoint, latency, status, retries, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()