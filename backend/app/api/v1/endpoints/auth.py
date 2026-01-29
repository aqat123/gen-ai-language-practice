from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.db.models import User, UserProgress
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserLoginResponse,
    UserResponse,
    UserUpdateLanguageRequest,
    UserUpdateLevelRequest,
    UserProgressResponse,
    UserCreate  # Legacy
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    update_user_language,
    update_user_level
)
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=UserLoginResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user with username and password.

    Returns JWT token and user information.
    """
    # Register user
    user = register_user(db, user_data)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.id})

    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.from_orm(user)
    )


@router.post("/login", response_model=UserLoginResponse)
async def login(credentials: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    """
    # Authenticate user
    user = authenticate_user(db, credentials.username, credentials.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.id})

    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return UserResponse.from_orm(current_user)


@router.put("/me/language", response_model=UserResponse)
async def update_language(
    language_data: UserUpdateLanguageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's target language.
    """
    user = update_user_language(db, current_user.id, language_data.target_language)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.from_orm(user)


@router.put("/me/level", response_model=UserResponse)
async def update_level(
    level_data: UserUpdateLevelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually set current user's proficiency level (skips placement test).
    """
    user = update_user_level(db, current_user.id, level_data.level)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Mark placement test as completed if manually setting level
    user.placement_test_completed = True
    db.commit()
    db.refresh(user)

    return UserResponse.from_orm(user)


@router.get("/me/progress", response_model=List[UserProgressResponse])
async def get_my_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's progress across all modules.
    """
    progress_records = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).all()

    return [
        UserProgressResponse(
            module=p.module,
            score=p.score,
            total_attempts=p.total_attempts,
            correct_attempts=p.correct_attempts
        )
        for p in progress_records
    ]


# Legacy endpoints for backward compatibility
@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (legacy endpoint)."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.external_id == user.external_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create new user
    new_user = User(
        external_id=user.external_id,
        target_language=user.target_language,
        level=user.level,
        username=user.external_id,  # Use external_id as username for legacy users
        hashed_password="",  # Legacy users have no password
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse.from_orm(new_user)


@router.get("/users/{external_id}", response_model=UserResponse)
async def get_user(external_id: str, db: Session = Depends(get_db)):
    """Get user by external ID (legacy endpoint)."""
    user = db.query(User).filter(User.external_id == external_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.from_orm(user)


@router.get("/users/{external_id}/progress", response_model=List[UserProgressResponse])
async def get_user_progress(external_id: str, db: Session = Depends(get_db)):
    """Get user progress across all modules (legacy endpoint)."""
    user = db.query(User).filter(User.external_id == external_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    progress_records = db.query(UserProgress).filter(UserProgress.user_id == user.id).all()

    return [
        UserProgressResponse(
            module=p.module,
            score=p.score,
            total_attempts=p.total_attempts,
            correct_attempts=p.correct_attempts
        )
        for p in progress_records
    ]
