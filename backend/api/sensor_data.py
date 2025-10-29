"""
Sensor Data API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from backend.models.database import get_db
from backend.models.session import Session as SessionModel
from backend.models.sensor_data import SensorDataBatch
from backend.models.user import User
from backend.api.schemas import SensorDataUpload, SensorDataResponse
from backend.api.dependencies import get_current_user

router = APIRouter()


@router.post("/sessions/{session_id}/sensor-data", response_model=SensorDataResponse, status_code=status.HTTP_201_CREATED)
async def upload_sensor_data(
    session_id: UUID,
    sensor_data: SensorDataUpload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload batched sensor data (accelerometer/gyroscope) for a session"""
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

    # Create sensor data batch
    sensor_batch = SensorDataBatch(
        session_id=session_id,
        start_time=sensor_data.start_time,
        end_time=sensor_data.end_time,
        sample_rate_hz=sensor_data.sample_rate_hz,
        data_blob=sensor_data.data_blob,
        compression_type=sensor_data.compression_type,
        data_points_count=sensor_data.data_points_count
    )

    db.add(sensor_batch)
    db.commit()
    db.refresh(sensor_batch)

    return sensor_batch


@router.get("/sessions/{session_id}/sensor-data", response_model=List[SensorDataResponse])
async def get_sensor_data(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all sensor data batches for a session"""
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

    sensor_batches = db.query(SensorDataBatch).filter(
        SensorDataBatch.session_id == session_id
    ).order_by(SensorDataBatch.start_time).all()

    return sensor_batches
