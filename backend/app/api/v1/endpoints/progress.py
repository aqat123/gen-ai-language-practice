"""
Progress tracking and level advancement endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.services.progress_service import (
    get_user_progress_summary,
    advance_user_level,
    get_level_history
)
from app.schemas.progress import (
    ProgressSummaryResponse,
    AdvancementResponse,
    LevelHistoryItem
)

router = APIRouter()


@router.get("/summary", response_model=ProgressSummaryResponse)
async def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get overall progress summary and advancement eligibility.

    Returns:
    - Current level and next level
    - Module-specific progress with thresholds
    - Conversation engagement metrics
    - Advancement eligibility status
    - Time at current level
    - Total XP
    """
    try:
        return get_user_progress_summary(current_user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress summary: {str(e)}")


@router.post("/advance", response_model=AdvancementResponse)
async def advance_level(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger level advancement for current user.

    Requirements:
    - All scored modules (vocabulary, grammar, writing, phonetics) >= 85%
    - Minimum 10 attempts per module
    - Minimum 20 conversation messages

    Actions:
    - Archives current progress to level_history
    - Advances user to next CEFR level
    - Resets module progress to 0
    - Awards XP based on level completed
    """
    try:
        return advance_user_level(current_user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to advance level: {str(e)}")


@router.get("/history", response_model=List[LevelHistoryItem])
async def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get historical level progression for current user.

    Returns list of completed levels with:
    - Level name (A1, A2, etc.)
    - Start and completion timestamps
    - Days spent at that level
    - Final scores for each module
    - Weighted overall score
    """
    try:
        return get_level_history(current_user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get level history: {str(e)}")


@router.get("/modules/{module}")
async def get_module_details(
    module: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed progress for a specific module.

    Currently returns basic module info.
    Can be extended with trend analysis and recommendations.
    """
    from app.db.models import UserProgress

    try:
        # Validate module name
        valid_modules = ["vocabulary", "grammar", "writing", "phonetics", "conversation"]
        if module not in valid_modules:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid module. Must be one of: {', '.join(valid_modules)}"
            )

        # Get progress for this module
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.module == module
        ).first()

        if not progress:
            return {
                "module": module,
                "current_score": None,
                "total_attempts": 0,
                "correct_attempts": 0,
                "message": "No activity in this module yet"
            }

        return {
            "module": module,
            "current_score": progress.score,
            "total_attempts": progress.total_attempts,
            "correct_attempts": progress.correct_attempts,
            "last_activity": progress.last_activity_at
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get module details: {str(e)}")
