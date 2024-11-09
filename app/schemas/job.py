from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class JobApplication(BaseModel):
    cover_letter: Optional[str] = None


class JobMatch(BaseModel):
    overall_match: float
    skills_match: Optional[float] = None
    wellbeing_match: Optional[float] = None
    values_match: Optional[float] = None
    matched_dimensions: list[str]
