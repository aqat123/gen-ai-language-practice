"""
Achievements endpoints for tracking and displaying user achievements.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.services.achievements_service import (
    get_user_achievements,
    mark_achievements_viewed
)

router = APIRouter()


@router.get("/")
async def list_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get all achievements for the current user.

    Returns:
    - unlocked: List of unlocked achievements with unlock dates
    - locked: List of locked achievements with progress percentages
    - new_count: Number of unviewed unlocked achievements
    """
    try:
        return get_user_achievements(current_user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get achievements: {str(e)}")


@router.post("/mark-viewed")
async def mark_viewed(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all user's achievements as viewed (clear NEW badges).
    """
    try:
        success = mark_achievements_viewed(current_user.id, db)
        return {"success": success, "message": "Achievements marked as viewed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark achievements as viewed: {str(e)}")
