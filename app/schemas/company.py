from pydantic import BaseModel
from typing import List
from app.db.models import Company, JobPosting


class JobPostingResponse(BaseModel):
    id: str
    company_id: str
    title: str
    description: str
    created_at: str
    skills_requirements: dict
    wellbeing_preferences: dict
    values_alignment: dict


class CompanyResponse(BaseModel):
    id: str
    name: str
    description: str
    industry: str
    wellbeing_profile: dict
    values_profile: dict
    jobs: List[JobPostingResponse]

    class Config:
        orm_mode = True
