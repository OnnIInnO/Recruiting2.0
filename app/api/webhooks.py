# app/api/webhooks.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from app.core.dimensions import AssessmentType
from app.db.database import get_db

router = APIRouter()


@router.post("/webhooks/assessment/{assessment_type}")
async def assessment_webhook(
    assessment_type: AssessmentType, payload: Dict, db: AsyncSession = Depends(get_db)
):
    """Handle assessment form submissions from Framer"""
    try:
        # Extract email from Name field
        email = payload.pop("Name", None)
        if not email:
            raise HTTPException(
                status_code=400, detail="Email is required in Name field"
            )

        # Convert string values to integers
        answers = {key: int(value) for key, value in payload.items()}
        print("Received answers:", answers)
        # Import and use the existing submit_assessment function
        from app.api.routes import submit_assessment

        # Use the existing function directly with the assessment_type from URL
        return await submit_assessment(
            assessment_type=assessment_type, answers=answers, user_email=email, db=db
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid numeric value: {str(e)}")
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
