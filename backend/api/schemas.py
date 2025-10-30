"""
Pydantic Schemas for API Request/Response Models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============================================
# Authentication Schemas
# ============================================

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    max_heart_rate: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: UUID
    email: str
    name: str
    max_heart_rate: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Session Schemas
# ============================================

class SessionCreate(BaseModel):
    session_type: str = Field(description="match or training")
    sport: str = Field(default="squash", description="squash, tennis, badminton, table_tennis, padel")
    scoring_system: str = Field(default="american", description="american or english")
    opponent_name: Optional[str] = None
    location: Optional[str] = None


class SessionUpdate(BaseModel):
    status: Optional[str] = None
    end_time: Optional[datetime] = None
    final_score_me: Optional[int] = None
    final_score_opponent: Optional[int] = None
    total_lets: Optional[int] = None
    notes: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: UUID
    user_id: UUID
    session_type: str
    sport: str
    scoring_system: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    metadata_: Optional[dict] = None
    final_score_me: Optional[int] = None
    final_score_opponent: Optional[int] = None
    total_games: Optional[int] = None
    total_points: Optional[int] = None
    total_rallies: Optional[int] = None
    total_lets: Optional[int] = None
    avg_hr: Optional[float] = None
    max_hr: Optional[float] = None
    sync_status: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# Point Schemas
# ============================================

class PointCreate(BaseModel):
    winner: str = Field(description="me or opponent")
    score_me_before: int
    score_opponent_before: int
    score_me_after: int
    score_opponent_after: int
    game_number: int
    hr_at_point_end: Optional[float] = None
    is_let: str = Field(default="false", description="true or false")
    notes: Optional[str] = None


class PointResponse(BaseModel):
    point_id: UUID
    session_id: UUID
    point_number: int
    game_number: int
    timestamp: datetime
    winner: str
    score_me_before: int
    score_opponent_before: int
    score_me_after: int
    score_opponent_after: int
    hr_at_point_end: Optional[float]
    is_let: str
    notes: Optional[str]

    class Config:
        from_attributes = True


# ============================================
# Heart Rate Schemas
# ============================================

class HeartRateDataPoint(BaseModel):
    timestamp: datetime
    bpm: float


class HeartRateUpload(BaseModel):
    data_points: List[HeartRateDataPoint]


class HeartRateResponse(BaseModel):
    hr_id: UUID
    session_id: UUID
    timestamp: datetime
    bpm: float

    class Config:
        from_attributes = True


# ============================================
# Sensor Data Schemas
# ============================================

class SensorDataUpload(BaseModel):
    start_time: datetime
    end_time: datetime
    sample_rate_hz: float
    data_blob: bytes
    compression_type: str = "msgpack"
    data_points_count: int


class SensorDataResponse(BaseModel):
    batch_id: UUID
    session_id: UUID
    start_time: datetime
    end_time: datetime
    sample_rate_hz: float
    compression_type: str
    data_points_count: int

    class Config:
        from_attributes = True


# ============================================
# Insights Schemas
# ============================================

class InsightResponse(BaseModel):
    insight_id: UUID
    session_id: UUID
    generated_at: datetime
    insight_type: str
    insight_data: dict

    class Config:
        from_attributes = True


# ============================================
# GPS Data Schemas
# ============================================

class GPSDataPoint(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None
    bearing: Optional[float] = None
    accuracy: Optional[float] = None
    vertical_accuracy: Optional[float] = None


class GPSUpload(BaseModel):
    data_points: List[GPSDataPoint]


class GPSDataResponse(BaseModel):
    time: datetime
    session_id: UUID
    latitude: float
    longitude: float
    altitude: Optional[float]
    speed: Optional[float]
    bearing: Optional[float]
    accuracy: Optional[float]
    vertical_accuracy: Optional[float]

    class Config:
        from_attributes = True


# ============================================
# SpO2 Data Schemas
# ============================================

class SpO2DataPoint(BaseModel):
    timestamp: datetime
    spo2_percentage: float
    confidence: Optional[float] = None
    measurement_quality: Optional[float] = None


class SpO2Upload(BaseModel):
    data_points: List[SpO2DataPoint]


class SpO2DataResponse(BaseModel):
    time: datetime
    session_id: UUID
    spo2_percentage: float
    confidence: Optional[float]
    measurement_quality: Optional[float]

    class Config:
        from_attributes = True


# ============================================
# Temperature Data Schemas
# ============================================

class TemperatureDataPoint(BaseModel):
    timestamp: datetime
    temperature_celsius: float
    sensor_location: Optional[float] = None
    confidence: Optional[float] = None


class TemperatureUpload(BaseModel):
    data_points: List[TemperatureDataPoint]


class TemperatureDataResponse(BaseModel):
    time: datetime
    session_id: UUID
    temperature_celsius: float
    sensor_location: Optional[float]
    confidence: Optional[float]

    class Config:
        from_attributes = True


# ============================================
# Activity Data Schemas
# ============================================

class ActivityDataPoint(BaseModel):
    timestamp: datetime
    steps: Optional[int] = None
    calories: Optional[float] = None
    distance: Optional[float] = None
    active_minutes: Optional[int] = None
    floors_climbed: Optional[int] = None
    intensity_level: Optional[int] = None


class ActivityUpload(BaseModel):
    data_points: List[ActivityDataPoint]


class ActivityDataResponse(BaseModel):
    time: datetime
    session_id: UUID
    steps: Optional[int]
    calories: Optional[float]
    distance: Optional[float]
    active_minutes: Optional[int]
    floors_climbed: Optional[int]
    intensity_level: Optional[int]

    class Config:
        from_attributes = True
