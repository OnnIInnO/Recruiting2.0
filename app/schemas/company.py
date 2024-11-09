# app/schemas/company.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID


class JobPostingResponse(BaseModel):
    id: UUID
    company_id: UUID
    title: str
    description: Optional[str] = None
    created_at: datetime
    skills_requirements: Optional[Dict] = None
    wellbeing_preferences: Optional[Dict] = None
    values_alignment: Optional[Dict] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={UUID: str, datetime: lambda v: v.isoformat()},
    )


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    wellbeing_profile: Optional[Dict] = None
    values_profile: Optional[Dict] = None
    jobs: List[JobPostingResponse]

    model_config = ConfigDict(from_attributes=True, json_encoders={UUID: str})
