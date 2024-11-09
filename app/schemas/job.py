from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime


class JobApplicationBase(BaseModel):
    user_id: UUID4
    job_id: UUID4


class JobApplicationCreate(JobApplicationBase):
    pass


class JobApplication(JobApplicationBase):
    id: UUID4
    created_at: datetime
    status: str
    skills_match: float
    wellbeing_match: float
    values_match: float
    overall_match: float

    class Config:
        orm_mode = True


class JobMatch(BaseModel):
    overall_match: float
    skills_match: Optional[float] = None
    wellbeing_match: Optional[float] = None
    values_match: Optional[float] = None
    matched_dimensions: list[str]
