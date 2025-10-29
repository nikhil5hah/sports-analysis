"""
Temperature Data API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from backend.models.database import get_db
from backend.models.session import Session as SessionModel
from backend.models.temperature_data import TemperatureData
from backend.models.user import User
from backend.api.schemas import TemperatureUpload, TemperatureDataResponse
from backend.api.dependencies import get_current_user

router = APIRouter()


@router.post("/sessions/{session_id}/temperature", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_temperature_data(
    session_id: UUID,
    temp_data: TemperatureUpload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload skin temperature data for a session"""
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

    # Create temperature data records in bulk
    temp_records = [
        TemperatureData(
            session_id=session_id,
            time=data_point.timestamp,
            temperature_celsius=data_point.temperature_celsius,
            sensor_location=data_point.sensor_location,
            confidence=data_point.confidence
        )
        for data_point in temp_data.data_points
    ]

    db.bulk_save_objects(temp_records)
    db.commit()

    return {
        "message": "Temperature data uploaded successfully",
        "records_created": len(temp_records)
    }


@router.get("/sessions/{session_id}/temperature", response_model=List[TemperatureDataResponse])
async def get_temperature_data(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all temperature data for a session"""
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

    temp_data = db.query(TemperatureData).filter(
        TemperatureData.session_id == session_id
    ).order_by(TemperatureData.time).all()

    return temp_data
