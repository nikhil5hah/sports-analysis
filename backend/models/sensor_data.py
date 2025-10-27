"""
Sensor Data model - Stores batched accelerometer/gyroscope data
For future ML training
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class SensorDataBatch(Base):
    __tablename__ = "sensor_data_batches"

    batch_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"), nullable=False, index=True)

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    sample_rate_hz = Column(Float, nullable=False)  # Usually 10 Hz

    # Compressed binary data (msgpack or similar)
    # Contains arrays of accelerometer_x/y/z, gyroscope_x/y/z
    data_blob = Column(LargeBinary, nullable=False)

    # Metadata about compression
    compression_type = Column(String(20), default="msgpack")
    data_points_count = Column(Integer)  # Number of samples in this batch

    # Relationship
    session = relationship("Session", back_populates="sensor_batches")

    def __repr__(self):
        return f"<SensorBatch {self.batch_id} - {self.data_points_count} samples>"
