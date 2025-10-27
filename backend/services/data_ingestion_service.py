"""
Data Ingestion Service
REUSES: data/ingestion/data_ingestion.py (existing code)

This service wraps the existing FitnessDataImporter to work with the backend.
"""
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import pandas as pd

# Import existing code
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from data.ingestion.data_ingestion import FitnessDataImporter

from backend.models import Session, HeartRateData, SensorDataBatch
from sqlalchemy.orm import Session as DBSession


class DataIngestionService:
    """
    Service to ingest fitness data from FIT/GPX files.
    Wraps existing FitnessDataImporter and stores in database.
    """

    def __init__(self, db: DBSession):
        self.db = db
        self.importer = FitnessDataImporter()  # REUSE existing class

    async def process_fit_file(self, file_path: str, session_id: str) -> Dict:
        """
        Process uploaded FIT file and store in database.

        Args:
            file_path: Path to FIT file
            session_id: UUID of session

        Returns:
            Dict with processing results
        """
        # REUSE existing import logic
        df = self.importer.import_fit_file(file_path)
        df = self.importer.preprocess_data(df)

        # Extract and store HR data
        hr_count = await self._store_hr_data(session_id, df)

        # Extract and store sensor data (if available)
        sensor_count = await self._store_sensor_data(session_id, df)

        # Update session summary
        await self._update_session_summary(session_id, df)

        return {
            "status": "success",
            "data_points": len(df),
            "hr_records": hr_count,
            "sensor_batches": sensor_count
        }

    async def _store_hr_data(self, session_id: str, df: pd.DataFrame) -> int:
        """Store heart rate data in bulk"""
        if 'heart_rate' not in df.columns:
            return 0

        # Calculate HR zones
        max_hr = self._get_max_hr_for_session(session_id)
        df = self._calculate_hr_zones(df, max_hr)

        # Prepare bulk insert
        hr_records = []
        for idx, row in df.iterrows():
            if pd.notna(row.get('heart_rate')):
                hr_records.append({
                    'time': row['timestamp'],
                    'session_id': session_id,
                    'heart_rate': float(row['heart_rate']),
                    'hr_zone': int(row.get('hr_zone', 0)),
                    'confidence': 1.0  # Assume high confidence from watch
                })

        if hr_records:
            # Bulk insert
            self.db.bulk_insert_mappings(HeartRateData, hr_records)
            self.db.commit()

        return len(hr_records)

    async def _store_sensor_data(self, session_id: str, df: pd.DataFrame) -> int:
        """
        Store sensor data in batches (compressed).
        For future ML training.
        """
        # Check if sensor data exists
        sensor_cols = ['accelerometer_x', 'accelerometer_y', 'accelerometer_z',
                      'gyroscope_x', 'gyroscope_y', 'gyroscope_z']

        has_sensor_data = any(col in df.columns for col in sensor_cols)
        if not has_sensor_data:
            return 0

        # TODO: Implement batching and compression (msgpack)
        # For MVP, we can skip this and add later when needed for ML

        return 0

    async def _update_session_summary(self, session_id: str, df: pd.DataFrame):
        """Update session with summary statistics from data"""
        session = self.db.query(Session).filter_by(session_id=session_id).first()
        if not session:
            return

        # Calculate summary stats
        if 'heart_rate' in df.columns:
            hr_data = df['heart_rate'].dropna()
            if len(hr_data) > 0:
                session.avg_hr = float(hr_data.mean())
                session.max_hr = float(hr_data.max())

        # Update duration if not set
        if not session.duration_seconds and len(df) > 0:
            duration = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).total_seconds()
            session.duration_seconds = int(duration)
            session.end_time = df['timestamp'].iloc[-1]

        self.db.commit()

    def _get_max_hr_for_session(self, session_id: str) -> float:
        """Get user's max HR or estimate from data"""
        session = self.db.query(Session).filter_by(session_id=session_id).first()
        if not session:
            return 185.0  # Default fallback

        # Check if user has max_hr set
        if session.user and session.user.max_heart_rate:
            return float(session.user.max_heart_rate)

        # Estimate from age if available
        if session.user and session.user.age:
            return 208 - (0.7 * session.user.age)

        # Default
        return 185.0

    def _calculate_hr_zones(self, df: pd.DataFrame, max_hr: float) -> pd.DataFrame:
        """
        Calculate HR zones for all data points.
        PORT of calculate_hr_zones() from core/metrics_framework.py
        """
        def assign_zone(hr: float) -> int:
            if pd.isna(hr):
                return 0

            pct = (hr / max_hr) * 100

            if pct < 50:
                return 0
            elif pct < 60:
                return 1
            elif pct < 70:
                return 2
            elif pct < 80:
                return 3
            elif pct < 90:
                return 4
            else:
                return 5

        df['hr_zone'] = df['heart_rate'].apply(assign_zone)
        return df
