"""
Heart Rate Data model - Time-series data
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


class HeartRateData(Base):
    __tablename__ = "heart_rate_data"

    # Composite primary key for TimescaleDB hypertable
    time = Column(DateTime(timezone=True), primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"), primary_key=True)

    heart_rate = Column(Float, nullable=False)
    hr_zone = Column(Integer)  # 0-5 (calculated)
    confidence = Column(Float)  # Sensor confidence (0-1)

    # Relationship
    session = relationship("Session", back_populates="hr_data")

    # Index for efficient time-based queries
    __table_args__ = (
        Index('ix_hr_data_session_time', 'session_id', 'time'),
    )

    def __repr__(self):
        return f"<HRData {self.heart_rate} bpm at {self.time}>"
