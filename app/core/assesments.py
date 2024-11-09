from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

class QuestionResponse(BaseModel):
    """Schema for assessment question"""
    id: str
    dimension: str
    dimension_title: str
    question_text: str
    theory: str

class AssessmentResponse(BaseModel):
    """Schema for assessment submission"""
    answers: Dict[str, int]  # question_id -> score

class ProfileResponse(BaseModel):
    """Schema for user profile"""
    email: EmailStr
    wellbeing_profile: Optional[Dict] = None
    skills_profile: Optional[Dict] = None
    values_profile: Optional[Dict] = None
    assessment_status: Dict[str, bool]

class DimensionMatch(BaseModel):
    """Schema for dimension match details"""
    match: float
    title: str
    description: str

class MatchResponse(BaseModel):
    """Schema for match results"""
    overall_match: float
    skills_match: Dict[str, DimensionMatch]
    wellbeing_match: Dict[str, DimensionMatch]
    values_match: Dict[str, DimensionMatch]
    insights: List[str]

class JobRecommendation(BaseModel):
    """Schema for job recommendation"""
    job: Dict
    match_score: MatchResponse   