from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional


class UserCreate(BaseModel):
    email: str
    name: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID4
    email: str
    name: Optional[str] = None

    class Config:
        orm_mode = True
