from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: UUID
    created_at: datetime
    wellbeing_profile: Optional[Dict] = None
    skills_profile: Optional[Dict] = None
    values_profile: Optional[Dict] = None

    class Config:
        from_attributes = True