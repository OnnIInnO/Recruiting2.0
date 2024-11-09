from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: str
    name: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None

    class Config:
        from_attributes = True
