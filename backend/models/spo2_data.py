"""
SpO2 (Blood Oxygen) Data model - Time-series oxygen saturation
"""
from sqlalchemy import Column, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


class SpO2Data(Base):
    __tablename__ = "spo2_data"

    # Composite primary key for time-series
    time = Column(DateTime(timezone=True), primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"), primary_key=True)

    # SpO2 measurement
    spo2_percentage = Column(Float, nullable=False)  # 0-100%

    # Quality/confidence
    confidence = Column(Float)  # Sensor confidence (0-1)
    measurement_quality = Column(Float)  # Quality score from device

    # Relationship
    session = relationship("Session", back_populates="spo2_data")

    # Index for efficient time-based queries
    __table_args__ = (
        Index('ix_spo2_data_session_time', 'session_id', 'time'),
    )

    def __repr__(self):
        return f"<SpO2Data {self.spo2_percentage}% at {self.time}>"
