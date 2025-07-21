import sqlite3
import pandas as pd

DB_NAME = "receipts.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            vendor TEXT,
            date TEXT,
            amount REAL,
            currency TEXT,
            category TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_receipt(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO receipts (filename, vendor, date, amount, currency, category)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data["filename"], data["vendor"], data["date"], data["amount"], data["currency"], data["category"]))
    conn.commit()
    conn.close()

def fetch_all_receipts():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM receipts", conn)
    conn.close()
    return df

def get_top_vendors():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT vendor, COUNT(*) as freq FROM receipts
        GROUP BY vendor ORDER BY freq DESC
    """)
    result = cursor.fetchall()
    conn.close()
    return [r[0] for r in result]
