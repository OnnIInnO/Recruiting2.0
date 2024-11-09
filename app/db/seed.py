from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Company, JobPosting
from app.core.dimensions import AssessmentDimensions, AssessmentType
import json

async def seed_data(db: AsyncSession):
    """Seed initial data for development"""
    
    # Create example companies
    companies = [
        {
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
            }
        },
        {
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
            }
        }
    ]
    
    for company_data in companies:
        company = Company(**company_data)
        db.add(company)
    
    await db.commit()