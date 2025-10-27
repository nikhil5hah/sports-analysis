"""
Point model - Records each point scored during a match
"""
from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class Point(Base):
    __tablename__ = "points"

    point_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"), nullable=False, index=True)

    point_number = Column(Integer, nullable=False)  # Sequential within session
    game_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    # Score tracking
    score_me_before = Column(Integer, nullable=False)
    score_opponent_before = Column(Integer, nullable=False)
    score_me_after = Column(Integer, nullable=False)
    score_opponent_after = Column(Integer, nullable=False)

    winner = Column(String(20), nullable=False)  # "me" or "opponent"

    # HR at point end (from watch)
    hr_at_point_end = Column(Float)

    # Optional: Was this a let?
    is_let = Column(String, default=False)

    # Optional notes
    notes = Column(String)

    # Relationship
    session = relationship("Session", back_populates="points")

    def __repr__(self):
        return f"<Point {self.point_number} - Game {self.game_number}>"
