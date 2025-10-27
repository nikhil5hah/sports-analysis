"""
Insight model - Stores generated insights for each session
"""
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class Insight(Base):
    __tablename__ = "insights"

    insight_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)

    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    insight_type = Column(String(50), default="session_analysis")

    # All metrics and insights stored as JSON
    # Uses MetricResult format from existing code
    metrics = Column(JSON, nullable=False)

    # HR + Score correlation (NEW insights)
    hr_score_correlation = Column(JSON)

    # Recommendations
    recommendations = Column(JSON)

    # Algorithm version (for tracking improvements)
    algorithm_version = Column(String(20), default="1.0")

    # Relationships
    session = relationship("Session", back_populates="insights")

    def __repr__(self):
        return f"<Insight {self.insight_id} for session {self.session_id}>"
