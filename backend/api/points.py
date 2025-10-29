"""
Points Recording API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from backend.models.database import get_db
from backend.models.session import Session as SessionModel
from backend.models.point import Point
from backend.models.user import User
from backend.api.schemas import PointCreate, PointResponse
from backend.api.dependencies import get_current_user

router = APIRouter()


@router.post("/sessions/{session_id}/points", response_model=PointResponse, status_code=status.HTTP_201_CREATED)
async def record_point(
    session_id: UUID,
    point_data: PointCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a point during a match"""
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

    if session.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add points to a completed session"
        )

    # Get the next point number for this session
    last_point = db.query(Point).filter(
        Point.session_id == session_id
    ).order_by(Point.point_number.desc()).first()

    point_number = (last_point.point_number + 1) if last_point else 1

    # Create new point
    new_point = Point(
        session_id=session_id,
        point_number=point_number,
        game_number=point_data.game_number,
        timestamp=datetime.utcnow(),
        winner=point_data.winner,
        score_me_before=point_data.score_me_before,
        score_opponent_before=point_data.score_opponent_before,
        score_me_after=point_data.score_me_after,
        score_opponent_after=point_data.score_opponent_after,
        hr_at_point_end=point_data.hr_at_point_end,
        is_let=point_data.is_let,
        notes=point_data.notes
    )

    # Update session total_lets if this was a let
    if point_data.is_let == "true":
        session.total_lets = (session.total_lets or 0) + 1

    db.add(new_point)
    db.commit()
    db.refresh(new_point)

    return new_point


@router.get("/sessions/{session_id}/points", response_model=List[PointResponse])
async def get_session_points(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all points for a session"""
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

    points = db.query(Point).filter(
        Point.session_id == session_id
    ).order_by(Point.point_number).all()

    return points
