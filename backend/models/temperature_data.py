"""
Temperature Data model - Time-series skin temperature
"""
from sqlalchemy import Column, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


class TemperatureData(Base):
    __tablename__ = "temperature_data"

    # Composite primary key for time-series
    time = Column(DateTime(timezone=True), primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"), primary_key=True)

    # Temperature measurement
    temperature_celsius = Column(Float, nullable=False)

    # Sensor location (wrist, chest, etc.)
    sensor_location = Column(Float)  # Optional: which sensor took the reading

    # Quality
    confidence = Column(Float)  # Sensor confidence (0-1)

    # Relationship
    session = relationship("Session", back_populates="temperature_data")

    # Index for efficient time-based queries
    __table_args__ = (
        Index('ix_temperature_data_session_time', 'session_id', 'time'),
    )

    def __repr__(self):
        return f"<TemperatureData {self.temperature_celsius}°C at {self.time}>"
