"""
Insights/Analytics API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from backend.models.database import get_db
from backend.models.session import Session as SessionModel
from backend.models.insight import Insight
from backend.models.user import User
from backend.api.schemas import InsightResponse
from backend.api.dependencies import get_current_user
from backend.services.insight_generator import InsightGenerator

router = APIRouter()


@router.get("/sessions/{session_id}/insights", response_model=List[InsightResponse])
async def get_session_insights(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all insights for a session"""
    # Verify session exists and belongs to user
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.user_id == current_user.user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Get existing insights
    insights = db.query(Insight).filter(
        Insight.session_id == session_id
    ).order_by(Insight.generated_at.desc()).all()

    # If no insights exist and session is completed, generate them
    if not insights and session.status == "completed":
        try:
            generator = InsightGenerator(db)
            insights = generator.generate_insights(session_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate insights: {str(e)}"
            )

    return insights


@router.post("/sessions/{session_id}/insights/regenerate", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def regenerate_insights(
    session_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Force regenerate insights for a session (runs in background)"""
    # Verify session exists and belongs to user
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.user_id == current_user.user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only generate insights for completed sessions"
        )

    # Delete existing insights
    db.query(Insight).filter(Insight.session_id == session_id).delete()
    db.commit()

    # Schedule insight generation in background
    def generate_insights_task():
        generator = InsightGenerator(db)
        generator.generate_insights(session_id)

    background_tasks.add_task(generate_insights_task)

    return {
        "message": "Insight regeneration started",
        "session_id": str(session_id)
    }
