# app/api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Optional
from uuid import UUID

from app.db.database import get_db
from app.db.crud import (
    get_user_by_email,
    get_or_create_user,
    update_user_assessment,
    get_active_jobs,
    get_job_posting,
    get_company_by_id,
)
from app.core.dimensions import AssessmentDimensions, AssessmentType
from app.core.matching import MatchingSystem
from app.schemas.assessment import (
    AssessmentResponse,
    QuestionResponse,
    ProfileResponse,
    MatchResponse,
)

router = APIRouter()
matching_system = MatchingSystem()


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
