# config.py

import mysql.connector

def get_connection():
    try:
        conn =  mysql.connector.connect(
        host="localhost",
        user="root",       # 🔁 Replace with your MySQL username
        password="server",   # 🔁 Replace with your password
        database="event_calendar",
        charset="utf8mb4"
        )
        print("✅ DB connection successful")
        return conn
    except Exception as e:
        print("❌ DB connection failed:", e)
        return None

"""
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="server",
        database="event_calendar",
        charset="utf8mb4"
    )
"""