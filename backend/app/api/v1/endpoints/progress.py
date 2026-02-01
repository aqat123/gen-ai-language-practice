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
from pydantic import BaseModel

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


class CheatCodeRequest(BaseModel):
    code: str


@router.post("/cheat-code")
async def apply_cheat_code(
    request: CheatCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply cheat code for demo purposes.

    Code 'fullclip' sets all progress to 100% and meets advancement criteria.
    """
    from app.db.models import UserProgress, ConversationSession
    from datetime import datetime

    if request.code != "fullclip":
        raise HTTPException(status_code=400, detail="Invalid cheat code")

    try:
        # Set all module progress to 100%
        modules = ["vocabulary", "grammar", "writing", "phonetics"]

        for module in modules:
            progress = db.query(UserProgress).filter(
                UserProgress.user_id == current_user.id,
                UserProgress.module == module
            ).first()

            if not progress:
                progress = UserProgress(
                    user_id=current_user.id,
                    module=module,
                    total_attempts=15,
                    correct_attempts=15,
                    score=95.0,
                    last_activity_at=datetime.utcnow()
                )
                db.add(progress)
            else:
                progress.total_attempts = max(progress.total_attempts, 15)
                progress.correct_attempts = max(progress.correct_attempts, 15)
                progress.score = 95.0
                progress.last_activity_at = datetime.utcnow()

        # Add conversation messages if needed
        sessions = db.query(ConversationSession).filter(
            ConversationSession.user_id == current_user.id
        ).all()

        # Count existing user messages
        existing_messages = 0
        for session in sessions:
            context = session.context_json
            if isinstance(context, dict) and "messages" in context:
                existing_messages += sum(
                    1 for msg in context["messages"]
                    if isinstance(msg, dict) and msg.get("role") == "user"
                )

        # If less than 25 messages, create a new session with dummy messages
        if existing_messages < 25:
            from uuid import uuid4
            # Create dummy user messages
            dummy_messages = []
            for i in range(25):
                dummy_messages.append({"role": "user", "content": f"Practice message {i+1}"})
                dummy_messages.append({"role": "assistant", "content": f"Response {i+1}"})

            session = ConversationSession(
                id=str(uuid4()),
                user_id=current_user.id,
                target_language=current_user.target_language or "Spanish",
                context_json={"messages": dummy_messages},
                created_at=datetime.utcnow()
            )
            db.add(session)

        # Set user as eligible for advancement
        current_user.can_advance = True
        current_user.advancement_notified_at = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "message": "Cheat code applied! All modules set to 95% with 15+ attempts. You can now advance to the next level!",
            "modules_updated": modules,
            "conversation_messages": 25
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to apply cheat code: {str(e)}")


@router.get("/charts")
async def get_charts_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get data formatted for charts visualization.

    Returns:
    - activity_by_date: Daily activity counts by module (last 30 days)
    - module_scores: Current scores for each module
    - level_progression: Historical level completion data
    """
    from app.db.models import ContentLog, UserProgress, LevelHistory
    from datetime import datetime, timedelta
    from collections import defaultdict

    try:
        # 1. Activity over time (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        logs = db.query(ContentLog).filter(
            ContentLog.user_id == current_user.id,
            ContentLog.created_at >= thirty_days_ago
        ).all()

        # Group by date and module
        activity_by_date = defaultdict(lambda: defaultdict(int))
        for log in logs:
            date_str = log.created_at.strftime('%Y-%m-%d')
            activity_by_date[date_str][log.module] += 1

        # Convert to sorted list
        sorted_dates = sorted(activity_by_date.keys())
        activity_data = {
            "dates": sorted_dates,
            "vocabulary": [activity_by_date[d].get("vocabulary", 0) for d in sorted_dates],
            "grammar": [activity_by_date[d].get("grammar", 0) for d in sorted_dates],
            "writing": [activity_by_date[d].get("writing", 0) for d in sorted_dates],
            "phonetics": [activity_by_date[d].get("phonetics", 0) for d in sorted_dates],
            "conversation": [activity_by_date[d].get("conversation", 0) for d in sorted_dates]
        }

        # 2. Current module scores
        progress_records = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id
        ).all()

        module_scores = {
            "modules": [],
            "scores": []
        }

        for progress in progress_records:
            if progress.score is not None:
                module_scores["modules"].append(progress.module.capitalize())
                module_scores["scores"].append(round(progress.score, 1))

        # 3. Level progression history
        level_history = db.query(LevelHistory).filter(
            LevelHistory.user_id == current_user.id
        ).order_by(LevelHistory.completed_at).all()

        level_progression = {
            "levels": [],
            "scores": [],
            "dates": []
        }

        for record in level_history:
            level_progression["levels"].append(record.level)
            level_progression["scores"].append(round(record.weighted_score, 1))
            level_progression["dates"].append(record.completed_at.strftime('%Y-%m-%d'))

        # Always add current level to show progress
        if current_user.level:
            # Calculate current weighted score from all modules
            current_progress = db.query(UserProgress).filter(
                UserProgress.user_id == current_user.id
            ).all()

            scores = [p.score for p in current_progress if p.score is not None]

            # Show current level even if no scores yet
            if scores:
                current_weighted = sum(scores) / len(scores)
            else:
                current_weighted = 0.0

            level_label = f"{current_user.level} (Current)" if level_history else current_user.level
            level_progression["levels"].append(level_label)
            level_progression["scores"].append(round(current_weighted, 1))

            date_str = current_user.level_started_at.strftime('%Y-%m-%d') if current_user.level_started_at else datetime.utcnow().strftime('%Y-%m-%d')
            level_progression["dates"].append(date_str)

        return {
            "activity_over_time": activity_data,
            "module_scores": module_scores,
            "level_progression": level_progression
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get charts data: {str(e)}")


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
