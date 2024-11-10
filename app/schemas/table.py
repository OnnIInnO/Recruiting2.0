from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from uuid import UUID


class TableRowResponse(BaseModel):
    company_name: str
    company_location: str
    company_logo_url: str
    job_title: str
    apply_link: str
    compatibility_score: float
    wellbeing_score: float
    application_deadline: str
    # New fields
    salary_range: Optional[str] = None
    remote_policy: Optional[str] = None


class TableDataResponse(BaseModel):
    jobs: List[TableRowResponse]
    total: int
