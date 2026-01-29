from pydantic import BaseModel, Field, validator
from typing import Optional
import re


class UserRegisterRequest(BaseModel):
    """Request to register a new user."""
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only alphanumeric characters and underscores')
        return v


class UserLoginRequest(BaseModel):
    """Request to login a user."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Response containing user information."""
    id: str
    username: str
    full_name: Optional[str] = None
    target_language: Optional[str] = None
    level: Optional[str] = None
    placement_test_completed: bool = False

    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """Response after successful login."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class UserUpdateLanguageRequest(BaseModel):
    """Request to update user's target language."""
    target_language: str = Field(..., min_length=2, max_length=50)


class UserUpdateLevelRequest(BaseModel):
    """Request to manually set user's proficiency level."""
    level: str = Field(..., pattern=r'^(A1|A2|B1|B2|C1|C2)$')


class UserProgressResponse(BaseModel):
    """Response containing user progress for a module."""
    module: str
    score: Optional[float] = None
    total_attempts: int
    correct_attempts: int


# Legacy schemas for backward compatibility
class UserCreate(BaseModel):
    """Request to create a new user (legacy)."""
    external_id: str
    target_language: Optional[str] = None
    level: Optional[str] = None
