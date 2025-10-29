"""
GPS Data API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from backend.models.database import get_db
from backend.models.session import Session as SessionModel
from backend.models.gps_data import GPSData
from backend.models.user import User
from backend.api.schemas import GPSUpload, GPSDataResponse
from backend.api.dependencies import get_current_user

router = APIRouter()


@router.post("/sessions/{session_id}/gps", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_gps_data(
    session_id: UUID,
    gps_data: GPSUpload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload GPS/location data for a session"""
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

    # Create GPS data records in bulk
    gps_records = [
        GPSData(
            session_id=session_id,
            time=data_point.timestamp,
            latitude=data_point.latitude,
            longitude=data_point.longitude,
            altitude=data_point.altitude,
            speed=data_point.speed,
            bearing=data_point.bearing,
            accuracy=data_point.accuracy,
            vertical_accuracy=data_point.vertical_accuracy
        )
        for data_point in gps_data.data_points
    ]

    db.bulk_save_objects(gps_records)
    db.commit()

    return {
        "message": "GPS data uploaded successfully",
        "records_created": len(gps_records)
    }


@router.get("/sessions/{session_id}/gps", response_model=List[GPSDataResponse])
async def get_gps_data(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all GPS data for a session"""
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

    gps_data = db.query(GPSData).filter(
        GPSData.session_id == session_id
    ).order_by(GPSData.time).all()

    return gps_data
