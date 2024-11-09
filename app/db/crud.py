from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime

from app.db.models import User, Company, JobPosting, JobApplication
from app.core.dimensions import AssessmentType


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get user by email address
    Returns None if user doesn't exist
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, name: Optional[str] = None) -> User:
    """
    Create new user
    Returns created user
    """
    user = User(
        email=email,
        name=name or email.split("@")[0],  # Use email prefix as name if not provided
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_user(
    db: AsyncSession, email: str, name: Optional[str] = None
) -> User:
    """
    Get existing user or create new one
    Returns user
    """
    user = await get_user_by_email(db, email)
    if not user:
        user = await create_user(db, email, name)
    return user


async def update_user_assessment(
    db: AsyncSession, user_id: UUID, assessment_type: AssessmentType, profile_data: Dict
) -> User:
    """
    Update user's assessment profile
    Returns updated user
    """
    user = await db.get(User, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    # Update appropriate profile based on assessment type
    if assessment_type == AssessmentType.WELLBEING:
        user.wellbeing_profile = profile_data
    elif assessment_type == AssessmentType.SKILLS:
        user.skills_profile = profile_data
    elif assessment_type == AssessmentType.VALUES:
        user.values_profile = profile_data

    await db.commit()
    await db.refresh(user)
    return user


async def get_user_applications(
    db: AsyncSession, user_id: UUID
) -> List[JobApplication]:
    """
    Get all job applications for a user
    Returns list of applications with job and company data
    """
    result = await db.execute(
        select(JobApplication)
        .options(joinedload(JobApplication.job).joinedload(JobPosting.company))
        .where(JobApplication.user_id == user_id)
        .order_by(JobApplication.created_at.desc())
    )
    return result.scalars().all()


async def get_active_jobs(
    db: AsyncSession, skip: int = 0, limit: int = 50
) -> List[JobPosting]:
    """
    Get active job postings with company data
    Returns list of jobs
    """
    result = await db.execute(
        select(JobPosting)
        .options(joinedload(JobPosting.company))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_job_application(
    db: AsyncSession, user_id: UUID, job_id: UUID, match_scores: Dict
) -> JobApplication:
    """
    Create new job application
    Returns created application
    """
    application = JobApplication(
        user_id=user_id,
        job_id=job_id,
        skills_match=match_scores.get("skills_match", 0),
        wellbeing_match=match_scores.get("wellbeing_match", 0),
        values_match=match_scores.get("values_match", 0),
        overall_match=match_scores.get("overall_match", 0),
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


async def get_company_by_id(db: AsyncSession, company_id: UUID) -> Optional[Company]:
    """
    Get company by ID with related data
    Returns None if company doesn't exist
    """
    result = await db.execute(
        select(Company)
        .where(Company.id == company_id)
    )
    return result.scalar_one_or_none()


async def get_job_posting(db: AsyncSession, job_id: UUID) -> Optional[JobPosting]:
    """
    Get job posting by ID with company data
    Returns None if job doesn't exist
    """
    result = await db.execute(
        select(JobPosting)
        .options(joinedload(JobPosting.company))
        .where(JobPosting.id == job_id)
    )
    return result.scalar_one_or_none()


async def get_application_stats(db: AsyncSession, job_id: UUID) -> Dict:
    """
    Get application statistics for a job posting
    Returns dict with stats
    """
    result = await db.execute(
        select(JobApplication).where(JobApplication.job_id == job_id)
    )
    applications = result.scalars().all()

    total = len(applications)
    if total == 0:
        return {"total_applications": 0, "average_match": 0, "high_match_count": 0}

    matches = [app.overall_match for app in applications]
    high_matches = sum(1 for m in matches if m >= 0.8)

    return {
        "total_applications": total,
        "average_match": sum(matches) / total,
        "high_match_count": high_matches,
    }


async def get_application(
    db: AsyncSession, user_id: UUID, job_id: UUID
) -> Optional[JobApplication]:
    """Get existing application"""
    result = await db.execute(
        select(JobApplication).where(
            JobApplication.user_id == user_id, JobApplication.job_id == job_id
        )
    )
    return result.scalar_one_or_none()


async def create_application(
    db: AsyncSession,
    user_id: UUID,
    job_id: UUID,
    match_scores: Dict,
) -> JobApplication:
    """Create new job application"""
    application = JobApplication(
        user_id=user_id,
        job_id=job_id,
        match_scores=match_scores,
        status="pending",
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


async def get_company_applications(
    db: AsyncSession, company_id: UUID
) -> List[JobApplication]:
    """Get all applications for a company's jobs"""
    result = await db.execute(
        select(JobApplication)
        .join(JobPosting)
        .options(joinedload(JobApplication.user), joinedload(JobApplication.job))
        .where(JobPosting.company_id == company_id)
        .order_by(JobApplication.created_at.desc())
    )
    return result.scalars().all()
