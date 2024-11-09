# app/api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Optional
from uuid import UUID
from app.db.models import Company, JobPosting, User  # Add this with the other imports
from sqlalchemy.orm import selectinload

# Add these imports to the top of routes.py
from app.schemas.company import CompanyResponse
from app.schemas.user import (
    UserCreate,
    UserResponse,
)  # You'll need to create these schemas
from app.schemas.job import (
    JobMatch,
    JobApplication,
)  # You'll need to create these schemas
from datetime import datetime


from app.db.database import get_db
from app.db.crud import (
    create_application,
    get_application,
    get_user_by_email,
    get_or_create_user,
    update_user_assessment,
    get_active_jobs,
    get_job_posting,
    get_company_by_id,
)
from sqlalchemy.util._concurrency_py3k import greenlet_spawn
from app.core.dimensions import AssessmentDimensions, AssessmentType
from app.core.matching import MatchingSystem
from app.schemas.assessment import (
    AssessmentResponse,
    QuestionResponse,
    ProfileResponse,
    MatchResponse,
)

from app.db.seed import seed_data

seed_router = APIRouter()


@seed_router.post("/seed-data")
async def load_seed_data(db: AsyncSession = Depends(get_db)):
    """Load initial seed data into the database"""
    await seed_data(db)
    return {"message": "Seed data loaded successfully"}


router = APIRouter()
matching_system = MatchingSystem()


@router.get("/companies", response_model=List[CompanyResponse])
async def get_all_companies(db: AsyncSession = Depends(get_db)):
    """Get a list of all companies and their job postings"""
    query = select(Company).options(selectinload(Company.jobs))
    result = await db.execute(query)
    companies = result.scalars().all()
    return companies


@router.get(
    "/assessments/{assessment_type}/questions", response_model=List[QuestionResponse]
)
async def get_assessment_questions(assessment_type: AssessmentType):
    """Get questions for specific assessment type"""
    try:
        questions = AssessmentDimensions.get_questions(assessment_type)
        return [
            QuestionResponse(
                id=f"{assessment_type}_{idx}",
                dimension=q["dimension"],
                dimension_title=q["dimension_title"],
                question_text=q["question"],
                theory=q["theory"],
            )
            for idx, q in enumerate(questions)
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assessments/{assessment_type}/submit")
async def submit_assessment(
    assessment_type: AssessmentType,
    answers: Dict[str, int],
    user_email: str,
    db: AsyncSession = Depends(get_db),
):
    """Submit assessment answers and get recommendations"""
    # Get or create user
    user = await get_or_create_user(db, user_email)

    # Process answers and generate profile
    profile = process_assessment_answers(assessment_type, answers)

    # Update user profile
    await update_user_assessment(db, user.id, assessment_type, profile)

    # Get recommendations based on completed assessments
    recommendations = await get_user_recommendations(db, user.id)

    return {
        "profile": profile,
        "recommendations": recommendations,
        "assessment_status": get_assessment_status(user),
    }


@router.get("/users/{user_email}/assessment-status")
async def get_user_assessment_status(
    user_email: str, db: AsyncSession = Depends(get_db)
):
    """Get user's assessment completion status"""
    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_assessment_status(user)


@router.get("/users/{user_email}/profile", response_model=ProfileResponse)
async def get_user_profile(user_email: str, db: AsyncSession = Depends(get_db)):
    """Get user's complete profile with all assessment results"""
    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return ProfileResponse(
        email=user.email,
        wellbeing_profile=user.wellbeing_profile,
        skills_profile=user.skills_profile,
        values_profile=user.values_profile,
        assessment_status=get_assessment_status(user),
    )


@router.get("/users/{user_email}/recommendations")
async def get_user_recommendations_route(
    user_email: str, db: AsyncSession = Depends(get_db)
):
    """Get job recommendations for user based on completed assessments"""
    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not has_any_assessment(user):
        raise HTTPException(
            status_code=400, detail="Please complete at least one assessment first"
        )

    recommendations = await get_user_recommendations(db, user.id)
    return recommendations


# Helper functions
def get_assessment_status(user: "User") -> Dict[str, bool]:
    """Get status of each assessment"""
    return {
        "wellbeing": bool(user.wellbeing_profile),
        "skills": bool(user.skills_profile),
        "values": bool(user.values_profile),
    }


def has_any_assessment(user: "User") -> bool:
    """Check if user has completed any assessment"""
    return any([user.wellbeing_profile, user.skills_profile, user.values_profile])


def get_completed_profiles(user: "User") -> Dict[str, Dict]:
    """Get only completed assessment profiles"""
    profiles = {}
    if user.wellbeing_profile:
        profiles["wellbeing_profile"] = user.wellbeing_profile
    if user.skills_profile:
        profiles["skills_profile"] = user.skills_profile
    if user.values_profile:
        profiles["values_profile"] = user.values_profile
    return profiles


async def get_user_recommendations(
    db: AsyncSession, user_id: UUID, limit: int = 10
) -> List[Dict]:
    """Get job recommendations based on completed assessments"""
    # Get user
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get completed profiles
    completed_profiles = get_completed_profiles(user)
    if not completed_profiles:
        return []

    # Get all active jobs
    jobs = await get_active_jobs(db)

    # Calculate matches based on completed assessments
    job_matches = []
    for job in jobs:
        # Get company data
        company = await get_company_by_id(db, job.company_id)

        # Prepare job requirements based on completed assessments
        job_requirements = {}
        if "skills_profile" in completed_profiles and job.skills_requirements:
            job_requirements["skills_requirements"] = job.skills_requirements
        if "wellbeing_profile" in completed_profiles and job.wellbeing_preferences:
            job_requirements["wellbeing_preferences"] = job.wellbeing_preferences
        if "values_profile" in completed_profiles and job.values_alignment:
            job_requirements["values_alignment"] = job.values_alignment

        # Prepare company profiles based on completed assessments
        company_profiles = {}
        if "wellbeing_profile" in completed_profiles and company.wellbeing_profile:
            company_profiles["wellbeing_profile"] = company.wellbeing_profile
        if "values_profile" in completed_profiles and company.values_profile:
            company_profiles["values_profile"] = company.values_profile

        # Calculate match score
        match_score = matching_system.calculate_match(
            completed_profiles, job_requirements, company_profiles
        )

        job_matches.append(
            {
                "job": {
                    "id": job.id,
                    "title": job.title,
                    "company": company.name,
                    "description": job.description,
                },
                "match_score": match_score,
                "matched_dimensions": list(
                    completed_profiles.keys()
                ),  # Include which dimensions were matched
            }
        )

    # Sort by match score and return top matches
    job_matches.sort(key=lambda x: x["match_score"]["overall_match"], reverse=True)
    return job_matches[:limit]


def process_assessment_answers(
    assessment_type: AssessmentType, answers: Dict[str, int]
) -> Dict:
    """Process raw assessment answers into dimension scores"""
    dimensions = AssessmentDimensions.get_dimensions(assessment_type)

    # Group answers by dimension
    dimension_answers = {}
    for dimension in dimensions:
        dimension_answers[dimension] = []

    for question_id, score in answers.items():
        # Extract dimension from question_id
        dimension = question_id.split("_")[0]
        if dimension in dimensions:
            dimension_answers[dimension].append(score)

    # Calculate dimension scores
    profile = {}
    for dimension, scores in dimension_answers.items():
        if scores:
            avg_score = sum(scores) / len(scores)
            profile[dimension] = {
                "score": avg_score,
                "title": dimensions[dimension]["title"],
                "description": dimensions[dimension]["description"],
            }

    return profile


# User Management Routes
@router.post("/users/", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        return existing_user

    user = await get_or_create_user(db, user_data.email, user_data.name)
    return user


@router.get("/users/{user_email}", response_model=UserResponse)
async def get_user(user_email: str, db: AsyncSession = Depends(get_db)):
    """Get user details"""
    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Matching Routes
@router.get("/jobs/{job_id}/match/{user_email}")
async def get_job_match(
    job_id: UUID, user_email: str, db: AsyncSession = Depends(get_db)
):
    """Get detailed match information for a specific job"""
    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    job = await get_job_posting(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    company = await get_company_by_id(db, job.company_id)

    # Get completed profiles
    completed_profiles = get_completed_profiles(user)
    if not completed_profiles:
        raise HTTPException(
            status_code=400, detail="Please complete at least one assessment first"
        )

    # Calculate match
    match_score = matching_system.calculate_match(
        completed_profiles,
        {
            "skills_requirements": job.skills_requirements,
            "wellbeing_preferences": job.wellbeing_preferences,
            "values_alignment": job.values_alignment,
        },
        {
            "wellbeing_profile": company.wellbeing_profile,
            "values_profile": company.values_profile,
        },
    )

    return {
        "job": {
            "id": job.id,
            "title": job.title,
            "company": company.name,
            "description": job.description,
        },
        "match_score": match_score,
        "matched_dimensions": list(completed_profiles.keys()),
    }


# Job Application Routes
@router.post("/jobs/{job_id}/apply")
async def apply_to_job(
    job_id: UUID,
    user_email: str,
    application_data: JobApplication,
    db: AsyncSession = Depends(get_db),
):
    """Apply to a specific job"""
    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    job = await get_job_posting(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if already applied
    existing_application = await get_application(db, user.id, job_id)
    if existing_application:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    # Calculate match score
    completed_profiles = get_completed_profiles(user)
    company = await get_company_by_id(db, job.company_id)

    match_score = matching_system.calculate_match(
        completed_profiles,
        {
            "skills_requirements": job.skills_requirements,
            "wellbeing_preferences": job.wellbeing_preferences,
            "values_alignment": job.values_alignment,
        },
        {
            "wellbeing_profile": company.wellbeing_profile,
            "values_profile": company.values_profile,
        },
    )

    # Create application
    application = await create_application(
        db,
        user_id=user.id,
        job_id=job_id,
        match_scores=match_score,
        cover_letter=application_data.cover_letter,
    )

    return {
        "application_id": application.id,
        "match_score": match_score,
        "status": "submitted",
    }


@router.get("/users/{user_email}/applications")
async def get_user_applications(user_email: str, db: AsyncSession = Depends(get_db)):
    """Get all applications for a user"""
    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    applications = await get_user_applications(db, user.id)

    return [
        {
            "id": app.id,
            "job": {
                "id": app.job.id,
                "title": app.job.title,
                "company": app.job.company.name,
            },
            "status": app.status,
            "match_score": app.match_scores,
            "created_at": app.created_at,
        }
        for app in applications
    ]


# Company View Routes (if needed)
@router.get("/companies/{company_id}/applications")
async def get_company_applications(
    company_id: UUID, db: AsyncSession = Depends(get_db)
):
    """Get all applications for a company's jobs"""
    applications = await get_company_applications(db, company_id)

    # Group by job and sort by match score
    jobs_applications = {}
    for app in applications:
        if app.job.id not in jobs_applications:
            jobs_applications[app.job.id] = {
                "job": {"id": app.job.id, "title": app.job.title},
                "applications": [],
            }

        jobs_applications[app.job.id]["applications"].append(
            {
                "id": app.id,
                "applicant": {"email": app.user.email, "name": app.user.name},
                "match_score": app.match_scores,
                "status": app.status,
                "created_at": app.created_at,
            }
        )

    return jobs_applications


# Matching Insights Routes
@router.get("/users/{user_email}/matching-insights")
async def get_user_matching_insights(
    user_email: str, db: AsyncSession = Depends(get_db)
):
    """Get detailed matching insights for a user"""
    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    completed_profiles = get_completed_profiles(user)
    if not completed_profiles:
        raise HTTPException(
            status_code=400, detail="Please complete at least one assessment first"
        )

    # Get all jobs and calculate matches
    jobs = await get_active_jobs(db)
    matches = []

    for job in jobs:
        company = await get_company_by_id(db, job.company_id)
        match_score = matching_system.calculate_match(
            completed_profiles,
            {
                "skills_requirements": job.skills_requirements,
                "wellbeing_preferences": job.wellbeing_preferences,
                "values_alignment": job.values_alignment,
            },
            {
                "wellbeing_profile": company.wellbeing_profile,
                "values_profile": company.values_profile,
            },
        )
        matches.append({"match_score": match_score, "job_type": job.title})

    # Calculate insights
    insights = {
        "best_matches": sorted(
            matches, key=lambda x: x["match_score"]["overall_match"], reverse=True
        )[:3],
        "completed_assessments": list(completed_profiles.keys()),
        "strongest_dimensions": get_strongest_dimensions(completed_profiles),
        "improvement_areas": get_improvement_areas(completed_profiles),
    }

    return insights


# Helper function for insights
def get_strongest_dimensions(profiles: Dict) -> List[Dict]:
    """Get user's strongest dimensions across all profiles"""
    strong_dimensions = []

    for profile_type, profile in profiles.items():
        for dimension, data in profile.items():
            if data.get("score", 0) > 7:  # Consider scores > 7 as strong
                strong_dimensions.append(
                    {
                        "dimension": dimension,
                        "profile_type": profile_type,
                        "score": data["score"],
                        "title": data["title"],
                    }
                )

    return sorted(strong_dimensions, key=lambda x: x["score"], reverse=True)[:5]


def get_improvement_areas(profiles: Dict) -> List[Dict]:
    """Get areas where user might want to improve"""
    improvement_areas = []

    for profile_type, profile in profiles.items():
        for dimension, data in profile.items():
            if (
                data.get("score", 10) < 6
            ):  # Consider scores < 6 as areas for improvement
                improvement_areas.append(
                    {
                        "dimension": dimension,
                        "profile_type": profile_type,
                        "score": data["score"],
                        "title": data["title"],
                    }
                )

    return sorted(improvement_areas, key=lambda x: x["score"])[:5]
