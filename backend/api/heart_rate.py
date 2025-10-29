"""
Heart Rate Data API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from backend.models.database import get_db
from backend.models.session import Session as SessionModel
from backend.models.heart_rate_data import HeartRateData
from backend.models.user import User
from backend.api.schemas import HeartRateUpload, HeartRateResponse
from backend.api.dependencies import get_current_user

router = APIRouter()


@router.post("/sessions/{session_id}/heart-rate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_heart_rate_data(
    session_id: UUID,
    hr_data: HeartRateUpload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload heart rate data for a session"""
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

    # Create HR data records in bulk
    hr_records = [
        HeartRateData(
            session_id=session_id,
            timestamp=data_point.timestamp,
            bpm=data_point.bpm
        )
        for data_point in hr_data.data_points
    ]

    db.bulk_save_objects(hr_records)
    db.commit()

    return {
        "message": "Heart rate data uploaded successfully",
        "records_created": len(hr_records)
    }


@router.get("/sessions/{session_id}/heart-rate", response_model=List[HeartRateResponse])
async def get_heart_rate_data(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all heart rate data for a session"""
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

    hr_data = db.query(HeartRateData).filter(
        HeartRateData.session_id == session_id
    ).order_by(HeartRateData.timestamp).all()

    return hr_data
