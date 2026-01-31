"""
Unit tests for database models.

These tests verify model creation, relationships, constraints, and data integrity.
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    User,
    UserProgress,
    ConversationSession,
    PlacementTest,
    ContentLog,
    LevelHistory
)
from app.core.security import get_password_hash


class TestUserModel:
    """Test cases for User model."""
    
    def test_create_user_with_all_fields(self, db_session):
        """Test creating a user with all fields populated."""
        # Arrange & Act
        user = User(
            username="fulluser",
            hashed_password=get_password_hash("password123"),
            full_name="Full User",
            target_language="Spanish",
            level="B1",
            is_active=True,
            placement_test_completed=True,
            placement_test_score=85.5,
            total_xp=1000
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.id is not None
        assert user.username == "fulluser"
        assert user.full_name == "Full User"
        assert user.target_language == "Spanish"
        assert user.level == "B1"
        assert user.is_active is True
        assert user.placement_test_completed is True
        assert user.placement_test_score == 85.5
        assert user.total_xp == 1000
        assert user.created_at is not None
    
    def test_create_user_with_minimal_fields(self, db_session):
        """Test creating a user with only required fields."""
        # Arrange & Act
        user = User(
            username="minimaluser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.id is not None
        assert user.username == "minimaluser"
        assert user.is_active is True  # Default value
        assert user.placement_test_completed is False  # Default value
        assert user.total_xp == 0  # Default value
    
    def test_user_unique_username_constraint(self, db_session):
        """Test that duplicate usernames raise an integrity error."""
        # Arrange
        user1 = User(username="duplicate", hashed_password="hash1")
        db_session.add(user1)
        db_session.commit()
        
        # Act & Assert
        user2 = User(username="duplicate", hashed_password="hash2")
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_auto_generates_id(self, db_session):
        """Test that user ID is automatically generated."""
        # Arrange & Act
        user = User(username="autoid", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.id is not None
        assert len(user.id) > 0  # UUID string
    
    def test_user_timestamps(self, db_session):
        """Test that created_at timestamp is automatically set."""
        # Arrange & Act
        user = User(username="timestamps", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)


class TestUserProgressModel:
    """Test cases for UserProgress model."""
    
    def test_create_user_progress(self, db_session, sample_user):
        """Test creating a user progress entry."""
        # Arrange & Act
        progress = UserProgress(
            user_id=sample_user.id,
            module="vocabulary",
            score=85.5,
            total_attempts=10,
            correct_attempts=8
        )
        db_session.add(progress)
        db_session.commit()
        db_session.refresh(progress)
        
        # Assert
        assert progress.id is not None
        assert progress.user_id == sample_user.id
        assert progress.module == "vocabulary"
        assert progress.score == 85.5
        assert progress.total_attempts == 10
        assert progress.correct_attempts == 8
        assert progress.last_activity_at is not None
    
    def test_user_progress_default_values(self, db_session, sample_user):
        """Test user progress default values."""
        # Arrange & Act
        progress = UserProgress(
            user_id=sample_user.id,
            module="grammar"
        )
        db_session.add(progress)
        db_session.commit()
        db_session.refresh(progress)
        
        # Assert
        assert progress.total_attempts == 0
        assert progress.correct_attempts == 0
        assert progress.last_activity_at is not None
    
    def test_multiple_progress_entries_per_user(self, db_session, sample_user):
        """Test that a user can have multiple progress entries."""
        # Arrange & Act
        modules = ["vocabulary", "grammar", "conversation", "writing"]
        for module in modules:
            progress = UserProgress(
                user_id=sample_user.id,
                module=module,
                total_attempts=5
            )
            db_session.add(progress)
        db_session.commit()
        
        # Assert
        user_progress = db_session.query(UserProgress).filter_by(
            user_id=sample_user.id
        ).all()
        assert len(user_progress) == 4
        
        # Verify all modules are present
        progress_modules = [p.module for p in user_progress]
        assert set(progress_modules) == set(modules)


class TestConversationSessionModel:
    """Test cases for ConversationSession model."""
    
    def test_create_conversation_session(self, db_session, sample_user):
        """Test creating a conversation session."""
        # Arrange & Act
        session = ConversationSession(
            user_id=sample_user.id,
            target_language="French",
            context_json={
                "topic": "travel",
                "messages": []
            },
            is_active=True
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        # Assert
        assert session.id is not None
        assert session.user_id == sample_user.id
        assert session.target_language == "French"
        assert session.context_json["topic"] == "travel"
        assert session.is_active is True
        assert session.created_at is not None
    
    def test_conversation_session_default_context(self, db_session, sample_user):
        """Test conversation session with default empty context."""
        # Arrange & Act
        session = ConversationSession(
            user_id=sample_user.id
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        # Assert
        assert session.context_json == {} or session.context_json is not None
        assert session.is_active is True
    
    def test_conversation_session_json_storage(self, db_session, sample_user):
        """Test that JSON data is stored and retrieved correctly."""
        # Arrange
        conversation_data = {
            "topic": "food",
            "difficulty": "intermediate",
            "messages": [
                {"role": "user", "text": "Bonjour"},
                {"role": "assistant", "text": "Bonjour! Ça va?"}
            ]
        }
        
        # Act
        session = ConversationSession(
            user_id=sample_user.id,
            context_json=conversation_data
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        # Assert
        assert session.context_json == conversation_data
        assert len(session.context_json["messages"]) == 2


class TestPlacementTestModel:
    """Test cases for PlacementTest model."""
    
    def test_create_placement_test(self, db_session, sample_user):
        """Test creating a placement test."""
        # Arrange & Act
        test = PlacementTest(
            user_id=sample_user.id,
            target_language="German",
            completed=False,
            questions_data={"questions": []},
            answers_data={}
        )
        db_session.add(test)
        db_session.commit()
        db_session.refresh(test)
        
        # Assert
        assert test.id is not None
        assert test.user_id == sample_user.id
        assert test.target_language == "German"
        assert test.completed is False
        assert test.test_date is not None
    
    def test_placement_test_with_scores(self, db_session, sample_user):
        """Test placement test with all score fields."""
        # Arrange & Act
        test = PlacementTest(
            user_id=sample_user.id,
            target_language="Spanish",
            completed=True,
            questions_data={"questions": []},
            answers_data={"answers": []},
            vocabulary_score=85.0,
            grammar_score=78.5,
            reading_score=82.0,
            overall_score=81.8,
            determined_level="B1"
        )
        db_session.add(test)
        db_session.commit()
        db_session.refresh(test)
        
        # Assert
        assert test.vocabulary_score == 85.0
        assert test.grammar_score == 78.5
        assert test.reading_score == 82.0
        assert test.overall_score == 81.8
        assert test.determined_level == "B1"
    
    def test_placement_test_json_data(self, db_session, sample_user):
        """Test placement test JSON data storage."""
        # Arrange
        questions = {
            "questions": [
                {"id": 1, "text": "What is your name?", "type": "vocabulary"},
                {"id": 2, "text": "Complete: I ___ a student", "type": "grammar"}
            ]
        }
        answers = {
            "answers": [
                {"question_id": 1, "answer": "correct"},
                {"question_id": 2, "answer": "am"}
            ]
        }
        
        # Act
        test = PlacementTest(
            user_id=sample_user.id,
            target_language="English",
            questions_data=questions,
            answers_data=answers
        )
        db_session.add(test)
        db_session.commit()
        db_session.refresh(test)
        
        # Assert
        assert len(test.questions_data["questions"]) == 2
        assert len(test.answers_data["answers"]) == 2


class TestContentLogModel:
    """Test cases for ContentLog model."""
    
    def test_create_content_log(self, db_session, sample_user):
        """Test creating a content log entry."""
        # Arrange & Act
        log = ContentLog(
            user_id=sample_user.id,
            module="vocabulary",
            input_payload={"language": "German", "level": "A1"},
            generated_content={"word": "Haus", "meaning": "house"},
            is_validated=False
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)
        
        # Assert
        assert log.id is not None
        assert log.user_id == sample_user.id
        assert log.module == "vocabulary"
        assert log.input_payload["language"] == "German"
        assert log.generated_content["word"] == "Haus"
        assert log.is_validated is False
        assert log.created_at is not None
    
    def test_content_log_with_validation(self, db_session, sample_user):
        """Test content log with checker and validation results."""
        # Arrange & Act
        log = ContentLog(
            user_id=sample_user.id,
            module="grammar",
            input_payload={"topic": "present tense"},
            generated_content={"question": "Fill in the blank"},
            checker_result={"is_valid": True, "confidence": 0.95},
            secondary_validation={"human_verified": True},
            is_validated=True
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)
        
        # Assert
        assert log.checker_result["is_valid"] is True
        assert log.secondary_validation["human_verified"] is True
        assert log.is_validated is True


class TestLevelHistoryModel:
    """Test cases for LevelHistory model."""
    
    def test_create_level_history(self, db_session, sample_user):
        """Test creating a level history entry."""
        # Arrange
        started_at = datetime.utcnow()
        
        # Act
        history = LevelHistory(
            user_id=sample_user.id,
            level="A2",
            vocabulary_score=85.0,
            grammar_score=80.0,
            writing_score=78.0,
            phonetics_score=82.0,
            vocabulary_attempts=50,
            grammar_attempts=45,
            writing_attempts=20,
            phonetics_attempts=30,
            conversation_messages=100,
            started_at=started_at,
            days_at_level=45,
            weighted_score=81.25
        )
        db_session.add(history)
        db_session.commit()
        db_session.refresh(history)
        
        # Assert
        assert history.id is not None
        assert history.user_id == sample_user.id
        assert history.level == "A2"
        assert history.vocabulary_score == 85.0
        assert history.days_at_level == 45
        assert history.weighted_score == 81.25
        assert history.completed_at is not None
    
    def test_level_history_default_values(self, db_session, sample_user):
        """Test level history default values."""
        # Arrange & Act
        history = LevelHistory(
            user_id=sample_user.id,
            level="B1",
            started_at=datetime.utcnow(),
            weighted_score=75.0
        )
        db_session.add(history)
        db_session.commit()
        db_session.refresh(history)
        
        # Assert
        assert history.conversation_messages == 0
        assert history.vocabulary_attempts == 0
        assert history.grammar_attempts == 0
    
    def test_multiple_level_history_entries(self, db_session, sample_user):
        """Test tracking progression through multiple levels."""
        # Arrange
        levels = ["A1", "A2", "B1"]
        
        # Act
        for level in levels:
            history = LevelHistory(
                user_id=sample_user.id,
                level=level,
                started_at=datetime.utcnow(),
                weighted_score=80.0
            )
            db_session.add(history)
        db_session.commit()
        
        # Assert
        user_history = db_session.query(LevelHistory).filter_by(
            user_id=sample_user.id
        ).all()
        assert len(user_history) == 3
        
        # Verify all levels are tracked
        tracked_levels = [h.level for h in user_history]
        assert set(tracked_levels) == set(levels)


class TestModelRelationships:
    """Test relationships between models."""
    
    def test_user_has_multiple_progress_entries(self, db_session, sample_user):
        """Test that a user can have multiple progress entries."""
        # Arrange & Act
        progress1 = UserProgress(user_id=sample_user.id, module="vocabulary")
        progress2 = UserProgress(user_id=sample_user.id, module="grammar")
        db_session.add_all([progress1, progress2])
        db_session.commit()
        
        # Assert
        progress_count = db_session.query(UserProgress).filter_by(
            user_id=sample_user.id
        ).count()
        assert progress_count == 2
    
    def test_user_has_multiple_conversation_sessions(self, db_session, sample_user):
        """Test that a user can have multiple conversation sessions."""
        # Arrange & Act
        session1 = ConversationSession(user_id=sample_user.id)
        session2 = ConversationSession(user_id=sample_user.id)
        db_session.add_all([session1, session2])
        db_session.commit()
        
        # Assert
        session_count = db_session.query(ConversationSession).filter_by(
            user_id=sample_user.id
        ).count()
        assert session_count == 2
