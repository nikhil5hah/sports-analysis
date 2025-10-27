"""
Session model
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)

    session_type = Column(String(20), nullable=False)  # "match" or "training"
    sport = Column(String(50), default="squash")
    scoring_system = Column(String(20), default="american")  # "american" or "english"

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)

    # Metadata (watch position, location, etc.)
    metadata_ = Column("metadata", JSON)

    # Summary statistics
    final_score_me = Column(Integer, default=0)
    final_score_opponent = Column(Integer, default=0)
    total_games = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    total_rallies = Column(Integer, default=0)
    total_lets = Column(Integer, default=0)  # For rally calculation
    avg_hr = Column(Float)
    max_hr = Column(Float)

    # Sync status
    sync_status = Column(String(20), default="pending")  # pending/syncing/synced/failed
    last_synced_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")
    points = relationship("Point", back_populates="session", cascade="all, delete-orphan")
    hr_data = relationship("HeartRateData", back_populates="session", cascade="all, delete-orphan")
    sensor_batches = relationship("SensorDataBatch", back_populates="session", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session {self.session_id} - {self.session_type}>"
