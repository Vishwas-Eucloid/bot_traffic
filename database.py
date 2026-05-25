import sqlite3
from pathlib import Path

DB_PATH = Path("storage/bot_users.db")


def create_tables():

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bot_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()



def save_user(email, password):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO bot_users (
            email,
            password
        )
        VALUES (?, ?)
        """,
        (email, password)
    )

    conn.commit()
    conn.close()



def get_random_user():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT email, password
        FROM bot_users
        ORDER BY RANDOM()
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    conn.close()

    return row