from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional
from uuid import UUID
from enum import Enum


class QuestionResponse(BaseModel):
    """Schema for assessment question"""

    id: str
    dimension: str
    dimension_title: str
    question_text: str
    theory: str


class AssessmentResponse(BaseModel):
    """Schema for assessment submission"""

    answers: Dict[str, int]


class AssessmentStatus(BaseModel):
    """Schema for assessment completion status"""

    wellbeing: bool
    skills: bool
    values: bool


class ProfileResponse(BaseModel):
    """Schema for user profile"""

    email: str
    wellbeing_profile: Optional[Dict] = None
    skills_profile: Optional[Dict] = None
    values_profile: Optional[Dict] = None
    assessment_status: Dict[str, bool]

    class Config:
        from_attributes = True


class MatchScore(BaseModel):
    """Schema for individual dimension match"""

    score: float
    title: str
    description: str


class MatchResponse(BaseModel):
    """Schema for overall match results"""

    overall_match: float
    skills_match: Optional[Dict[str, MatchScore]] = None
    wellbeing_match: Optional[Dict[str, MatchScore]] = None
    values_match: Optional[Dict[str, MatchScore]] = None
    insights: List[str] = []

    class Config:
        from_attributes = True
