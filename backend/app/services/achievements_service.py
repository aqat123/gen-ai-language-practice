"""
Achievements Service
Manages achievement unlocking, tracking, and progress calculation.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.db.models import Achievement, UserAchievement, User, UserProgress, LevelHistory, ContentLog


def check_and_unlock_achievements(user_id: str, db: Session) -> List[Dict]:
    """
    Check if user has met criteria for any locked achievements and unlock them.

    Args:
        user_id: User ID to check achievements for
        db: Database session

    Returns:
        List of newly unlocked achievements with details
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    # Get all achievements
    all_achievements = db.query(Achievement).all()

    # Get already unlocked achievement IDs
    unlocked_ids = [
        ua.achievement_id for ua in
        db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()
    ]

    # Filter to only locked achievements
    locked_achievements = [a for a in all_achievements if a.id not in unlocked_ids]

    newly_unlocked = []

    for achievement in locked_achievements:
        # Check if criteria is met
        if _check_criteria(user, achievement, db):
            # Unlock the achievement
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                unlocked_at=datetime.utcnow(),
                is_viewed=False  # Mark as new
            )
            db.add(user_achievement)

            # Award XP
            user.total_xp = (user.total_xp or 0) + achievement.xp_reward

            newly_unlocked.append({
                "id": achievement.id,
                "code": achievement.code,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "tier": achievement.tier,
                "xp_reward": achievement.xp_reward
            })

    if newly_unlocked:
        db.commit()

    return newly_unlocked


def _check_criteria(user: User, achievement: Achievement, db: Session) -> bool:
    """
    Check if user meets the criteria for an achievement.

    Args:
        user: User object
        achievement: Achievement object to check
        db: Database session

    Returns:
        True if criteria is met, False otherwise
    """
    criteria_type = achievement.criteria_type
    threshold = achievement.criteria_threshold
    module = achievement.criteria_module

    if criteria_type == "count":
        # Count-based achievements (e.g., "complete 10 flashcards")
        if module == "all":
            # Total activities across all modules
            total_count = db.query(ContentLog).filter(
                ContentLog.user_id == user.id
            ).count()
            return total_count >= threshold
        else:
            # Specific module count
            progress = db.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user.id,
                    UserProgress.module == module
                )
            ).first()

            if not progress:
                return False

            return progress.total_attempts >= threshold

    elif criteria_type == "score":
        # Score-based achievements (e.g., "get 90% in grammar")
        if not module:
            return False

        progress = db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user.id,
                UserProgress.module == module
            )
        ).first()

        if not progress or progress.score is None:
            return False

        return progress.score >= threshold

    elif criteria_type == "level_advance":
        # Level advancement achievements
        level_count = db.query(LevelHistory).filter(
            LevelHistory.user_id == user.id
        ).count()

        return level_count >= threshold

    elif criteria_type == "total_xp":
        # Total XP achievements
        return (user.total_xp or 0) >= threshold

    return False


def get_user_achievements(user_id: str, db: Session) -> Dict:
    """
    Get all achievements for a user with unlock status and progress.

    Args:
        user_id: User ID (string/UUID)
        db: Database session

    Returns:
        Dictionary with unlocked and locked achievements, including progress
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"[DEBUG] User not found with id: {user_id}")
        return {"unlocked": [], "locked": []}

    # Get all achievements
    all_achievements = db.query(Achievement).all()

    # Get unlocked achievements
    user_achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id
    ).all()

    unlocked_map = {ua.achievement_id: ua for ua in user_achievements}

    unlocked = []
    locked = []

    for achievement in all_achievements:
        achievement_data = {
            "id": achievement.id,
            "code": achievement.code,
            "name": achievement.name,
            "description": achievement.description,
            "icon": achievement.icon,
            "tier": achievement.tier,
            "xp_reward": achievement.xp_reward,
            "criteria_type": achievement.criteria_type,
            "criteria_threshold": achievement.criteria_threshold,
            "criteria_module": achievement.criteria_module
        }

        if achievement.id in unlocked_map:
            # Unlocked achievement
            ua = unlocked_map[achievement.id]
            achievement_data["unlocked_at"] = ua.unlocked_at.isoformat()
            achievement_data["is_new"] = not ua.is_viewed
            unlocked.append(achievement_data)
        else:
            # Locked achievement - calculate progress
            progress_percent = _calculate_progress(user, achievement, db)
            achievement_data["progress"] = progress_percent
            locked.append(achievement_data)

    # Sort unlocked by date (newest first)
    unlocked.sort(key=lambda x: x["unlocked_at"], reverse=True)

    # Sort locked by progress (closest to unlock first)
    locked.sort(key=lambda x: x["progress"], reverse=True)

    return {
        "unlocked": unlocked,
        "locked": locked,
        "new_count": sum(1 for a in unlocked if a["is_new"])
    }


def _calculate_progress(user: User, achievement: Achievement, db: Session) -> int:
    """
    Calculate progress percentage towards an achievement.

    Args:
        user: User object
        achievement: Achievement object
        db: Database session

    Returns:
        Progress percentage (0-100)
    """
    criteria_type = achievement.criteria_type
    threshold = achievement.criteria_threshold
    module = achievement.criteria_module

    if threshold == 0:
        return 0

    current_value = 0

    if criteria_type == "count":
        if module == "all":
            current_value = db.query(ContentLog).filter(
                ContentLog.user_id == user.id
            ).count()
        else:
            progress = db.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user.id,
                    UserProgress.module == module
                )
            ).first()
            current_value = progress.total_attempts if progress else 0

    elif criteria_type == "score":
        if module:
            progress = db.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user.id,
                    UserProgress.module == module
                )
            ).first()
            current_value = progress.score if progress and progress.score else 0

    elif criteria_type == "level_advance":
        current_value = db.query(LevelHistory).filter(
            LevelHistory.user_id == user.id
        ).count()

    elif criteria_type == "total_xp":
        current_value = user.total_xp or 0

    # Calculate percentage
    progress = min(100, int((current_value / threshold) * 100))
    return progress


def mark_achievements_viewed(user_id: str, db: Session) -> bool:
    """
    Mark all user's achievements as viewed (clear NEW badges).

    Args:
        user_id: User ID
        db: Database session

    Returns:
        True if successful
    """
    user_achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id
    ).all()

    for ua in user_achievements:
        ua.is_viewed = True

    db.commit()
    return True
