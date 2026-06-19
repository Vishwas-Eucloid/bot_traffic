import sqlite3
from pathlib import Path

DB_PATH = Path("storage/bot_users.db")

def get_connection():
    """Helper function to cleanly open a connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    # SQLite prefers paths as strings
    return sqlite3.connect(str(DB_PATH))

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
    except Exception as e:
        print(f"  -> [Database Error] Could not create tables: {e}")
    finally:
        # The 'finally' block GUARANTEES the connection closes, even on a crash
        conn.close()

def save_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Swapped back to standard INSERT so we can catch the exact error
        cursor.execute(
            """
            INSERT INTO bot_users (email, password) 
            VALUES (?, ?)
            """,
            (email, password)
        )
        conn.commit()
        print(f"  -> [Database] Successfully saved {email} to vault.")
    except sqlite3.IntegrityError:
        # Now you will actually know if a duplicate email was generated!
        print(f"  -> [Database Warning] {email} already exists. Skipping duplicate.")
    except Exception as e:
        print(f"  -> [Database Error] Could not save user: {e}")
    finally:
        conn.close()

def get_random_user():
    conn = get_connection()
    cursor = conn.cursor()
    row = None
    try:
        cursor.execute(
            """
            SELECT email, password
            FROM bot_users
            ORDER BY RANDOM()
            LIMIT 1
            """
        )
        row = cursor.fetchone()
    except Exception as e:
        print(f"  -> [Database Error] Could not fetch user: {e}")
    finally:
        conn.close()
    
    return row
