"""
Seed achievements data into the database
"""
import sqlite3
import sys

ACHIEVEMENTS = [
    # Vocabulary Achievements
    {
        "code": "first_word",
        "name": "First Word",
        "description": "Complete your first vocabulary flashcard",
        "criteria_type": "count",
        "criteria_threshold": 1,
        "criteria_module": "vocabulary",
        "xp_reward": 10,
        "tier": "bronze",
        "icon": "📚"
    },
    {
        "code": "word_explorer",
        "name": "Word Explorer",
        "description": "Complete 10 vocabulary flashcards",
        "criteria_type": "count",
        "criteria_threshold": 10,
        "criteria_module": "vocabulary",
        "xp_reward": 50,
        "tier": "bronze",
        "icon": "🔍"
    },
    {
        "code": "vocabulary_master",
        "name": "Vocabulary Master",
        "description": "Complete 100 vocabulary flashcards",
        "criteria_type": "count",
        "criteria_threshold": 100,
        "criteria_module": "vocabulary",
        "xp_reward": 200,
        "tier": "gold",
        "icon": "🏆"
    },

    # Grammar Achievements
    {
        "code": "grammar_guru",
        "name": "Grammar Guru",
        "description": "Score 90% or higher on 5 grammar questions",
        "criteria_type": "score",
        "criteria_threshold": 90,
        "criteria_module": "grammar",
        "xp_reward": 100,
        "tier": "silver",
        "icon": "📖"
    },
    {
        "code": "grammar_perfectionist",
        "name": "Grammar Perfectionist",
        "description": "Get 10 grammar questions correct in a row",
        "criteria_type": "count",
        "criteria_threshold": 10,
        "criteria_module": "grammar",
        "xp_reward": 150,
        "tier": "gold",
        "icon": "✨"
    },

    # Writing Achievements
    {
        "code": "first_composition",
        "name": "First Composition",
        "description": "Submit your first writing piece",
        "criteria_type": "count",
        "criteria_threshold": 1,
        "criteria_module": "writing",
        "xp_reward": 25,
        "tier": "bronze",
        "icon": "✍️"
    },
    {
        "code": "prolific_writer",
        "name": "Prolific Writer",
        "description": "Submit 20 writing pieces",
        "criteria_type": "count",
        "criteria_threshold": 20,
        "criteria_module": "writing",
        "xp_reward": 150,
        "tier": "silver",
        "icon": "📝"
    },

    # Conversation Achievements
    {
        "code": "conversationalist",
        "name": "Conversationalist",
        "description": "Send 50 messages in conversation practice",
        "criteria_type": "count",
        "criteria_threshold": 50,
        "criteria_module": "conversation",
        "xp_reward": 100,
        "tier": "silver",
        "icon": "💬"
    },

    # Phonetics Achievements
    {
        "code": "pronunciation_pro",
        "name": "Pronunciation Pro",
        "description": "Complete 10 pronunciation practices",
        "criteria_type": "count",
        "criteria_threshold": 10,
        "criteria_module": "phonetics",
        "xp_reward": 75,
        "tier": "bronze",
        "icon": "🎤"
    },

    # Level Achievements
    {
        "code": "level_up",
        "name": "Level Up!",
        "description": "Advance to a new CEFR level",
        "criteria_type": "level_advance",
        "criteria_threshold": 1,
        "criteria_module": None,
        "xp_reward": 300,
        "tier": "gold",
        "icon": "⬆️"
    },
    {
        "code": "rapid_learner",
        "name": "Rapid Learner",
        "description": "Advance 2 CEFR levels",
        "criteria_type": "level_advance",
        "criteria_threshold": 2,
        "criteria_module": None,
        "xp_reward": 500,
        "tier": "platinum",
        "icon": "🚀"
    },

    # XP Achievements
    {
        "code": "xp_collector",
        "name": "XP Collector",
        "description": "Earn 1000 total XP",
        "criteria_type": "total_xp",
        "criteria_threshold": 1000,
        "criteria_module": None,
        "xp_reward": 100,
        "tier": "silver",
        "icon": "💎"
    },
    {
        "code": "xp_champion",
        "name": "XP Champion",
        "description": "Earn 5000 total XP",
        "criteria_type": "total_xp",
        "criteria_threshold": 5000,
        "criteria_module": None,
        "xp_reward": 500,
        "tier": "platinum",
        "icon": "👑"
    },

    # Dedication Achievements
    {
        "code": "dedicated_learner",
        "name": "Dedicated Learner",
        "description": "Complete 100 activities across all modules",
        "criteria_type": "count",
        "criteria_threshold": 100,
        "criteria_module": "all",
        "xp_reward": 250,
        "tier": "gold",
        "icon": "🌟"
    }
]


def seed_achievements(db_path='language_app.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Seeding achievements into: {db_path}")

    for achievement in ACHIEVEMENTS:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO achievements
                (code, name, description, criteria_type, criteria_threshold, criteria_module, xp_reward, tier, icon)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                achievement["code"],
                achievement["name"],
                achievement["description"],
                achievement["criteria_type"],
                achievement["criteria_threshold"],
                achievement["criteria_module"],
                achievement["xp_reward"],
                achievement["tier"],
                achievement["icon"]
            ))
            print(f"✓ Added: {achievement['name']}")
        except sqlite3.IntegrityError as e:
            print(f"✗ Skipped (already exists): {achievement['name']}")

    conn.commit()

    # Count total achievements
    cursor.execute("SELECT COUNT(*) FROM achievements")
    count = cursor.fetchone()[0]
    print(f"\nTotal achievements in database: {count}")

    conn.close()
    print("✓ Seeding completed!")


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'language_app.db'
    seed_achievements(db_path)
