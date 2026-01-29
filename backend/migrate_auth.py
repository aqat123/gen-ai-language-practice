"""
Database migration script to add authentication fields
"""
import sqlite3

def migrate():
    conn = sqlite3.connect('test_language_app.db')
    cursor = conn.cursor()
    
    try:
        # Add new columns to users table
        print("Adding username column...")
        cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
        cursor.execute("CREATE UNIQUE INDEX idx_users_username ON users(username)")
    except sqlite3.OperationalError as e:
        print(f"username column might already exist: {e}")
    
    try:
        print("Adding hashed_password column...")
        cursor.execute("ALTER TABLE users ADD COLUMN hashed_password TEXT")
    except sqlite3.OperationalError as e:
        print(f"hashed_password column might already exist: {e}")
    
    try:
        print("Adding full_name column...")
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    except sqlite3.OperationalError as e:
        print(f"full_name column might already exist: {e}")
    
    try:
        print("Adding is_active column...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
    except sqlite3.OperationalError as e:
        print(f"is_active column might already exist: {e}")
    
    try:
        print("Adding placement_test_completed column...")
        cursor.execute("ALTER TABLE users ADD COLUMN placement_test_completed BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError as e:
        print(f"placement_test_completed column might already exist: {e}")
    
    try:
        print("Adding placement_test_score column...")
        cursor.execute("ALTER TABLE users ADD COLUMN placement_test_score REAL")
    except sqlite3.OperationalError as e:
        print(f"placement_test_score column might already exist: {e}")
    
    try:
        print("Making external_id nullable...")
        # SQLite doesn't support ALTER COLUMN, so we note it
        print("Note: external_id is now nullable in the model, but existing constraint remains")
    except Exception as e:
        print(f"Note: {e}")
    
    # Create placement_tests table
    try:
        print("Creating placement_tests table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS placement_tests (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                target_language TEXT NOT NULL,
                test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed BOOLEAN DEFAULT 0,
                questions_data TEXT NOT NULL,
                answers_data TEXT NOT NULL,
                vocabulary_score REAL,
                grammar_score REAL,
                reading_score REAL,
                overall_score REAL,
                determined_level TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
    except sqlite3.OperationalError as e:
        print(f"placement_tests table might already exist: {e}")
    
    conn.commit()
    print("\nMigration completed successfully!")
    conn.close()

if __name__ == "__main__":
    migrate()
