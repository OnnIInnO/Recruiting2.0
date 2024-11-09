from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Company, JobPosting
from app.core.dimensions import AssessmentDimensions, AssessmentType
import json
import uuid
from app.db.database import get_db
import asyncio


async def seed_data(db: AsyncSession):
    """Seed initial data for development"""

    # Create example companies
    companies = [
        {
            "id": str(uuid.UUID(int=1)),
            "name": "Tech Innovators",
            "description": "Leading software development company",
            "industry": "Technology",
            "wellbeing_profile": {
                "AUTONOMY": {"score": 8.5},
                "MASTERY": {"score": 9.0},
                "WORK_LIFE": {"score": 8.0},
            },
            "values_profile": {
                "INNOVATION": {"score": 9.0},
                "SUSTAINABILITY": {"score": 7.5},
                "GROWTH": {"score": 8.5},
            },
        },
        {
            "id": str(uuid.UUID(int=2)),
            "name": "Green Future",
            "description": "Sustainable energy solutions",
            "industry": "Energy",
            "wellbeing_profile": {
                "AUTONOMY": {"score": 7.5},
                "MASTERY": {"score": 8.0},
                "WORK_LIFE": {"score": 9.0},
            },
            "values_profile": {
                "SUSTAINABILITY": {"score": 9.5},
                "IMPACT": {"score": 9.0},
                "ETHICS": {"score": 8.5},
            },
        },
        {
            "id": str(uuid.UUID(int=3)),
            "name": "Welmo Health Solutions",
            "description": "Leading provider of health and well-being services, focused on promoting mental wellness and work-life balance.",
            "industry": "Healthcare",
            "wellbeing_profile": {
                "AUTONOMY": {"score": 8},
                "MASTERY": {"score": 7},
                "RELATEDNESS": {"score": 9},
                "WORK_LIFE": {"score": 10},
                "PURPOSE": {"score": 9},
                "PSYCHOLOGICAL_SAFETY": {"score": 9},
            },
            "values_profile": {
                "INNOVATION": {"score": 6},
                "SUSTAINABILITY": {"score": 8},
                "DIVERSITY": {"score": 9},
                "ETHICS": {"score": 10},
                "GROWTH": {"score": 7},
                "IMPACT": {"score": 9},
            },
        },
        {
            "id": str(uuid.UUID(int=4)),
            "name": "TechNova Innovations",
            "description": "Tech company committed to driving innovation and supporting a diverse, inclusive work environment.",
            "industry": "Technology",
            "wellbeing_profile": {
                "AUTONOMY": {"score": 9},
                "MASTERY": {"score": 8},
                "RELATEDNESS": {"score": 7},
                "WORK_LIFE": {"score": 6},
                "PURPOSE": {"score": 8},
                "PSYCHOLOGICAL_SAFETY": {"score": 8},
            },
            "values_profile": {
                "INNOVATION": {"score": 10},
                "SUSTAINABILITY": {"score": 7},
                "DIVERSITY": {"score": 9},
                "ETHICS": {"score": 8},
                "GROWTH": {"score": 8},
                "IMPACT": {"score": 7},
            },
        },
        {
            "id": str(uuid.UUID(int=5)),
            "name": "GreenPath Financial",
            "description": "A finance company promoting mental resilience, integrity, and sustainability within the workplace.",
            "industry": "Finance",
            "wellbeing_profile": {
                "AUTONOMY": {"score": 5},
                "MASTERY": {"score": 8},
                "RELATEDNESS": {"score": 6},
                "WORK_LIFE": {"score": 7},
                "PURPOSE": {"score": 9},
                "PSYCHOLOGICAL_SAFETY": {"score": 7},
            },
            "values_profile": {
                "INNOVATION": {"score": 5},
                "SUSTAINABILITY": {"score": 10},
                "DIVERSITY": {"score": 6},
                "ETHICS": {"score": 9},
                "GROWTH": {"score": 8},
                "IMPACT": {"score": 6},
            },
        },
        {
            "id": str(uuid.UUID(int=6)),
            "name": "EcoWave Solutions",
            "description": "Environmental consulting firm prioritizing employee well-being and sustainable practices.",
            "industry": "Environmental Consulting",
            "wellbeing_profile": {
                "AUTONOMY": {"score": 7},
                "MASTERY": {"score": 9},
                "RELATEDNESS": {"score": 8},
                "WORK_LIFE": {"score": 9},
                "PURPOSE": {"score": 10},
                "PSYCHOLOGICAL_SAFETY": {"score": 8},
            },
            "values_profile": {
                "INNOVATION": {"score": 8},
                "SUSTAINABILITY": {"score": 10},
                "DIVERSITY": {"score": 8},
                "ETHICS": {"score": 9},
                "GROWTH": {"score": 9},
                "IMPACT": {"score": 10},
            },
        },
        {
            "id": str(uuid.UUID(int=7)),
            "name": "FutureWork Labs",
            "description": "AI and machine learning company creating future-proof career paths with a focus on growth and adaptability.",
            "industry": "Artificial Intelligence",
            "wellbeing_profile": {
                "AUTONOMY": {"score": 10},
                "MASTERY": {"score": 8},
                "RELATEDNESS": {"score": 6},
                "WORK_LIFE": {"score": 7},
                "PURPOSE": {"score": 9},
                "PSYCHOLOGICAL_SAFETY": {"score": 8},
            },
            "values_profile": {
                "INNOVATION": {"score": 10},
                "SUSTAINABILITY": {"score": 6},
                "DIVERSITY": {"score": 7},
                "ETHICS": {"score": 8},
                "GROWTH": {"score": 10},
                "IMPACT": {"score": 7},
            },
        },
    ]

    # Create example job_positngs
    job_postings = [
        # Tech Innovators
        {
            "id": str(uuid.UUID(int=8)),
            "company_id": str(uuid.UUID(int=1)),
            "title": "Software Engineer",
            "description": "Develop and maintain software applications with a focus on scalability and efficiency.",
            "skills_requirements": {
                "TECHNICAL": {"score": 8},
                "PROBLEM_SOLVING": {"score": 9},
                "COMMUNICATION": {"score": 7},
            },
            "wellbeing_preferences": {
                "AUTONOMY": {"score": 8},
                "MASTERY": {"score": 9},
                "WORK_LIFE": {"score": 8},
            },
            "values_alignment": {
                "INNOVATION": {"score": 9},
                "GROWTH": {"score": 8},
                "SUSTAINABILITY": {"score": 7.5},
            },
        },
        {
            "id": str(uuid.UUID(int=9)),
            "company_id": str(uuid.UUID(int=1)),
            "title": "Product Manager",
            "description": "Lead product development from ideation to launch, working cross-functionally to ensure alignment with business goals.",
            "skills_requirements": {
                "COMMUNICATION": {"score": 9},
                "ADAPTABILITY": {"score": 8},
                "LEADERSHIP": {"score": 8},
            },
            "wellbeing_preferences": {
                "RELATEDNESS": {"score": 7},
                "MASTERY": {"score": 8},
                "WORK_LIFE": {"score": 7},
            },
            "values_alignment": {
                "INNOVATION": {"score": 9},
                "ETHICS": {"score": 8},
                "DIVERSITY": {"score": 8},
            },
        },
        {
            "id": str(uuid.UUID(int=10)),
            "company_id": str(uuid.UUID(int=2)),
            "title": "Renewable Energy Analyst",
            "description": "Analyze and develop renewable energy projects, focusing on sustainability and environmental impact.",
            "skills_requirements": {
                "TECHNICAL": {"score": 8},
                "PROBLEM_SOLVING": {"score": 7},
                "ADAPTABILITY": {"score": 8},
            },
            "wellbeing_preferences": {
                "AUTONOMY": {"score": 7},
                "MASTERY": {"score": 8},
                "PURPOSE": {"score": 9},
            },
            "values_alignment": {
                "SUSTAINABILITY": {"score": 9.5},
                "IMPACT": {"score": 9},
                "ETHICS": {"score": 8.5},
            },
        },
        {
            "id": str(uuid.UUID(int=11)),
            "company_id": str(uuid.UUID(int=2)),
            "title": "Sustainability Consultant",
            "description": "Provide consulting services to clients on sustainable business practices and energy conservation.",
            "skills_requirements": {
                "COMMUNICATION": {"score": 8},
                "ADAPTABILITY": {"score": 7},
                "COLLABORATION": {"score": 8},
            },
            "wellbeing_preferences": {
                "AUTONOMY": {"score": 6},
                "PURPOSE": {"score": 9},
                "WORK_LIFE": {"score": 8},
            },
            "values_alignment": {
                "SUSTAINABILITY": {"score": 10},
                "ETHICS": {"score": 8.5},
                "GROWTH": {"score": 7},
            },
        },
        # Welmo Health Solutionsstr(uuid.UUID())
        {
            "id": str(uuid.uuid4()),
            "company_id": str(uuid.UUID(int=3)),
            "title": "Clinical Psychologist",
            "description": "Provide clinical therapy and mental health support services, promoting well-being and mental resilience.",
            "skills_requirements": {
                "COMMUNICATION": {"score": 9},
                "PROBLEM_SOLVING": {"score": 8},
                "COLLABORATION": {"score": 7},
            },
            "wellbeing_preferences": {
                "RELATEDNESS": {"score": 9},
                "WORK_LIFE": {"score": 9},
                "PSYCHOLOGICAL_SAFETY": {"score": 9},
            },
            "values_alignment": {
                "GROWTH": {"score": 7},
                "DIVERSITY": {"score": 9},
                "IMPACT": {"score": 8},
            },
        },
        {
            "id": str(uuid.uuid4()),
            "company_id": str(uuid.UUID(int=3)),
            "title": "Wellness Program Coordinator",
            "description": "Coordinate and manage company-wide wellness programs to support employee health.",
            "skills_requirements": {
                "LEADERSHIP": {"score": 8},
                "COMMUNICATION": {"score": 9},
                "COLLABORATION": {"score": 8},
            },
            "wellbeing_preferences": {
                "WORK_LIFE": {"score": 10},
                "RELATEDNESS": {"score": 8},
                "PURPOSE": {"score": 9},
            },
            "values_alignment": {
                "ETHICS": {"score": 10},
                "IMPACT": {"score": 8},
                "GROWTH": {"score": 8},
            },
        },
        # TechNova Innovations
        {
            "id": str(uuid.uuid4()),
            "company_id": str(uuid.UUID(int=4)),
            "title": "Data Scientist",
            "description": "Use data science to generate insights that drive business decisions and optimize performance.",
            "skills_requirements": {
                "TECHNICAL": {"score": 9},
                "PROBLEM_SOLVING": {"score": 8},
                "COMMUNICATION": {"score": 7},
            },
            "wellbeing_preferences": {
                "MASTERY": {"score": 8},
                "AUTONOMY": {"score": 9},
                "WORK_LIFE": {"score": 6},
            },
            "values_alignment": {
                "INNOVATION": {"score": 10},
                "GROWTH": {"score": 8},
                "DIVERSITY": {"score": 7},
            },
        },
        {
            "id": str(uuid.uuid4()),
            "company_id": str(uuid.UUID(int=4)),
            "title": "Machine Learning Engineer",
            "description": "Develop machine learning models for product innovations.",
            "skills_requirements": {
                "TECHNICAL": {"score": 9},
                "PROBLEM_SOLVING": {"score": 8},
                "ADAPTABILITY": {"score": 7},
            },
            "wellbeing_preferences": {
                "AUTONOMY": {"score": 8},
                "MASTERY": {"score": 9},
                "WORK_LIFE": {"score": 7},
            },
            "values_alignment": {
                "INNOVATION": {"score": 10},
                "DIVERSITY": {"score": 8},
                "ETHICS": {"score": 7},
            },
        },
        # GreenPath Financial
        {
            "id": str(uuid.uuid4()),
            "company_id": str(uuid.UUID(int=5)),  # GreenPath Financial's id
            "title": "Financial Planner",
            "description": "Provide personalized financial planning services focused on sustainable investment strategies.",
            "skills_requirements": {
                "TECHNICAL": {"score": 7},
                "COMMUNICATION": {"score": 9},
                "PROBLEM_SOLVING": {"score": 8},
            },
            "wellbeing_preferences": {
                "PURPOSE": {"score": 9},
                "RELATEDNESS": {"score": 7},
                "WORK_LIFE": {"score": 8},
            },
            "values_alignment": {
                "SUSTAINABILITY": {"score": 9},
                "ETHICS": {"score": 9},
                "IMPACT": {"score": 7},
            },
        },
        {
            "id": str(uuid.uuid4()),
            "company_id": str(uuid.UUID(int=5)),
            "title": "Sustainability Investment Analyst",
            "description": "Analyze sustainable investment opportunities and provide recommendations aligned with ESG criteria.",
            "skills_requirements": {
                "TECHNICAL": {"score": 8},
                "ADAPTABILITY": {"score": 7},
                "PROBLEM_SOLVING": {"score": 9},
            },
            "wellbeing_preferences": {
                "AUTONOMY": {"score": 6},
                "MASTERY": {"score": 8},
                "PSYCHOLOGICAL_SAFETY": {"score": 8},
            },
            "values_alignment": {
                "SUSTAINABILITY": {"score": 10},
                "GROWTH": {"score": 8},
                "ETHICS": {"score": 8},
            },
        },
        # EcoWave Solutions
        {
            "id": str(uuid.uuid4()),
            "company_id": str(uuid.UUID(int=6)),  # EcoWave Solutions's id
            "title": "Environmental Project Manager",
            "description": "Lead environmental projects focused on sustainability and compliance with environmental regulations.",
            "skills_requirements": {
                "LEADERSHIP": {"score": 8},
                "COLLABORATION": {"score": 9},
                "COMMUNICATION": {"score": 8},
            },
            "wellbeing_preferences": {
                "PURPOSE": {"score": 10},
                "WORK_LIFE": {"score": 8},
                "MASTERY": {"score": 9},
            },
            "values_alignment": {
                "SUSTAINABILITY": {"score": 10},
                "ETHICS": {"score": 9},
                "INNOVATION": {"score": 7},
            },
        },
        {
            "id": str(uuid.uuid4()),
            "company_id": str(uuid.UUID(int=6)),
            "title": "Sustainability Consultant",
            "description": "Consult with clients to implement sustainable practices and improve environmental impact.",
            "skills_requirements": {
                "TECHNICAL": {"score": 7},
                "PROBLEM_SOLVING": {"score": 8},
                "ADAPTABILITY": {"score": 9},
            },
            "wellbeing_preferences": {
                "AUTONOMY": {"score": 7},
                "WORK_LIFE": {"score": 8},
                "PURPOSE": {"score": 9},
            },
            "values_alignment": {
                "SUSTAINABILITY": {"score": 10},
                "IMPACT": {"score": 10},
                "DIVERSITY": {"score": 8},
            },
        },
        # FutureWork Labs
        {
            "id": str(uuid.uuid4()),
            "company_id": str(uuid.UUID(int=7)),  # FutureWork Labs's id
            "title": "AI Research Scientist",
            "description": "Conduct research and development in artificial intelligence, focusing on future career applications.",
            "skills_requirements": {
                "TECHNICAL": {"score": 9},
                "PROBLEM_SOLVING": {"score": 10},
                "ADAPTABILITY": {"score": 8},
            },
            "wellbeing_preferences": {
                "AUTONOMY": {"score": 10},
                "MASTERY": {"score": 9},
                "WORK_LIFE": {"score": 6},
            },
            "values_alignment": {
                "INNOVATION": {"score": 10},
                "GROWTH": {"score": 10},
                "ETHICS": {"score": 7},
            },
        },
        {
            "id": str(uuid.uuid4()),
            "company_id": str(uuid.UUID(int=7)),
            "title": "Machine Learning Engineer",
            "description": "Develop machine learning models and algorithms for scalable, future-ready applications.",
            "skills_requirements": {
                "TECHNICAL": {"score": 9},
                "COLLABORATION": {"score": 7},
                "COMMUNICATION": {"score": 8},
            },
            "wellbeing_preferences": {
                "MASTERY": {"score": 8},
                "AUTONOMY": {"score": 9},
                "RELATEDNESS": {"score": 6},
            },
            "values_alignment": {
                "INNOVATION": {"score": 10},
                "GROWTH": {"score": 9},
                "DIVERSITY": {"score": 7},
            },
        },
    ]

    for company_data in companies:
        company = Company(**company_data)
        db.add(company)

    for job_post_data in job_postings:
        job_post = JobPosting(**job_post_data)
        db.add(job_post)

    await db.commit()
