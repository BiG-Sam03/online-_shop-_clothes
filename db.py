import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict

# تعديل القيم حسب جهازك
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",          # في XAMPP/WAMP غالباً فاضية
    "database": "online_shop_clothes",
}

def connect():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    """Create database/table if not exists."""
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS online_shop_clothes CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cur.execute("USE online_shop_clothes;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
          id INT AUTO_INCREMENT PRIMARY KEY,
          name VARCHAR(120) NOT NULL,
          email VARCHAR(190) NOT NULL UNIQUE,
          password_hash VARCHAR(500) NOT NULL,
          created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_user(name: str, email: str, password_hash: str) -> None:
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (name.strip(), email.strip().lower(), password_hash)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_user_by_email(email: str) -> Optional[Dict]:
    conn = connect()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email = %s", (email.strip().lower(),))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_user_by_id(user_id: int) -> Optional[Dict]:
    conn = connect()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row
