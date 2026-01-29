from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PlacementTestStartRequest(BaseModel):
    """Request to start a placement test."""
    target_language: str = Field(..., min_length=2, max_length=50)


class PlacementTestQuestion(BaseModel):
    """A single placement test question."""
    question_number: int
    question_text: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    section: str  # "vocabulary", "grammar", or "reading"
    difficulty_level: str  # "A1", "A2", "B1", "B2", "C1", "C2"
    passage: Optional[str] = None  # For reading comprehension questions


class PlacementTestStartResponse(BaseModel):
    """Response after starting a placement test."""
    test_id: str
    target_language: str
    total_questions: int
    message: str


class PlacementTestQuestionResponse(BaseModel):
    """Response containing the next question."""
    test_id: str
    question: PlacementTestQuestion
    current_question_number: int
    total_questions: int
    has_next: bool


class PlacementTestAnswerRequest(BaseModel):
    """Request to submit an answer."""
    question_number: int
    selected_option: int = Field(..., ge=0, le=3)  # 0-3 for options A-D


class PlacementTestAnswerResponse(BaseModel):
    """Response after submitting an answer."""
    message: str
    current_question_number: int
    total_questions: int
    has_next: bool


class PlacementTestSectionScore(BaseModel):
    """Score breakdown for a test section."""
    section: str
    score_percentage: float
    correct_answers: int
    total_questions: int


class PlacementTestResultResponse(BaseModel):
    """Response with test results."""
    test_id: str
    overall_score: float
    determined_level: str
    section_scores: List[PlacementTestSectionScore]
    recommendations: List[str]
    completed_at: datetime

    class Config:
        from_attributes = True


class PlacementTestHistoryItem(BaseModel):
    """A single placement test history entry."""
    test_id: str
    target_language: str
    test_date: datetime
    completed: bool
    determined_level: Optional[str] = None
    overall_score: Optional[float] = None

    class Config:
        from_attributes = True


class PlacementTestHistoryResponse(BaseModel):
    """Response containing user's placement test history."""
    tests: List[PlacementTestHistoryItem]
