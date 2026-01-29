from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.schemas.grammar import GrammarQuestionResponse, GrammarAnswerRequest, GrammarAnswerResponse
from app.services.grammar import get_grammar_question, submit_grammar_answer

router = APIRouter()


@router.get("/question", response_model=GrammarQuestionResponse)
async def get_question(
    topic: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get grammar question for authenticated user."""
    if not current_user.target_language:
        raise HTTPException(status_code=400, detail="Please set your target language first")

    if not current_user.level:
        raise HTTPException(status_code=400, detail="Please set your proficiency level or take the placement test")

    try:
        return await get_grammar_question(current_user.id, current_user.target_language, current_user.level, topic, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=GrammarAnswerResponse)
async def submit_answer(
    request: GrammarAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit grammar answer."""
    try:
        return await submit_grammar_answer(request, current_user, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
