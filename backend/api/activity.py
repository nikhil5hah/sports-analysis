"""
Activity Data API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from backend.models.database import get_db
from backend.models.session import Session as SessionModel
from backend.models.activity_data import ActivityData
from backend.models.user import User
from backend.api.schemas import ActivityUpload, ActivityDataResponse
from backend.api.dependencies import get_current_user

router = APIRouter()


@router.post("/sessions/{session_id}/activity", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_activity_data(
    session_id: UUID,
    activity_data: ActivityUpload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload activity metrics (steps, calories, distance) for a session"""
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

    # Create activity data records in bulk
    activity_records = [
        ActivityData(
            session_id=session_id,
            time=data_point.timestamp,
            steps=data_point.steps,
            calories=data_point.calories,
            distance=data_point.distance,
            active_minutes=data_point.active_minutes,
            floors_climbed=data_point.floors_climbed,
            intensity_level=data_point.intensity_level
        )
        for data_point in activity_data.data_points
    ]

    db.bulk_save_objects(activity_records)
    db.commit()

    return {
        "message": "Activity data uploaded successfully",
        "records_created": len(activity_records)
    }


@router.get("/sessions/{session_id}/activity", response_model=List[ActivityDataResponse])
async def get_activity_data(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all activity data for a session"""
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

    activity_data = db.query(ActivityData).filter(
        ActivityData.session_id == session_id
    ).order_by(ActivityData.time).all()

    return activity_data
