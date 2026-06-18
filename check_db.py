import sqlite3
from pathlib import Path

def view_database():
    # Dynamically locate the storage folder relative to this script
    base_dir = Path(__file__).parent.absolute()
    db_path = base_dir / "storage" / "bot_users.db"
    
    if not db_path.exists():
        print(f"\n❌ The file '{db_path}' does not exist yet.")
        print("Run your test_sqlite_flow.py script first to generate it!")
        return

    print("\n--- 🗄️ CURRENT DATABASE CONTENTS ---")
    try:
        # SQLite needs the path as a string
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bot_users'")
        if not cursor.fetchone():
            print("The 'bot_users' table has not been created yet.")
            return

        # Fetch all users
        cursor.execute("SELECT id, email, password FROM bot_users")
        rows = cursor.fetchall()
        
        if not rows:
            print("The database is currently empty (0 users).")
        else:
            print(f"Total Users Found: {len(rows)}\n")
            for row in rows:
                print(f"ID: {row[0]} | Email: {row[1]} | Password: {row[2]}")
                
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    print("------------------------------------\n")

if __name__ == "__main__":
    view_database()