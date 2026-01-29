"""
Pydantic schemas for progress tracking and level advancement.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class ModuleProgress(BaseModel):
    """Progress information for a single module."""
    module: str
    score: Optional[float] = None
    total_attempts: int = 0
    correct_attempts: int = 0
    last_activity: Optional[datetime] = None
    meets_threshold: bool = False  # True if >= 85%
    meets_minimum_attempts: bool = False  # True if >= 10

    class Config:
        from_attributes = True


class ConversationEngagement(BaseModel):
    """Conversation module engagement metrics."""
    total_messages: int = 0
    meets_threshold: bool = False  # True if >= 20

    class Config:
        from_attributes = True


class ProgressSummaryResponse(BaseModel):
    """Complete progress summary for a user."""
    current_level: str  # "B1"
    next_level: Optional[str] = None  # "B2" or None if C2
    can_advance: bool = False
    advancement_reason: Optional[str] = None  # Why can't advance

    overall_progress: float = 0.0  # 0-100
    weighted_score: float = 0.0

    modules: List[ModuleProgress] = []
    conversation_engagement: ConversationEngagement

    time_at_current_level: int = 0  # days
    total_xp: int = 0

    class Config:
        from_attributes = True


class LevelHistoryItem(BaseModel):
    """Historical record of a completed level."""
    level: str
    started_at: datetime
    completed_at: datetime
    days_at_level: int
    weighted_score: float
    scores: Dict[str, Optional[float]]  # Module scores

    class Config:
        from_attributes = True


class AdvancementResponse(BaseModel):
    """Response when user advances to a new level."""
    success: bool
    new_level: str
    old_level: str
    xp_earned: int
    celebration_message: str
    module_scores: Dict[str, Optional[float]]

    class Config:
        from_attributes = True


class ModuleDetailResponse(BaseModel):
    """Detailed progress for a specific module."""
    module: str
    current_score: Optional[float] = None
    total_attempts: int = 0
    correct_attempts: int = 0
    recent_activities: List[Dict] = []
    trend: str = "stable"  # "improving", "stable", "declining"
    recommendations: List[str] = []

    class Config:
        from_attributes = True
