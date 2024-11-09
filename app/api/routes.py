from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime

from app.db.database import get_db
from app.db.models import User, JobPosting, Company, JobApplication
from app.core.dimensions import AssessmentDimensions, AssessmentType
from app.core.matching import MatchingSystem
from app.schemas.assessment import (
    AssessmentResponse,
    QuestionResponse,
    ProfileResponse,
    MatchResponse
)

router = APIRouter()
matching_system = MatchingSystem()

# Assessment routes
@router.get("/assessments/{assessment_type}/questions", response_model=List[QuestionResponse])
async def get_assessment_questions(
    assessment_type: AssessmentType
):
    """Get questions for specific assessment type"""
    try:
        questions = AssessmentDimensions.get_questions(assessment_type)
        return [
            QuestionResponse(
                id=f"{assessment_type}_{idx}",
                dimension=q["dimension"],
                dimension_title=q["dimension_title"],
                question_text=q["question"],
                theory=q["theory"]
            ) for idx, q in enumerate(questions)
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/assessments/{assessment_type}/submit")
async def submit_assessment(
    assessment_type: AssessmentType,
    answers: Dict[str, int],
    user_email: str,
    db: AsyncSession = Depends(get_db)
):
    """Submit assessment answers and get recommendations"""
    # Get or create user
    user = await get_or_create_user(db, user_email)
    
    # Process answers and generate profile
    profile = process_assessment_answers(assessment_type, answers)
    
    # Update user profile
    await update_user_profile(db, user.id, assessment_type, profile)
    
    # Get recommendations if all assessments completed
    recommendations = None
    if await check_all_assessments_completed(db, user.id):
        recommendations = await get_user_recommendations(db, user.id)
    
    return {
        "profile": profile,
        "recommendations": recommendations,
        "assessment_status": await get_assessment_status(db, user.id)
    }

@router.get("/users/{user_email}/assessment-status")
async def get_user_assessment_status(
    user_email: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user's assessment completion status"""
    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return await get_assessment_status(db, user.id)

@router.get("/users/{user_email}/profile", response_model=ProfileResponse)
async def get_user_profile(
    user_email: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user's complete profile with all assessment results"""
    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return ProfileResponse(
        email=user.email,
        wellbeing_profile=user.wellbeing_profile,
        skills_profile=user.skills_profile,
        values_profile=user.values_profile,
        assessment_status=await get_assessment_status(db, user.id)
    )

@router.get("/users/{user_email}/recommendations")
async def get_user_recommendations(
    user_email: str,
    db: AsyncSession = Depends(get_db)
):
    """Get job recommendations for user"""
    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not await check_all_assessments_completed(db, user.id):
        raise HTTPException(
            status_code=400,
            detail="Please complete all assessments first"
        )
    
    recommendations = await get_user_recommendations(db, user.id)
    return recommendations

# Helper functions
async def get_or_create_user(
    db: AsyncSession,
    email: str
) -> User:
    """Get existing user or create new one"""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    return user

async def update_user_profile(
    db: AsyncSession,
    user_id: UUID,
    assessment_type: AssessmentType,
    profile: Dict
):
    """Update user's assessment profile"""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if assessment_type == AssessmentType.WELLBEING:
        user.wellbeing_profile = profile
    elif assessment_type == AssessmentType.SKILLS:
        user.skills_profile = profile
    elif assessment_type == AssessmentType.VALUES:
        user.values_profile = profile
    
    await db.commit()
    await db.refresh(user)

async def check_all_assessments_completed(
    db: AsyncSession,
    user_id: UUID
) -> bool:
    """Check if user has completed all assessments"""
    user = await db.get(User, user_id)
    return all([
        user.wellbeing_profile,
        user.skills_profile,
        user.values_profile
    ])

async def get_assessment_status(
    db: AsyncSession,
    user_id: UUID
) -> Dict[str, bool]:
    """Get status of each assessment"""
    user = await db.get(User, user_id)
    return {
        "wellbeing": bool(user.wellbeing_profile),
        "skills": bool(user.skills_profile),
        "values": bool(user.values_profile)
    }

async def get_user_recommendations(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 10
) -> List[Dict]:
    """Get job recommendations for user"""
    # Get user profiles
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all active jobs with company profiles
    jobs_result = await db.execute(
        select(JobPosting, Company)
        .join(Company)
        .where(JobPosting.company_id == Company.id)
    )
    jobs = jobs_result.all()
    
    # Calculate matches
    job_matches = []
    for job, company in jobs:
        match_score = matching_system.calculate_match(
            {
                'wellbeing_profile': user.wellbeing_profile,
                'skills_profile': user.skills_profile,
                'values_profile': user.values_profile
            },
            {
                'skills_requirements': job.skills_requirements,
                'wellbeing_preferences': job.wellbeing_preferences,
                'values_alignment': job.values_alignment
            },
            {
                'wellbeing_profile': company.wellbeing_profile,
                'values_profile': company.values_profile
            }
        )
        
        job_matches.append({
            'job': {
                'id': job.id,
                'title': job.title,
                'company': company.name,
                'description': job.description
            },
            'match_score': match_score
        })
    
    # Sort by match score and return top matches
    job_matches.sort(key=lambda x: x['match_score']['overall_match'], reverse=True)
    return job_matches[:limit]

def process_assessment_answers(
    assessment_type: AssessmentType,
    answers: Dict[str, int]
) -> Dict:
    """Process raw assessment answers into dimension scores"""
    dimensions = AssessmentDimensions.get_dimensions(assessment_type)
    
    # Group answers by dimension
    dimension_answers = {}
    for dimension in dimensions:
        dimension_answers[dimension] = []
    
    for question_id, score in answers.items():
        # Extract dimension from question_id (format: "dimension_idx")
        dimension = question_id.split('_')[0]
        if dimension in dimensions:
            dimension_answers[dimension].append(score)
    
    # Calculate dimension scores
    profile = {}
    for dimension, scores in dimension_answers.items():
        if scores:
            avg_score = sum(scores) / len(scores)
            profile[dimension] = {
                'score': avg_score,
                'title': dimensions[dimension]['title'],
                'description': dimensions[dimension]['description']
            }
    
    return profile