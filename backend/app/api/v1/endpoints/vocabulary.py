from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.schemas.vocabulary import FlashcardResponse, VocabularyAnswerRequest, VocabularyAnswerResponse
from app.services.vocabulary import get_next_flashcard, submit_vocabulary_answer

router = APIRouter()


@router.get("/next", response_model=FlashcardResponse)
async def get_flashcard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get next vocabulary flashcard for authenticated user."""
    if not current_user.target_language:
        raise HTTPException(status_code=400, detail="Please set your target language first")

    if not current_user.level:
        raise HTTPException(status_code=400, detail="Please set your proficiency level or take the placement test")

    try:
        return await get_next_flashcard(current_user.id, current_user.target_language, current_user.level, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=VocabularyAnswerResponse)
async def submit_answer(
    request: VocabularyAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit vocabulary answer."""
    try:
        return await submit_vocabulary_answer(request, current_user, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
