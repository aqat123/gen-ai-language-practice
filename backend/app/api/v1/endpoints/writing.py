from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.schemas.writing import WritingFeedbackRequest, WritingFeedbackResponse
from app.services.writing import get_writing_feedback
from app.services.writing_prompts import get_writing_prompt, get_all_prompts_for_level

router = APIRouter()


@router.get("/prompts")
async def get_prompts(
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """Get all writing prompts for the user's current level."""
    if not current_user.level:
        raise HTTPException(status_code=400, detail="Please set your proficiency level or take the placement test")

    return get_all_prompts_for_level(current_user.level)


@router.post("/feedback", response_model=WritingFeedbackResponse)
async def get_feedback(
    request: WritingFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get writing feedback for authenticated user."""
    if not current_user.target_language:
        raise HTTPException(status_code=400, detail="Please set your target language first")

    if not current_user.level:
        raise HTTPException(status_code=400, detail="Please set your proficiency level or take the placement test")

    try:
        return await get_writing_feedback(current_user, request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
