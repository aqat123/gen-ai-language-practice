from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.schemas.conversation import (
    ConversationStartRequest,
    ConversationStartResponse,
    ConversationMessageRequest,
    ConversationMessageResponse
)
from app.services.conversation import start_conversation, send_message

router = APIRouter()


@router.post("/start", response_model=ConversationStartResponse)
async def start_conversation_endpoint(
    request: ConversationStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new conversation session for authenticated user."""
    if not current_user.target_language:
        raise HTTPException(status_code=400, detail="Please set your target language first")

    if not current_user.level:
        raise HTTPException(status_code=400, detail="Please set your proficiency level or take the placement test")

    try:
        return await start_conversation(current_user, request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/message", response_model=ConversationMessageResponse)
async def send_message_endpoint(
    session_id: str,
    request: ConversationMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a conversation session."""
    try:
        return await send_message(session_id, current_user, request, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
