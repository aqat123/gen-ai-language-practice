"""
Database migration script to add progress tracking and level advancement features.

This script:
1. Adds new columns to the users table (level_started_at, can_advance, advancement_notified_at, total_xp)
2. Creates the level_history table
3. Sets level_started_at for existing users based on their earliest activity
"""

import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "test_language_app.db")

def migrate():
    print("Starting progress tracking migration...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Add new columns to users table
        print("\n1. Adding new columns to users table...")

        new_columns = [
            ("level_started_at", "DATETIME"),
            ("can_advance", "BOOLEAN DEFAULT 0"),
            ("advancement_notified_at", "DATETIME"),
            ("total_xp", "INTEGER DEFAULT 0")
        ]

        for column_name, column_type in new_columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                print(f"   ✓ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"   - Column {column_name} already exists, skipping")
                else:
                    raise

        # 2. Create level_history table
        print("\n2. Creating level_history table...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                level TEXT NOT NULL,

                vocabulary_score REAL,
                grammar_score REAL,
                writing_score REAL,
                phonetics_score REAL,
                conversation_messages INTEGER DEFAULT 0,

                vocabulary_attempts INTEGER DEFAULT 0,
                grammar_attempts INTEGER DEFAULT 0,
                writing_attempts INTEGER DEFAULT 0,
                phonetics_attempts INTEGER DEFAULT 0,

                started_at DATETIME NOT NULL,
                completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                days_at_level INTEGER,

                weighted_score REAL NOT NULL,

                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("   ✓ Created level_history table")

        # 3. Set level_started_at for existing users
        print("\n3. Setting level_started_at for existing users...")

        # Get all users
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()

        for (user_id,) in users:
            # Find earliest activity from user_progress
            cursor.execute("""
                SELECT MIN(last_activity_at)
                FROM user_progress
                WHERE user_id = ?
            """, (user_id,))

            result = cursor.fetchone()
            earliest_activity = result[0] if result and result[0] else None

            if earliest_activity:
                cursor.execute("""
                    UPDATE users
                    SET level_started_at = ?
                    WHERE id = ? AND level_started_at IS NULL
                """, (earliest_activity, user_id))
                print(f"   ✓ Set level_started_at for user {user_id[:8]}...")
            else:
                # If no activity, set to created_at
                cursor.execute("""
                    UPDATE users
                    SET level_started_at = created_at
                    WHERE id = ? AND level_started_at IS NULL
                """, (user_id,))
                print(f"   ✓ Set level_started_at to created_at for user {user_id[:8]}...")

        conn.commit()
        print("\n✓ Migration completed successfully!")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
