from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from uuid import uuid4
from app.db.database import Base

"""Modified to work on SQLite which does not support UUID type natively.
If you are on pgsql, remove the getter and use UUID type directly."""

# Helper to ensure we always get a string
def get_uuid_str():
    return str(uuid4())

class User(Base):
    """User model for storing user information."""
    __tablename__ = "users"

    # CHANGE: explicitly use String type
    id = Column(String, primary_key=True, default=get_uuid_str)
    external_id = Column(String, unique=True, index=True, nullable=True)  # Made nullable for backward compatibility

    # Authentication fields
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # Placement test fields
    placement_test_completed = Column(Boolean, default=False)
    placement_test_score = Column(Float, nullable=True)

    # Language learning fields
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    target_language = Column(String, nullable=True)
    level = Column(String, nullable=True)

    # Progress tracking fields
    level_started_at = Column(DateTime, nullable=True)
    can_advance = Column(Boolean, default=False)
    advancement_notified_at = Column(DateTime, nullable=True)
    total_xp = Column(Integer, default=0)


class UserProgress(Base):
    """Track per-module learning progress for users."""
    __tablename__ = "user_progress"

    id = Column(String, primary_key=True, default=get_uuid_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    module = Column(String, nullable=False)
    score = Column(Float, nullable=True)
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    last_activity_at = Column(DateTime, server_default=func.now())


class ConversationSession(Base):
    """Store conversation session data and chat history."""
    __tablename__ = "conversation_sessions"

    id = Column(String, primary_key=True, default=get_uuid_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    context_json = Column(JSON, nullable=False, default=dict)
    target_language = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)


class PlacementTest(Base):
    """Store placement test data and results."""
    __tablename__ = "placement_tests"

    id = Column(String, primary_key=True, default=get_uuid_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    target_language = Column(String, nullable=False)
    test_date = Column(DateTime, server_default=func.now())
    completed = Column(Boolean, default=False)

    # Test content and answers
    questions_data = Column(JSON, nullable=False, default=dict)
    answers_data = Column(JSON, nullable=False, default=dict)

    # Scores
    vocabulary_score = Column(Float, nullable=True)
    grammar_score = Column(Float, nullable=True)
    reading_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)

    # Determined CEFR level
    determined_level = Column(String, nullable=True)


class ContentLog(Base):
    """Log all AI-generated content for auditing and improvement."""
    __tablename__ = "content_logs"

    id = Column(String, primary_key=True, default=get_uuid_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    module = Column(String, nullable=False)
    input_payload = Column(JSON, nullable=False)
    generated_content = Column(JSON, nullable=False)
    checker_result = Column(JSON, nullable=True)
    secondary_validation = Column(JSON, nullable=True)
    is_validated = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class LevelHistory(Base):
    """Track historical progression through CEFR levels."""
    __tablename__ = "level_history"

    id = Column(String, primary_key=True, default=get_uuid_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    level = Column(String, nullable=False)  # A1, A2, B1, B2, C1, C2

    # Scores at time of advancement
    vocabulary_score = Column(Float, nullable=True)
    grammar_score = Column(Float, nullable=True)
    writing_score = Column(Float, nullable=True)
    phonetics_score = Column(Float, nullable=True)
    conversation_messages = Column(Integer, default=0)

    # Attempt counts
    vocabulary_attempts = Column(Integer, default=0)
    grammar_attempts = Column(Integer, default=0)
    writing_attempts = Column(Integer, default=0)
    phonetics_attempts = Column(Integer, default=0)

    # Timestamps
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, server_default=func.now())
    days_at_level = Column(Integer, nullable=True)

    # Overall metric
    weighted_score = Column(Float, nullable=False)