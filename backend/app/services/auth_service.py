"""
Authentication service for user registration, login, and management.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.core.security import get_password_hash, verify_password
from app.schemas.auth import UserRegisterRequest


def register_user(db: Session, user_data: UserRegisterRequest) -> Optional[User]:
    """
    Register a new user.

    Args:
        db: Database session
        user_data: User registration data

    Returns:
        Created User object, or None if username already exists

    Raises:
        IntegrityError: If username is not unique
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        return None

    # Create new user with hashed password
    new_user = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        external_id=user_data.username,  # Use username as external_id for new auth users
        is_active=True,
        placement_test_completed=False,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        return None


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password.

    Args:
        db: Database session
        username: Username
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """
    Get a user by ID.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user_language(db: Session, user_id: str, language: str) -> Optional[User]:
    """
    Update user's target language.

    Args:
        db: Database session
        user_id: User ID
        language: Target language

    Returns:
        Updated User object if found, None otherwise
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    user.target_language = language
    db.commit()
    db.refresh(user)
    return user


def update_user_level(db: Session, user_id: str, level: str) -> Optional[User]:
    """
    Update user's proficiency level.

    Args:
        db: Database session
        user_id: User ID
        level: CEFR level (A1-C2)

    Returns:
        Updated User object if found, None otherwise
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    user.level = level
    db.commit()
    db.refresh(user)
    return user
