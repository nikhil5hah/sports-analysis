"""
SpO2 Data API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from backend.models.database import get_db
from backend.models.session import Session as SessionModel
from backend.models.spo2_data import SpO2Data
from backend.models.user import User
from backend.api.schemas import SpO2Upload, SpO2DataResponse
from backend.api.dependencies import get_current_user

router = APIRouter()


@router.post("/sessions/{session_id}/spo2", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_spo2_data(
    session_id: UUID,
    spo2_data: SpO2Upload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload SpO2 (blood oxygen) data for a session"""
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

    # Create SpO2 data records in bulk
    spo2_records = [
        SpO2Data(
            session_id=session_id,
            time=data_point.timestamp,
            spo2_percentage=data_point.spo2_percentage,
            confidence=data_point.confidence,
            measurement_quality=data_point.measurement_quality
        )
        for data_point in spo2_data.data_points
    ]

    db.bulk_save_objects(spo2_records)
    db.commit()

    return {
        "message": "SpO2 data uploaded successfully",
        "records_created": len(spo2_records)
    }


@router.get("/sessions/{session_id}/spo2", response_model=List[SpO2DataResponse])
async def get_spo2_data(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all SpO2 data for a session"""
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

    spo2_data = db.query(SpO2Data).filter(
        SpO2Data.session_id == session_id
    ).order_by(SpO2Data.time).all()

    return spo2_data
