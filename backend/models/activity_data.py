"""
Activity Data model - Time-series activity metrics (steps, calories, distance)
"""
from sqlalchemy import Column, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


class ActivityData(Base):
    __tablename__ = "activity_data"

    # Composite primary key for time-series
    time = Column(DateTime(timezone=True), primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"), primary_key=True)

    # Activity metrics (cumulative or per-interval)
    steps = Column(Integer)  # Step count
    calories = Column(Float)  # Calories burned (kcal)
    distance = Column(Float)  # Distance traveled (meters)

    # Additional metrics
    active_minutes = Column(Integer)  # Active time in minutes
    floors_climbed = Column(Integer)  # Floors/elevation gain

    # Movement intensity
    intensity_level = Column(Integer)  # 0=sedentary, 1=light, 2=moderate, 3=vigorous

    # Relationship
    session = relationship("Session", back_populates="activity_data")

    # Index for efficient time-based queries
    __table_args__ = (
        Index('ix_activity_data_session_time', 'session_id', 'time'),
    )

    def __repr__(self):
        return f"<ActivityData {self.steps} steps, {self.calories} cal at {self.time}>"
