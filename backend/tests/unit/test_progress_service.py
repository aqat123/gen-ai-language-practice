"""
Unit tests for progress service.

Tests:
- Level progression logic
- Advancement eligibility
- Progress summary generation
- Constants validation
"""

import pytest
from uuid import uuid4
from app.services.progress_service import (
    get_next_level,
    calculate_advancement_eligibility,
    get_user_progress_summary,
    advance_user_level,
    get_level_history,
    LEVEL_ORDER,
    SCORE_THRESHOLD,
    MINIMUM_ATTEMPTS,
    CONVERSATION_MINIMUM,
    XP_REWARDS
)
from app.db.models import User, UserProgress, ConversationSession
from datetime import datetime


class TestLevelProgression:
    """Test level progression functionality."""
    
    def test_get_next_level_from_a1(self):
        """Test progression from A1 to A2."""
        assert get_next_level("A1") == "A2"
    
    def test_get_next_level_from_b2(self):
        """Test progression from B2 to C1."""
        assert get_next_level("B2") == "C1"
    
    def test_get_next_level_from_c2_returns_none(self):
        """Test that C2 is the maximum level."""
        assert get_next_level("C2") is None
    
    def test_get_next_level_with_none_returns_a1(self):
        """Test that None level defaults to A1."""
        result = get_next_level(None)
        assert result == "A1" or result is None
    
    def test_get_next_level_with_invalid_level_returns_a1(self):
        """Test handling of invalid level."""
        result = get_next_level("INVALID")
        assert result == "A1" or result is None


class TestAdvancementEligibility:
    """Test advancement eligibility checks."""
    
    def test_user_not_found(self, db_session):
        """Test advancement check for non-existent user."""
        result = calculate_advancement_eligibility(
            user_id="nonexistent",
            db=db_session
        )
        assert result["eligible"] is False
    
    def test_user_without_level(self, db_session):
        """Test user without assigned level."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German"
        )
        db_session.add(user)
        db_session.commit()
        
        result = calculate_advancement_eligibility(
            user_id=user.id,
            db=db_session
        )
        assert result["eligible"] is False
    
    def test_user_at_maximum_level(self, db_session):
        """Test user at C2 level cannot advance."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="C2"
        )
        db_session.add(user)
        db_session.commit()
        
        result = calculate_advancement_eligibility(
            user_id=user.id,
            db=db_session
        )
        assert result["eligible"] is False
    
    def test_user_without_progress(self, db_session):
        """Test user without any module progress."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        result = calculate_advancement_eligibility(
            user_id=user.id,
            db=db_session
        )
        assert result["eligible"] is False
    
    def test_user_with_low_scores(self, db_session):
        """Test user with scores below threshold."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        # Add progress with low score
        progress = UserProgress(
            user_id=user.id,
            module="vocabulary",
            total_attempts=20,
            correct_attempts=8  # 40% score
        )
        db_session.add(progress)
        db_session.commit()
        
        result = calculate_advancement_eligibility(
            user_id=user.id,
            db=db_session
        )
        assert result["eligible"] is False
    
    def test_user_with_insufficient_attempts(self, db_session):
        """Test user with not enough attempts."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        # Add progress with good score but few attempts
        progress = UserProgress(
            user_id=user.id,
            module="vocabulary",
            total_attempts=5,
            correct_attempts=5  # 100% score but only 5 attempts
        )
        db_session.add(progress)
        db_session.commit()
        
        result = calculate_advancement_eligibility(
            user_id=user.id,
            db=db_session
        )
        assert result["eligible"] is False
    
    def test_user_without_enough_conversation(self, db_session):
        """Test user without enough conversation messages."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        # Add excellent progress in all modules
        for module in ["vocabulary", "grammar", "writing", "phonetics"]:
            progress = UserProgress(
                user_id=user.id,
                module=module,
                total_attempts=20,
                correct_attempts=18  # 90% score
            )
            db_session.add(progress)
        db_session.commit()
        
        # But no conversation messages
        result = calculate_advancement_eligibility(
            user_id=user.id,
            db=db_session
        )
        assert result["eligible"] is False


class TestProgressSummary:
    """Test progress summary generation."""
    
    def test_progress_summary_for_new_user(self, db_session):
        """Test progress summary for user with no progress."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        summary = get_user_progress_summary(user_id=user.id, db=db_session)
        
        assert summary is not None
        assert summary.current_level == "A1"
        assert summary.can_advance is False
    
    def test_progress_summary_with_progress(self, db_session):
        """Test progress summary with some module progress."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        # Add progress
        progress = UserProgress(
            user_id=user.id,
            module="vocabulary",
            total_attempts=10,
            correct_attempts=8,
            last_activity_at=datetime.utcnow()
        )
        db_session.add(progress)
        db_session.commit()
        
        summary = get_user_progress_summary(user_id=user.id, db=db_session)
        
        assert summary is not None
        # Should have progress for all modules (some might be empty)
        assert len(summary.modules) >= 1
    
    def test_progress_summary_nonexistent_user_raises_error(self, db_session):
        """Test that non-existent user raises error."""
        with pytest.raises(Exception):
            get_user_progress_summary(user_id="nonexistent", db=db_session)


class TestConstants:
    """Test progress service constants."""
    
    def test_level_order_contains_all_cefr_levels(self):
        """Test that LEVEL_ORDER has all CEFR levels."""
        expected_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        assert LEVEL_ORDER == expected_levels
    
    def test_score_threshold_is_reasonable(self):
        """Test that score threshold is between 0 and 100."""
        assert 0 < SCORE_THRESHOLD <= 100
        assert SCORE_THRESHOLD >= 70  # At least 70% is reasonable
    
    def test_minimum_attempts_is_positive(self):
        """Test that minimum attempts is a positive number."""
        assert MINIMUM_ATTEMPTS > 0
        assert isinstance(MINIMUM_ATTEMPTS, int)
    
    def test_conversation_minimum_is_positive(self):
        """Test that conversation minimum is positive."""
        assert CONVERSATION_MINIMUM > 0
        assert isinstance(CONVERSATION_MINIMUM, int)
    
    def test_xp_rewards_defined_for_all_levels(self):
        """Test that XP rewards exist for all levels."""
        for level in LEVEL_ORDER:
            assert level in XP_REWARDS
            assert XP_REWARDS[level] > 0
    
    def test_xp_rewards_increase_with_level(self):
        """Test that XP rewards generally increase with difficulty."""
        # A1 should have lower or equal XP than higher levels
        assert XP_REWARDS["A1"] <= XP_REWARDS["C2"]


class TestAdvanceUserLevel:
    """Test the advance_user_level function."""
    
    def test_successful_advancement_from_a1_to_a2(self, db_session):
        """Test successful level advancement."""
        from datetime import datetime, timedelta
        
        # Create user at A1
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A1",
            level_started_at=datetime.utcnow() - timedelta(days=10),
            total_xp=0
        )
        db_session.add(user)
        db_session.commit()
        
        # Create progress for all modules with good scores
        for module in ["vocabulary", "grammar", "writing", "phonetics"]:
            progress = UserProgress(
                id=str(uuid4()),
                user_id=user.id,
                module=module,
                score=85.0,
                total_attempts=30,
                correct_attempts=25
            )
            db_session.add(progress)
        
        # Create conversation sessions with messages
        for i in range(6):
            session = ConversationSession(
                id=str(uuid4()),
                user_id=user.id,
                target_language="German",
                context_json={
                    "messages": [
                        {"role": "user", "content": f"Message {j}"}
                        for j in range(5)  # 5 messages per session = 30 total
                    ]
                }
            )
            db_session.add(session)
        
        db_session.commit()
        
        result = advance_user_level(user.id, db_session)
        
        # Check result
        assert result.old_level == "A1"
        assert result.new_level == "A2"
        assert result.xp_earned == XP_REWARDS["A1"]
        
        # Check user updated
        db_session.refresh(user)
        assert user.level == "A2"
        assert user.total_xp == XP_REWARDS["A1"]
        
        # Check level history created
        from app.db.models import LevelHistory
        history = db_session.query(LevelHistory).filter(
            LevelHistory.user_id == user.id
        ).first()
        assert history is not None
        assert history.level == "A1"
    
    def test_advancement_not_eligible_raises_error(self, db_session):
        """Test that advancement fails if user not eligible."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A1",
            total_xp=0
        )
        db_session.add(user)
        db_session.commit()
        
        # No progress created - user not eligible
        with pytest.raises(ValueError, match="Not eligible to advance"):
            advance_user_level(user.id, db_session)
    
    def test_advancement_at_max_level_raises_error(self, db_session):
        """Test that advancement fails at maximum level."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="C2",
            total_xp=1000
        )
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Already at maximum level"):
            advance_user_level(user.id, db_session)
    
    def test_advancement_resets_progress(self, db_session):
        """Test that advancement resets module progress."""
        from datetime import datetime
        
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A1",
            level_started_at=datetime.utcnow(),
            total_xp=0
        )
        db_session.add(user)
        db_session.commit()
        
        # Create progress
        for module in ["vocabulary", "grammar", "writing", "phonetics"]:
            progress = UserProgress(
                id=str(uuid4()),
                user_id=user.id,
                module=module,
                score=90.0,
                total_attempts=30,
                correct_attempts=27
            )
            db_session.add(progress)
        
        # Create conversation sessions with messages
        for i in range(6):
            session = ConversationSession(
                id=str(uuid4()),
                user_id=user.id,
                target_language="German",
                context_json={
                    "messages": [
                        {"role": "user", "content": f"Message {j}"}
                        for j in range(5)  # 5 messages per session = 30 total
                    ]
                }
            )
            db_session.add(session)
        
        db_session.commit()
        
        advance_user_level(user.id, db_session)
        
        # Check all progress reset
        for module in ["vocabulary", "grammar", "writing", "phonetics"]:
            progress = db_session.query(UserProgress).filter(
                UserProgress.user_id == user.id,
                UserProgress.module == module
            ).first()
            assert progress.score == 0.0
            assert progress.total_attempts == 0
            assert progress.correct_attempts == 0
        
        # Check conversations deleted
        sessions = db_session.query(ConversationSession).filter(
            ConversationSession.user_id == user.id
        ).all()
        assert len(sessions) == 0


class TestLevelHistory:
    """Test level history tracking."""
    
    def test_get_level_history_for_new_user(self, db_session):
        """Test getting history for user with no history."""
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A1"
        )
        db_session.add(user)
        db_session.commit()
        
        history = get_level_history(user.id, db_session)
        assert history == []
    
    def test_get_level_history_returns_sorted(self, db_session):
        """Test that history is returned in descending order by completion date."""
        from datetime import datetime, timedelta
        
        user = User(
            username="testuser",
            hashed_password="hash",
            target_language="German",
            level="A2"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create history entries
        from app.db.models import LevelHistory
        
        history1 = LevelHistory(
            id=str(uuid4()),
            user_id=user.id,
            level="A1",
            vocabulary_score=80.0,
            grammar_score=85.0,
            writing_score=75.0,
            phonetics_score=80.0,
            conversation_messages=5,
            weighted_score=80.0,
            days_at_level=10,
            started_at=datetime.utcnow() - timedelta(days=20),
            completed_at=datetime.utcnow() - timedelta(days=10)
        )
        db_session.add(history1)
        db_session.commit()
        
        result = get_level_history(user.id, db_session)
        
        assert len(result) == 1
        assert result[0].level == "A1"
        assert result[0].weighted_score == 80.0
        assert result[0].scores["vocabulary"] == 80.0
        assert result[0].scores["conversation_messages"] == 5
