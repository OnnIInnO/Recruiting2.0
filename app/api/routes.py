from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.schemas.models import User, UserCreate
from uuid import UUID

router = APIRouter()

@router.post("/users/", response_model=User)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new user or return existing"""
    return await get_or_create_user(db, user)

@router.get("/jobs/recommended/", response_model=List[Dict])
async def get_recommendations(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get job recommendations for user"""
    return await get_job_recommendations(db, user_id)