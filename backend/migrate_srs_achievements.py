"""
Database migration script to add Vocabulary Review (SRS) and Achievements tables
"""
import sqlite3
import sys

def migrate(db_path='language_app.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Migrating database: {db_path}")

    # Create VocabularyReview table
    try:
        print("Creating vocabulary_reviews table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                word VARCHAR(200) NOT NULL,
                definition TEXT NOT NULL,
                example_sentence TEXT,
                target_language VARCHAR(50) NOT NULL,
                easiness_factor REAL DEFAULT 2.5,
                repetitions INTEGER DEFAULT 0,
                interval INTEGER DEFAULT 1,
                next_review_date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_reviewed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("✓ vocabulary_reviews table created")
    except sqlite3.OperationalError as e:
        print(f"✗ vocabulary_reviews table might already exist: {e}")

    # Create indexes for vocabulary_reviews
    try:
        print("Creating indexes for vocabulary_reviews...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_next_review
            ON vocabulary_reviews(user_id, next_review_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_word
            ON vocabulary_reviews(user_id, word)
        """)
        print("✓ Indexes created")
    except sqlite3.OperationalError as e:
        print(f"✗ Error creating indexes: {e}")

    # Create Achievement table
    try:
        print("Creating achievements table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                criteria_type VARCHAR(50) NOT NULL,
                criteria_threshold INTEGER,
                criteria_module VARCHAR(50),
                xp_reward INTEGER DEFAULT 0,
                tier VARCHAR(20) DEFAULT 'bronze',
                icon VARCHAR(10)
            )
        """)
        print("✓ achievements table created")
    except sqlite3.OperationalError as e:
        print(f"✗ achievements table might already exist: {e}")

    # Create UserAchievement table
    try:
        print("Creating user_achievements table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_id INTEGER NOT NULL,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_viewed BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (achievement_id) REFERENCES achievements(id)
            )
        """)
        print("✓ user_achievements table created")
    except sqlite3.OperationalError as e:
        print(f"✗ user_achievements table might already exist: {e}")

    # Create index for user_achievements
    try:
        print("Creating index for user_achievements...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_achievement
            ON user_achievements(user_id, achievement_id)
        """)
        print("✓ Index created")
    except sqlite3.OperationalError as e:
        print(f"✗ Error creating index: {e}")

    conn.commit()
    conn.close()
    print("\n✓ Migration completed successfully!")

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'language_app.db'
    migrate(db_path)
