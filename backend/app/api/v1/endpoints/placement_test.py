from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.schemas.placement_test import (
    PlacementTestStartRequest,
    PlacementTestStartResponse,
    PlacementTestQuestionResponse,
    PlacementTestAnswerRequest,
    PlacementTestAnswerResponse,
    PlacementTestResultResponse,
    PlacementTestHistoryResponse,
    PlacementTestHistoryItem
)
from app.services.placement_test_service import (
    start_placement_test,
    get_next_question,
    submit_answer,
    calculate_results,
    get_user_test_history
)

router = APIRouter()


@router.post("/start", response_model=PlacementTestStartResponse)
async def create_placement_test(
    request: PlacementTestStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new placement test.

    Generates all 18 questions (6 vocabulary, 6 grammar, 6 reading) upfront using predefined questions.
    """
    # Create new placement test with all questions
    test = start_placement_test(db, current_user.id, request.target_language)

    questions = test.questions_data.get("questions", [])

    return PlacementTestStartResponse(
        test_id=test.id,
        target_language=test.target_language,
        total_questions=len(questions),
        message=f"Placement test created with {len(questions)} questions. Good luck!"
    )


@router.get("/{test_id}/question", response_model=PlacementTestQuestionResponse)
async def get_question(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the next unanswered question in the test.
    """
    question_data = get_next_question(db, test_id)

    if question_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No more questions available or test not found"
        )

    # Verify the test belongs to the current user
    from app.db.models import PlacementTest
    test = db.query(PlacementTest).filter(PlacementTest.id == test_id).first()
    if test and test.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return PlacementTestQuestionResponse(**question_data)


@router.post("/{test_id}/answer", response_model=PlacementTestAnswerResponse)
async def submit_test_answer(
    test_id: str,
    answer: PlacementTestAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit an answer for a question.
    """
    # Verify the test belongs to the current user
    from app.db.models import PlacementTest
    test = db.query(PlacementTest).filter(PlacementTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )

    if test.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if test.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test is already completed"
        )

    # Submit the answer
    success = submit_answer(db, test_id, answer.question_number, answer.selected_option)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to submit answer"
        )

    # Check if there are more questions
    questions = test.questions_data.get("questions", [])
    answers = test.answers_data.get("answers", {})
    total_questions = len(questions)
    current_number = answer.question_number
    has_next = current_number < total_questions

    return PlacementTestAnswerResponse(
        message="Answer submitted successfully",
        current_question_number=current_number,
        total_questions=total_questions,
        has_next=has_next
    )


@router.post("/{test_id}/complete", response_model=PlacementTestResultResponse)
async def complete_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete the test and calculate results.

    Returns the determined CEFR level and section scores.
    """
    # Verify the test belongs to the current user
    from app.db.models import PlacementTest
    test = db.query(PlacementTest).filter(PlacementTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )

    if test.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if test.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test is already completed"
        )

    # Calculate results
    results = calculate_results(db, test_id)

    if results is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate results"
        )

    return PlacementTestResultResponse(**results)


@router.get("/history", response_model=PlacementTestHistoryResponse)
async def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get placement test history for the current user.
    """
    tests = get_user_test_history(db, current_user.id)

    return PlacementTestHistoryResponse(
        tests=[
            PlacementTestHistoryItem(
                test_id=t.id,
                target_language=t.target_language,
                test_date=t.test_date,
                completed=t.completed,
                determined_level=t.determined_level,
                overall_score=t.overall_score
            )
            for t in tests
        ]
    )
