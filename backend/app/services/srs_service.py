"""
Spaced Repetition System (SRS) Service
Implements the SM-2 algorithm for vocabulary review scheduling.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.models import VocabularyReview, User


def calculate_sm2(quality: int, easiness_factor: float, repetitions: int, interval: int) -> Dict:
    """
    Calculate next review parameters using the SM-2 algorithm.

    Args:
        quality: User's self-assessed quality of recall (0-5)
                 0 = complete blackout
                 1 = incorrect response; correct one remembered
                 2 = incorrect response; correct one seemed easy to recall
                 3 = correct response recalled with serious difficulty
                 4 = correct response after a hesitation
                 5 = perfect response
        easiness_factor: Current easiness factor (EF)
        repetitions: Current number of consecutive correct repetitions
        interval: Current interval in days

    Returns:
        Dictionary with new EF, repetitions, and interval
    """
    # Update easiness factor
    # EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
    new_ef = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    # Minimum EF is 1.3
    if new_ef < 1.3:
        new_ef = 1.3

    # Update repetitions and interval
    if quality < 3:
        # Incorrect or difficult response - reduce repetitions but don't fully restart
        # This is more forgiving than standard SM-2 for language learning
        new_repetitions = max(0, repetitions - 2)  # Lose 2 levels instead of resetting to 0
        new_interval = 1
    else:
        # Correct response
        new_repetitions = repetitions + 1

        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = round(interval * new_ef)

    return {
        "easiness_factor": round(new_ef, 2),
        "repetitions": new_repetitions,
        "interval": new_interval
    }


def add_word_to_srs(
    db: Session,
    user: User,
    word: str,
    definition: str,
    example_sentence: Optional[str] = None
) -> VocabularyReview:
    """
    Add a new word to the user's SRS review queue.

    Args:
        db: Database session
        user: Current user
        word: The vocabulary word
        definition: Definition in user's native language
        example_sentence: Example sentence using the word

    Returns:
        Created VocabularyReview object
    """
    # Check if word already exists for this user
    existing = db.query(VocabularyReview).filter(
        and_(
            VocabularyReview.user_id == user.id,
            VocabularyReview.word == word,
            VocabularyReview.target_language == user.target_language
        )
    ).first()

    if existing:
        # Update next_review_date to make it due now if it's in the future
        if existing.next_review_date > datetime.now():
            existing.next_review_date = datetime.now()
            db.commit()
        return existing

    # Create new review
    review = VocabularyReview(
        user_id=user.id,
        word=word,
        definition=definition,
        example_sentence=example_sentence,
        target_language=user.target_language,
        easiness_factor=2.5,
        repetitions=0,
        interval=1,
        next_review_date=datetime.now()  # First review immediately (in same session)
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def update_review(
    db: Session,
    review_id: int,
    quality: int
) -> VocabularyReview:
    """
    Update a review after the user has completed it.

    Args:
        db: Database session
        review_id: ID of the review
        quality: Quality rating (0-5)

    Returns:
        Updated VocabularyReview object
    """
    review = db.query(VocabularyReview).filter(VocabularyReview.id == review_id).first()

    if not review:
        raise ValueError(f"Review {review_id} not found")

    # Calculate new parameters using SM-2
    new_params = calculate_sm2(
        quality=quality,
        easiness_factor=review.easiness_factor,
        repetitions=review.repetitions,
        interval=review.interval
    )

    # Update review
    review.easiness_factor = new_params["easiness_factor"]
    review.repetitions = new_params["repetitions"]
    review.interval = new_params["interval"]
    review.next_review_date = datetime.now() + timedelta(days=new_params["interval"])
    review.last_reviewed_at = datetime.now()

    db.commit()
    db.refresh(review)

    return review


def get_due_reviews(db: Session, user: User) -> List[VocabularyReview]:
    """
    Get all reviews that are due for the user.

    Args:
        db: Database session
        user: Current user

    Returns:
        List of due VocabularyReview objects
    """
    return db.query(VocabularyReview).filter(
        and_(
            VocabularyReview.user_id == user.id,
            VocabularyReview.next_review_date <= datetime.now()
        )
    ).order_by(VocabularyReview.next_review_date).all()


def get_review_stats(db: Session, user: User) -> Dict:
    """
    Get statistics about the user's SRS reviews.

    Args:
        db: Database session
        user: Current user

    Returns:
        Dictionary with review statistics
    """
    # Count due reviews
    due_count = db.query(VocabularyReview).filter(
        and_(
            VocabularyReview.user_id == user.id,
            VocabularyReview.next_review_date <= datetime.now()
        )
    ).count()

    # Count learning (repetitions < 5)
    learning_count = db.query(VocabularyReview).filter(
        and_(
            VocabularyReview.user_id == user.id,
            VocabularyReview.repetitions < 5
        )
    ).count()

    # Count mastered (repetitions >= 5)
    mastered_count = db.query(VocabularyReview).filter(
        and_(
            VocabularyReview.user_id == user.id,
            VocabularyReview.repetitions >= 5
        )
    ).count()

    return {
        "due": due_count,
        "learning": learning_count,
        "mastered": mastered_count,
        "total": learning_count + mastered_count
    }


def get_review_by_id(db: Session, review_id: int, user_id: str) -> Optional[VocabularyReview]:
    """
    Get a specific review by ID for a user.

    Args:
        db: Database session
        review_id: Review ID
        user_id: User ID (string/UUID) (for security check)

    Returns:
        VocabularyReview object or None
    """
    return db.query(VocabularyReview).filter(
        and_(
            VocabularyReview.id == review_id,
            VocabularyReview.user_id == user_id
        )
    ).first()
