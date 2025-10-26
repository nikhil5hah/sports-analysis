"""
Squash Performance Analysis - Data Ingestion Module

Handles importing and preprocessing fitness tracker data from various sources.
"""

import pandas as pd
import numpy as np
import gpxpy
import gpxpy.gpx
from fitparse import FitFile
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FitnessDataImporter:
    """Handles importing fitness tracker data from GPX and FIT files."""
    
    def __init__(self):
        self.data = None
        self.session_info = {}
    
    def import_gpx_file(self, file_path: str) -> pd.DataFrame:
        """Import data from GPX file (typically from Strava exports)."""
        try:
            with open(file_path, 'r') as gpx_file:
                gpx = gpxpy.parse(gpx_file)
            
            data_points = []
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        data_points.append({
                            'timestamp': point.time,
                            'latitude': point.latitude,
                            'longitude': point.longitude,
                            'elevation': point.elevation,
                            'heart_rate': getattr(point, 'heart_rate', None),
                            'cadence': getattr(point, 'cadence', None),
                            'speed': getattr(point, 'speed', None)
                        })
            
            df = pd.DataFrame(data_points)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"Imported {len(df)} data points from GPX file")
            return df
            
        except Exception as e:
            logger.error(f"Error importing GPX file: {e}")
            raise
    
    def import_fit_file(self, file_path: str) -> pd.DataFrame:
        """Import data from FIT file (native fitness tracker format)."""
        try:
            fitfile = FitFile(file_path)
            
            data_points = []
            for record in fitfile.get_messages('record'):
                point = {}
                for data in record:
                    if data.name == 'timestamp':
                        point['timestamp'] = data.value
                    elif data.name == 'heart_rate':
                        point['heart_rate'] = data.value
                    elif data.name == 'cadence':
                        point['cadence'] = data.value
                    elif data.name == 'speed':
                        point['speed'] = data.value
                    elif data.name == 'power':
                        point['power'] = data.value
                    elif data.name == 'temperature':
                        point['temperature'] = data.value
                    elif data.name == 'position_lat':
                        point['latitude'] = data.value
                    elif data.name == 'position_long':
                        point['longitude'] = data.value
                    elif data.name == 'altitude':
                        point['elevation'] = data.value
                    # Accelerometer data
                    elif data.name == 'accel_x':
                        point['accelerometer_x'] = data.value
                    elif data.name == 'accel_y':
                        point['accelerometer_y'] = data.value
                    elif data.name == 'accel_z':
                        point['accelerometer_z'] = data.value
                    # Gyroscope data
                    elif data.name == 'gyro_x':
                        point['gyroscope_x'] = data.value
                    elif data.name == 'gyro_y':
                        point['gyroscope_y'] = data.value
                    elif data.name == 'gyro_z':
                        point['gyroscope_z'] = data.value
                    # Additional movement data
                    elif data.name == 'step_count':
                        point['step_count'] = data.value
                    elif data.name == 'stride_length':
                        point['stride_length'] = data.value
                    elif data.name == 'vertical_oscillation':
                        point['vertical_oscillation'] = data.value
                    elif data.name == 'ground_contact_time':
                        point['ground_contact_time'] = data.value
                
                if point:
                    data_points.append(point)
            
            df = pd.DataFrame(data_points)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"Imported {len(df)} data points from FIT file")
            
            # Log available data fields
            available_fields = [col for col in df.columns if col != 'timestamp']
            logger.info(f"Available data fields: {available_fields}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error importing FIT file: {e}")
            raise
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the imported data."""
        # Remove duplicates
        df = df.drop_duplicates(subset=['timestamp']).reset_index(drop=True)
        
        # Interpolate missing values for continuous metrics
        numeric_columns = ['heart_rate', 'cadence', 'speed', 'power', 'temperature',
                          'accelerometer_x', 'accelerometer_y', 'accelerometer_z',
                          'gyroscope_x', 'gyroscope_y', 'gyroscope_z',
                          'step_count', 'stride_length', 'vertical_oscillation', 'ground_contact_time']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].interpolate(method='linear')
        
        # Calculate time differences
        df['time_diff'] = df['timestamp'].diff().dt.total_seconds()
        
        # Calculate cumulative time
        df['cumulative_time'] = df['time_diff'].cumsum()
        
        # Calculate session duration
        if len(df) > 0:
            self.session_info['duration_minutes'] = df['cumulative_time'].iloc[-1] / 60
            self.session_info['start_time'] = df['timestamp'].iloc[0]
            self.session_info['end_time'] = df['timestamp'].iloc[-1]
        
        logger.info(f"Preprocessed data: {len(df)} points, {self.session_info.get('duration_minutes', 0):.1f} minutes")
        return df
    
    def set_session_context(self, hand_position: str, session_type: str):
        """Set context for analysis (hand position and session type)."""
        self.session_info['hand_position'] = hand_position  # 'playing_hand' or 'non_playing_hand'
        self.session_info['session_type'] = session_type    # 'training' or 'match'
        
        logger.info(f"Session context set: {hand_position}, {session_type}")


if __name__ == "__main__":
    # Example usage
    importer = FitnessDataImporter()
    
    # Test with sample data structure
    sample_data = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01 10:00:00', periods=100, freq='1s'),
        'heart_rate': np.random.normal(120, 20, 100),
        'cadence': np.random.normal(80, 10, 100),
        'speed': np.random.normal(5, 2, 100)
    })
    
    processed_data = importer.preprocess_data(sample_data)
    print(f"Processed {len(processed_data)} data points")
    print(f"Session duration: {importer.session_info.get('duration_minutes', 0):.1f} minutes")
