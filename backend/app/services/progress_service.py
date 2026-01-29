"""
Progress tracking and level advancement service.

Handles:
- Calculating advancement eligibility
- Tracking user progress across modules
- Managing level transitions
- Archiving progress history
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from uuid import uuid4

from app.db.models import User, UserProgress, LevelHistory, ConversationSession
from app.schemas.progress import (
    ModuleProgress,
    ConversationEngagement,
    ProgressSummaryResponse,
    LevelHistoryItem,
    AdvancementResponse
)


# CEFR level progression
LEVEL_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]

# Advancement thresholds
SCORE_THRESHOLD = 85.0  # 85% minimum for each module
MINIMUM_ATTEMPTS = 10  # Minimum attempts per module
CONVERSATION_MINIMUM = 20  # Minimum conversation messages

# XP rewards per level
XP_REWARDS = {
    "A1": 100,
    "A2": 200,
    "B1": 300,
    "B2": 400,
    "C1": 500,
    "C2": 1000
}

# Scored modules (exclude conversation)
SCORED_MODULES = ["vocabulary", "grammar", "writing", "phonetics"]


def get_next_level(current_level: str) -> Optional[str]:
    """Get the next CEFR level, or None if already at max."""
    if not current_level or current_level not in LEVEL_ORDER:
        return "A1"

    current_index = LEVEL_ORDER.index(current_level)
    if current_index < len(LEVEL_ORDER) - 1:
        return LEVEL_ORDER[current_index + 1]
    return None


def _get_module_progress(user_id: str, module: str, db: Session) -> Optional[UserProgress]:
    """Get progress record for a specific module."""
    return db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.module == module
    ).first()


def _get_conversation_message_count(user_id: str, db: Session) -> int:
    """Get total conversation messages sent by user."""
    # Count messages from conversation_sessions context_json
    sessions = db.query(ConversationSession).filter(
        ConversationSession.user_id == user_id
    ).all()

    total_messages = 0
    for session in sessions:
        context = session.context_json
        if isinstance(context, dict) and "messages" in context:
            # Count user messages only
            total_messages += sum(
                1 for msg in context["messages"]
                if isinstance(msg, dict) and msg.get("role") == "user"
            )

    return total_messages


def calculate_advancement_eligibility(user_id: str, db: Session) -> dict:
    """
    Calculate if user is eligible to advance to next level.

    Requirements:
    - All 4 scored modules >= 85% with minimum 10 attempts each
    - Conversation module >= 20 messages
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"eligible": False, "reason": "User not found"}

    if not user.level:
        return {"eligible": False, "reason": "User level not set"}

    next_level = get_next_level(user.level)
    if not next_level:
        return {"eligible": False, "reason": "Already at maximum level (C2)"}

    # Check each scored module
    module_status = {}
    all_modules_ready = True
    blocking_reasons = []

    for module in SCORED_MODULES:
        progress = _get_module_progress(user_id, module, db)

        if not progress:
            module_status[module] = {
                "ready": False,
                "score": None,
                "attempts": 0,
                "reason": "No activity yet"
            }
            all_modules_ready = False
            blocking_reasons.append(f"{module.title()}: No activity yet")
            continue

        score = progress.score or 0.0
        attempts = progress.total_attempts or 0

        meets_score = score >= SCORE_THRESHOLD
        meets_attempts = attempts >= MINIMUM_ATTEMPTS
        ready = meets_score and meets_attempts

        module_status[module] = {
            "ready": ready,
            "score": score,
            "attempts": attempts,
            "reason": None if ready else (
                f"Score too low ({score:.1f}%)" if not meets_score else
                f"Not enough attempts ({attempts}/{MINIMUM_ATTEMPTS})"
            )
        }

        if not ready:
            all_modules_ready = False
            blocking_reasons.append(
                f"{module.title()}: {module_status[module]['reason']}"
            )

    # Check conversation engagement
    conversation_messages = _get_conversation_message_count(user_id, db)
    conversation_ready = conversation_messages >= CONVERSATION_MINIMUM

    if not conversation_ready:
        all_modules_ready = False
        blocking_reasons.append(
            f"Conversation: Need {CONVERSATION_MINIMUM - conversation_messages} more messages"
        )

    eligible = all_modules_ready and conversation_ready

    return {
        "eligible": eligible,
        "reason": None if eligible else "; ".join(blocking_reasons),
        "modules": module_status,
        "conversation_messages": conversation_messages,
        "conversation_ready": conversation_ready
    }


def get_user_progress_summary(user_id: str, db: Session) -> ProgressSummaryResponse:
    """Get comprehensive progress summary for user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Get advancement eligibility
    eligibility = calculate_advancement_eligibility(user_id, db)

    # Build module progress list
    modules = []
    total_score = 0.0
    scored_count = 0

    for module in SCORED_MODULES:
        progress = _get_module_progress(user_id, module, db)

        if progress:
            score = progress.score or 0.0
            total_attempts = progress.total_attempts or 0
            correct_attempts = progress.correct_attempts or 0
            last_activity = progress.last_activity_at

            meets_threshold = score >= SCORE_THRESHOLD
            meets_minimum = total_attempts >= MINIMUM_ATTEMPTS

            modules.append(ModuleProgress(
                module=module,
                score=score,
                total_attempts=total_attempts,
                correct_attempts=correct_attempts,
                last_activity=last_activity,
                meets_threshold=meets_threshold,
                meets_minimum_attempts=meets_minimum
            ))

            total_score += score
            scored_count += 1
        else:
            modules.append(ModuleProgress(
                module=module,
                score=None,
                total_attempts=0,
                correct_attempts=0,
                last_activity=None,
                meets_threshold=False,
                meets_minimum_attempts=False
            ))

    # Conversation engagement
    conversation_messages = eligibility["conversation_messages"]
    conversation_engagement = ConversationEngagement(
        total_messages=conversation_messages,
        meets_threshold=conversation_messages >= CONVERSATION_MINIMUM
    )

    # Calculate weighted score
    module_scores = {m: eligibility["modules"].get(m, {}).get("score", 0.0) for m in SCORED_MODULES}
    # Ensure all scores are numbers (convert None to 0.0)
    weighted_score = (
        (module_scores.get("vocabulary") or 0.0) * 0.30 +
        (module_scores.get("grammar") or 0.0) * 0.30 +
        (module_scores.get("writing") or 0.0) * 0.20 +
        (module_scores.get("phonetics") or 0.0) * 0.20
    )

    # Calculate overall progress based on modules ready to advance
    # Count how many modules meet BOTH requirements (attempts >= 10 AND score >= 85%)
    modules_ready = 0
    total_modules = 5  # 4 scored modules + conversation

    for module in SCORED_MODULES:
        module_status = eligibility["modules"].get(module, {})
        if module_status.get("ready", False):
            modules_ready += 1

    if eligibility["conversation_ready"]:
        modules_ready += 1

    overall_progress = (modules_ready / total_modules) * 100

    # Calculate time at current level
    days_at_level = 0
    if user.level_started_at:
        delta = datetime.utcnow() - user.level_started_at
        days_at_level = delta.days

    return ProgressSummaryResponse(
        current_level=user.level or "A1",
        next_level=get_next_level(user.level) if user.level else "A1",
        can_advance=eligibility["eligible"],
        advancement_reason=eligibility["reason"],
        overall_progress=overall_progress,
        weighted_score=weighted_score,
        modules=modules,
        conversation_engagement=conversation_engagement,
        time_at_current_level=days_at_level,
        total_xp=user.total_xp or 0
    )


def advance_user_level(user_id: str, db: Session) -> AdvancementResponse:
    """
    Advance user to next level.

    Steps:
    1. Verify eligibility
    2. Archive current progress to level_history
    3. Increment level
    4. Reset progress
    5. Award XP
    6. Return celebration data
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Verify eligibility
    eligibility = calculate_advancement_eligibility(user_id, db)
    if not eligibility["eligible"]:
        raise ValueError(f"Not eligible to advance: {eligibility['reason']}")

    old_level = user.level
    new_level = get_next_level(old_level)

    if not new_level:
        raise ValueError("Already at maximum level")

    # Collect current scores for archiving
    module_scores = {}
    module_attempts = {}

    for module in SCORED_MODULES:
        progress = _get_module_progress(user_id, module, db)
        if progress:
            module_scores[module] = progress.score
            module_attempts[module] = progress.total_attempts
        else:
            module_scores[module] = None
            module_attempts[module] = 0

    conversation_messages = eligibility["conversation_messages"]

    # Calculate weighted score for history (ensure all values are numbers)
    weighted_score = (
        (module_scores.get("vocabulary") or 0.0) * 0.30 +
        (module_scores.get("grammar") or 0.0) * 0.30 +
        (module_scores.get("writing") or 0.0) * 0.20 +
        (module_scores.get("phonetics") or 0.0) * 0.20
    )

    # Calculate days at level
    days_at_level = 0
    if user.level_started_at:
        delta = datetime.utcnow() - user.level_started_at
        days_at_level = delta.days

    # Archive to level_history
    history_entry = LevelHistory(
        id=str(uuid4()),
        user_id=user_id,
        level=old_level,
        vocabulary_score=module_scores.get("vocabulary"),
        grammar_score=module_scores.get("grammar"),
        writing_score=module_scores.get("writing"),
        phonetics_score=module_scores.get("phonetics"),
        conversation_messages=conversation_messages,
        vocabulary_attempts=module_attempts.get("vocabulary", 0),
        grammar_attempts=module_attempts.get("grammar", 0),
        writing_attempts=module_attempts.get("writing", 0),
        phonetics_attempts=module_attempts.get("phonetics", 0),
        started_at=user.level_started_at or user.created_at,
        completed_at=datetime.utcnow(),
        days_at_level=days_at_level,
        weighted_score=weighted_score
    )
    db.add(history_entry)

    # Reset progress for new level
    reset_progress_for_new_level(user_id, db)

    # Update user
    user.level = new_level
    user.level_started_at = datetime.utcnow()
    user.can_advance = False
    user.advancement_notified_at = None

    # Award XP
    xp_earned = XP_REWARDS.get(old_level, 100)
    user.total_xp = (user.total_xp or 0) + xp_earned

    db.commit()

    celebration_message = f"Congratulations! You've advanced from {old_level} to {new_level}!"

    return AdvancementResponse(
        success=True,
        new_level=new_level,
        old_level=old_level,
        xp_earned=xp_earned,
        celebration_message=celebration_message,
        module_scores=module_scores
    )


def reset_progress_for_new_level(user_id: str, db: Session):
    """Reset all module progress scores and attempts to 0."""
    progress_records = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).all()

    for progress in progress_records:
        progress.score = 0.0
        progress.total_attempts = 0
        progress.correct_attempts = 0


def get_level_history(user_id: str, db: Session) -> List[LevelHistoryItem]:
    """Get historical level progression for user."""
    history_records = db.query(LevelHistory).filter(
        LevelHistory.user_id == user_id
    ).order_by(LevelHistory.completed_at.desc()).all()

    result = []
    for record in history_records:
        scores = {
            "vocabulary": record.vocabulary_score,
            "grammar": record.grammar_score,
            "writing": record.writing_score,
            "phonetics": record.phonetics_score,
            "conversation_messages": record.conversation_messages
        }

        result.append(LevelHistoryItem(
            level=record.level,
            started_at=record.started_at,
            completed_at=record.completed_at,
            days_at_level=record.days_at_level or 0,
            weighted_score=record.weighted_score,
            scores=scores
        ))

    return result
