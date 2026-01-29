from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.services.phonetics import evaluate_pronunciation, generate_target_phrase
from app.schemas.phonetics import PhoneticsEvaluationResponse, PhoneticsPracticeSession

router = APIRouter()


@router.get("/phrase", response_model=PhoneticsPracticeSession)
async def get_practice_phrase(
        current_user: User = Depends(get_current_user)
):
    """Get a practice phrase for authenticated user."""
    if not current_user.target_language:
        raise HTTPException(status_code=400, detail="Please set your target language first")

    if not current_user.level:
        raise HTTPException(status_code=400, detail="Please set your proficiency level or take the placement test")

    result = await generate_target_phrase(current_user.target_language, current_user.level)
    return result


@router.post("/evaluate", response_model=PhoneticsEvaluationResponse)
async def evaluate_audio(
        target_phrase: str = Form(...),
        audio_file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Evaluate pronunciation for authenticated user."""
    if not current_user.target_language:
        raise HTTPException(status_code=400, detail="Please set your target language first")

    # Read the audio bytes from the uploaded file
    audio_bytes = await audio_file.read()

    # Call the service logic
    result = await evaluate_pronunciation(
        user_id=current_user.id,
        target_language=current_user.target_language,
        target_phrase=target_phrase,
        audio_bytes=audio_bytes,
        db=db
    )
    return result