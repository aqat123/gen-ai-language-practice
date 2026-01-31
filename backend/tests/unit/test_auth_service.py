"""
Unit tests for authentication service.

These tests verify user registration, login, and authentication logic
without making actual API calls.
"""

import pytest
from sqlalchemy.orm import Session

from app.services.auth_service import (
    register_user,
    authenticate_user,
    update_user_language,
    update_user_level
)
from app.schemas.auth import UserRegisterRequest
from app.db.models import User
from app.core.security import verify_password


class TestUserRegistration:
    """Test cases for user registration."""
    
    def test_register_user_creates_new_user(self, db_session: Session):
        """Test that registering a user creates a new database entry."""
        # Arrange
        user_data = UserRegisterRequest(
            username="newuser",
            password="securepassword123",
            full_name="New User"
        )
        
        # Act
        user = register_user(db_session, user_data)
        
        # Assert
        assert user is not None
        assert user.username == "newuser"
        assert user.full_name == "New User"
        assert user.hashed_password != "securepassword123"  # Should be hashed
        assert user.is_active is True
        
        # Verify password was hashed correctly
        assert verify_password("securepassword123", user.hashed_password)
    
    def test_register_user_with_duplicate_username_returns_none(self, db_session: Session):
        """Test that registering with an existing username fails."""
        # Arrange
        user_data = UserRegisterRequest(
            username="duplicate",
            password="password123",
            full_name="First User"
        )
        register_user(db_session, user_data)
        
        # Act - Try to register again with same username
        duplicate_data = UserRegisterRequest(
            username="duplicate",
            password="differentpass",
            full_name="Second User"
        )
        result = register_user(db_session, duplicate_data)
        
        # Assert
        assert result is None  # Should fail
        
        # Verify only one user exists
        users = db_session.query(User).filter_by(username="duplicate").all()
        assert len(users) == 1
    
    def test_register_user_with_all_optional_fields(self, db_session: Session):
        """Test that registering a user with all fields works correctly."""
        # Arrange
        user_data = UserRegisterRequest(
            username="fulluser",
            password="password123",
            full_name="Full Name User"
        )
        
        # Act
        user = register_user(db_session, user_data)
        
        # Assert
        assert user is not None
        assert user.username == "fulluser"
        assert user.full_name == "Full Name User"
        assert user.is_active is True
        assert verify_password("password123", user.hashed_password)
    
    def test_register_user_with_minimal_data(self, db_session: Session):
        """Test registration with minimal required data."""
        # Arrange
        user_data = UserRegisterRequest(
            username="minimal",
            password="password123"
        )
        
        # Act
        user = register_user(db_session, user_data)
        
        # Assert
        assert user is not None
        assert user.username == "minimal"
        assert user.full_name is None
        assert user.target_language is None
        assert user.level is None
    
    def test_register_user_password_is_hashed(self, db_session: Session):
        """Test that user passwords are properly hashed."""
        # Arrange
        plain_password = "myplainpassword"
        user_data = UserRegisterRequest(
            username="hashtest",
            password=plain_password,
            full_name="Hash Test"
        )
        
        # Act
        user = register_user(db_session, user_data)
        
        # Assert
        assert user.hashed_password != plain_password
        assert len(user.hashed_password) > 20  # Hashed passwords are long
        assert verify_password(plain_password, user.hashed_password)
        assert not verify_password("wrongpassword", user.hashed_password)


class TestUserAuthentication:
    """Test cases for user authentication."""
    
    def test_authenticate_user_with_correct_password(self, db_session: Session):
        """Test that authentication succeeds with correct credentials."""
        # Arrange - Create a user first
        user_data = UserRegisterRequest(
            username="authtest",
            password="mypassword",
            full_name="Auth Test"
        )
        created_user = register_user(db_session, user_data)
        
        # Act
        authenticated_user = authenticate_user(db_session, "authtest", "mypassword")
        
        # Assert
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.username == "authtest"
    
    def test_authenticate_user_with_wrong_password(self, db_session: Session):
        """Test that authentication fails with incorrect password."""
        # Arrange
        user_data = UserRegisterRequest(
            username="authtest2",
            password="correctpassword",
            full_name="Auth Test 2"
        )
        register_user(db_session, user_data)
        
        # Act
        user = authenticate_user(db_session, "authtest2", "wrongpassword")
        
        # Assert
        assert user is None
    
    def test_authenticate_user_with_nonexistent_username(self, db_session: Session):
        """Test that authentication fails with non-existent username."""
        # Act
        user = authenticate_user(db_session, "nonexistent", "anypassword")
        
        # Assert
        assert user is None
    
    def test_authenticate_user_case_sensitive_username(self, db_session: Session):
        """Test that usernames are case-sensitive."""
        # Arrange
        user_data = UserRegisterRequest(
            username="CaseSensitive",
            password="password123",
            full_name="Case Test"
        )
        register_user(db_session, user_data)
        
        # Act - Try with different case
        user_lower = authenticate_user(db_session, "casesensitive", "password123")
        user_correct = authenticate_user(db_session, "CaseSensitive", "password123")
        
        # Assert
        assert user_lower is None  # Should fail with wrong case
        assert user_correct is not None  # Should succeed with correct case
    
    def test_authenticate_inactive_user(self, db_session: Session):
        """Test that inactive users cannot authenticate."""
        # Arrange - Create and deactivate a user
        user_data = UserRegisterRequest(
            username="inactive",
            password="password123",
            full_name="Inactive User"
        )
        user = register_user(db_session, user_data)
        user.is_active = False
        db_session.commit()
        
        # Act
        authenticated_user = authenticate_user(db_session, "inactive", "password123")
        
        # Assert
        assert authenticated_user is None


class TestUserLanguageUpdate:
    """Test cases for updating user language."""
    
    def test_update_user_language_success(self, db_session: Session, sample_user: User):
        """Test successfully updating user's target language."""
        # Act
        updated_user = update_user_language(db_session, sample_user.id, "French")
        
        # Assert
        assert updated_user is not None
        assert updated_user.target_language == "French"
        
        # Verify in database
        db_user = db_session.query(User).filter_by(id=sample_user.id).first()
        assert db_user.target_language == "French"
    
    def test_update_user_language_for_nonexistent_user(self, db_session: Session):
        """Test updating language for non-existent user returns None."""
        # Act
        result = update_user_language(db_session, "nonexistent-id", "Spanish")
        
        # Assert
        assert result is None
    
    def test_update_user_language_to_none(self, db_session: Session, sample_user: User):
        """Test updating language to None (clearing it)."""
        # Act
        updated_user = update_user_language(db_session, sample_user.id, None)
        
        # Assert
        assert updated_user is not None
        assert updated_user.target_language is None


class TestUserLevelUpdate:
    """Test cases for updating user level."""
    
    def test_update_user_level_success(self, db_session: Session, sample_user: User):
        """Test successfully updating user's proficiency level."""
        # Act
        updated_user = update_user_level(db_session, sample_user.id, "B1")
        
        # Assert
        assert updated_user is not None
        assert updated_user.level == "B1"
        
        # Verify in database
        db_user = db_session.query(User).filter_by(id=sample_user.id).first()
        assert db_user.level == "B1"
    
    def test_update_user_level_for_nonexistent_user(self, db_session: Session):
        """Test updating level for non-existent user returns None."""
        # Act
        result = update_user_level(db_session, "nonexistent-id", "C2")
        
        # Assert
        assert result is None
    
    @pytest.mark.parametrize("level", ["A1", "A2", "B1", "B2", "C1", "C2"])
    def test_update_user_level_all_valid_levels(
        self,
        db_session: Session,
        sample_user: User,
        level: str
    ):
        """Test that all CEFR levels can be set."""
        # Act
        updated_user = update_user_level(db_session, sample_user.id, level)
        
        # Assert
        assert updated_user is not None
        assert updated_user.level == level


class TestUserModel:
    """Test cases for User model properties."""
    
    def test_user_default_values(self, db_session: Session):
        """Test that User model has correct default values."""
        # Arrange & Act
        user = User(
            username="defaults",
            hashed_password="hash"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.is_active is True
        assert user.placement_test_completed is False
        assert user.placement_test_score is None
        assert user.target_language is None
        assert user.level is None
        assert user.can_advance is False
        assert user.total_xp == 0
        assert user.id is not None  # UUID should be generated
        assert user.created_at is not None
    
    def test_user_unique_username_constraint(self, db_session: Session):
        """Test that duplicate usernames raise an error."""
        # Arrange
        user1 = User(username="unique", hashed_password="hash1")
        db_session.add(user1)
        db_session.commit()
        
        # Act & Assert
        user2 = User(username="unique", hashed_password="hash2")
        db_session.add(user2)
        
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            db_session.commit()
