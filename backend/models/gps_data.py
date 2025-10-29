"""
GPS/Location Data model - Time-series location tracking
"""
from sqlalchemy import Column, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


class GPSData(Base):
    __tablename__ = "gps_data"

    # Composite primary key for time-series
    time = Column(DateTime(timezone=True), primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"), primary_key=True)

    # Location data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float)  # meters above sea level

    # Movement metrics
    speed = Column(Float)  # meters per second
    bearing = Column(Float)  # degrees (0-360)

    # Accuracy/quality
    accuracy = Column(Float)  # horizontal accuracy in meters
    vertical_accuracy = Column(Float)  # vertical accuracy in meters

    # Relationship
    session = relationship("Session", back_populates="gps_data")

    # Index for efficient time-based queries
    __table_args__ = (
        Index('ix_gps_data_session_time', 'session_id', 'time'),
    )

    def __repr__(self):
        return f"<GPSData ({self.latitude}, {self.longitude}) at {self.time}>"
