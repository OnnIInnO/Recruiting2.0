from pydantic import BaseModel
from datetime import date
from typing import List


class TableRowResponse(BaseModel):
    company_name: str
    company_location: str  # Placeholder
    company_logo_url: str  # Placeholder
    job_title: str
    apply_link: str  # Will be job.id
    compatibility_score: float
    wellbeing_score: float
    application_deadline: str  # Placeholder
