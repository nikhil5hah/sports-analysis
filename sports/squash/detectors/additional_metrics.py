"""
Additional Metric Detectors for Squash Performance Analysis

Extends the metrics framework with additional detectors for comprehensive analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from core.metrics_framework import BaseMetricDetector, MetricResult, MetricType

logger = logging.getLogger(__name__)

class SessionDurationDetector(BaseMetricDetector):
    """Detects total session duration."""
    
    def __init__(self):
        super().__init__("total_session_duration", MetricType.TEMPORAL)
        self.algorithm_version = "1.0"
    
    def get_required_data_fields(self) -> List[str]:
        return ['timestamp']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Calculate total session duration."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing timestamp data'}
            )
        
        if len(df) < 2:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Insufficient data points'}
            )
        
        # Calculate duration from first to last timestamp
        start_time = df['timestamp'].iloc[0]
        end_time = df['timestamp'].iloc[-1]
        duration_minutes = (end_time - start_time).total_seconds() / 60
        
        return MetricResult(
            metric_name=self.metric_name,
            value=duration_minutes,
            confidence=1.0,  # Always confident in this calculation
            metadata={
                'start_time': start_time,
                'end_time': end_time,
                'data_points': len(df),
                'algorithm': 'timestamp_difference'
            }
        )

class PlayingTimeDetector(BaseMetricDetector):
    """Detects total playing time (sum of rally durations)."""
    
    def __init__(self):
        super().__init__("total_playing_time", MetricType.TEMPORAL)
        self.algorithm_version = "1.0"
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate', 'timestamp']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Calculate total playing time from rallies."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing required data fields'}
            )
        
        # Get rallies from context or detect them
        rallies = context.get('rallies', []) if context else []
        
        if not rallies:
            # Fallback: detect rallies ourselves
            from core.metrics_framework import RallyDetector
            rally_detector = RallyDetector()
            rally_result = rally_detector.detect(df, context)
            rallies = rally_result.metadata.get('rallies', [])
        
        if not rallies:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'No rallies detected'}
            )
        
        # Sum up rally durations
        total_playing_time = sum([rally['duration_minutes'] for rally in rallies])
        
        confidence = self.get_confidence_score(df, total_playing_time)
        
        return MetricResult(
            metric_name=self.metric_name,
            value=total_playing_time,
            confidence=confidence,
            metadata={
                'rally_count': len(rallies),
                'avg_rally_duration': total_playing_time / len(rallies) if rallies else 0,
                'algorithm': 'rally_duration_sum'
            }
        )
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on rally detection quality."""
        hr_data = df['heart_rate'].dropna()
        completeness = len(hr_data) / len(df)
        
        if result > 0:
            # Confidence based on playing time ratio
            session_duration = df['cumulative_time'].iloc[-1] / 60 if 'cumulative_time' in df.columns else 0
            if session_duration > 0:
                playing_ratio = result / session_duration
                # Reasonable playing ratio is 30-70% of session time
                ratio_confidence = 1.0 - abs(playing_ratio - 0.5) * 2
                return min(completeness * max(ratio_confidence, 0.3), 1.0)
        
        return completeness * 0.5

class LongestRallyDetector(BaseMetricDetector):
    """Detects the longest rally duration."""
    
    def __init__(self):
        super().__init__("longest_rally_length", MetricType.TEMPORAL)
        self.algorithm_version = "1.0"
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate', 'timestamp']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Find the longest rally duration."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing required data fields'}
            )
        
        # Get rallies from context or detect them
        rallies = context.get('rallies', []) if context else []
        
        if not rallies:
            # Fallback: detect rallies ourselves
            from core.metrics_framework import RallyDetector
            rally_detector = RallyDetector()
            rally_result = rally_detector.detect(df, context)
            rallies = rally_result.metadata.get('rallies', [])
        
        if not rallies:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'No rallies detected'}
            )
        
        # Find longest rally
        longest_rally = max(rallies, key=lambda r: r['duration_minutes'])
        
        # Multiply by 2 to account for both players (you + opponent)
        longest_rally_duration = longest_rally['duration_minutes'] * 2
        
        confidence = self.get_confidence_score(df, longest_rally_duration)
        
        return MetricResult(
            metric_name=self.metric_name,
            value=longest_rally_duration,
            confidence=confidence,
            metadata={
                'longest_rally': longest_rally,
                'total_rallies': len(rallies),
                'algorithm': 'max_rally_duration_times_two',
                'note': 'Duration multiplied by 2 to account for both players'
            }
        )
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on rally detection quality."""
        hr_data = df['heart_rate'].dropna()
        completeness = len(hr_data) / len(df)
        
        if result > 0:
            # Confidence based on longest rally reasonableness
            # Very long rallies (>5 minutes) might indicate detection issues
            reasonableness = 1.0 - max(0, result - 5.0) * 0.1
            return min(completeness * reasonableness, 1.0)
        
        return completeness * 0.5

class RalliesPerGameDetector(BaseMetricDetector):
    """Detects rallies per game."""
    
    def __init__(self):
        super().__init__("rallies_per_game", MetricType.COUNT)
        self.algorithm_version = "1.0"
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate', 'timestamp']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Calculate rallies per game."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing required data fields'}
            )
        
        # Get rallies and games from context
        rallies = context.get('rallies', []) if context else []
        games = context.get('games', []) if context else []
        
        if not rallies:
            # Fallback: detect rallies ourselves
            from core.metrics_framework import RallyDetector
            rally_detector = RallyDetector()
            rally_result = rally_detector.detect(df, context)
            rallies = rally_result.metadata.get('rallies', [])
        
        if not games:
            # Fallback: detect games ourselves
            from core.metrics_framework import GameDetector
            game_detector = GameDetector()
            game_result = game_detector.detect(df, context)
            num_games = game_result.value
        else:
            num_games = len(games)
        
        if num_games == 0:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'No games detected'}
            )
        
        rallies_per_game = len(rallies) / num_games
        
        confidence = self.get_confidence_score(df, rallies_per_game)
        
        return MetricResult(
            metric_name=self.metric_name,
            value=rallies_per_game,
            confidence=confidence,
            metadata={
                'total_rallies': len(rallies),
                'total_games': num_games,
                'algorithm': 'rallies_divided_by_games'
            }
        )
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on game and rally detection quality."""
        hr_data = df['heart_rate'].dropna()
        completeness = len(hr_data) / len(df)
        
        if result > 0:
            # Confidence based on reasonableness of rallies per game
            # Typical range is 5-50 rallies per game
            if 5 <= result <= 50:
                reasonableness = 1.0
            else:
                reasonableness = max(0.3, 1.0 - abs(result - 25) * 0.02)
            
            return min(completeness * reasonableness, 1.0)
        
        return completeness * 0.5

class RestBetweenGamesDetector(BaseMetricDetector):
    """Detects rest periods between games."""
    
    def __init__(self):
        super().__init__("rest_between_games", MetricType.TEMPORAL)
        self.algorithm_version = "1.0"
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate', 'timestamp']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Detect rest periods between games."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing required data fields'}
            )
        
        hr_data = df['heart_rate'].dropna()
        if len(hr_data) < 50:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Insufficient heart rate data'}
            )
        
        # Calculate baseline heart rate
        baseline_hr = hr_data.quantile(0.2)
        rest_threshold = baseline_hr + (hr_data.max() - baseline_hr) * 0.15
        
        # Find rest periods
        below_threshold = hr_data < rest_threshold
        
        # Group consecutive rest periods
        rest_periods = []
        current_start = None
        
        for i, is_rest in enumerate(below_threshold):
            if is_rest and current_start is None:
                current_start = i
            elif not is_rest and current_start is not None:
                if i - current_start >= 3:  # Minimum rest duration
                    rest_periods.append((current_start, i))
                current_start = None
        
        if not rest_periods:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'No rest periods detected'}
            )
        
        # Calculate rest period durations
        rest_durations = []
        for start_idx, end_idx in rest_periods:
            # Calculate duration using time_diff if available
            if 'time_diff' in df.columns:
                duration = (end_idx - start_idx) * df['time_diff'].mean() / 60
            else:
                # Fallback: calculate from timestamps
                duration = (df['timestamp'].iloc[end_idx] - df['timestamp'].iloc[start_idx]).total_seconds() / 60
            rest_durations.append(duration)
        
        # Filter for game breaks (>2 minutes)
        game_breaks = [d for d in rest_durations if d > 2.0]
        
        if not game_breaks:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'No game breaks detected'}
            )
        
        avg_rest_between_games = np.mean(game_breaks)
        
        confidence = self.get_confidence_score(df, avg_rest_between_games)
        
        return MetricResult(
            metric_name=self.metric_name,
            value=avg_rest_between_games,
            confidence=confidence,
            metadata={
                'game_breaks': len(game_breaks),
                'game_break_durations': game_breaks,
                'min_game_break': min(game_breaks),
                'max_game_break': max(game_breaks),
                'algorithm': 'game_break_analysis'
            }
        )
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on game break detection quality."""
        hr_data = df['heart_rate'].dropna()
        completeness = len(hr_data) / len(df)
        
        if result > 0:
            # Confidence based on reasonableness of game break duration
            # Typical range is 1-5 minutes
            if 1.0 <= result <= 5.0:
                reasonableness = 1.0
            else:
                reasonableness = max(0.3, 1.0 - abs(result - 3.0) * 0.1)
            
            return min(completeness * reasonableness, 1.0)
        
        return completeness * 0.5

# Enhanced accelerometer-based detectors
class AccelerometerShotDetector(BaseMetricDetector):
    """Detects shots using accelerometer data."""
    
    def __init__(self):
        super().__init__("shots_detected", MetricType.COUNT)
        self.algorithm_version = "1.0"
    
    def get_required_data_fields(self) -> List[str]:
        return ['accelerometer_x', 'accelerometer_y', 'accelerometer_z', 'timestamp']
    
    def get_optional_data_fields(self) -> List[str]:
        return ['heart_rate', 'cadence']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Detect shots using accelerometer data."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing accelerometer data'}
            )
        
        # Calculate magnitude of acceleration
        accel_magnitude = np.sqrt(
            df['accelerometer_x']**2 + 
            df['accelerometer_y']**2 + 
            df['accelerometer_z']**2
        )
        
        # Find peaks in acceleration (shots)
        from scipy.signal import find_peaks
        
        # Use adaptive threshold based on data
        threshold = accel_magnitude.mean() + accel_magnitude.std() * 2
        
        peaks, properties = find_peaks(
            accel_magnitude,
            height=threshold,
            distance=10  # Minimum 10 samples between shots
        )
        
        shots = []
        for peak in peaks:
            shots.append({
                'timestamp': df.iloc[peak]['timestamp'],
                'acceleration': accel_magnitude.iloc[peak],
                'intensity': properties['peak_heights'][list(peaks).index(peak)]
            })
        
        confidence = self.get_confidence_score(df, len(shots))
        
        return MetricResult(
            metric_name=self.metric_name,
            value=len(shots),
            confidence=confidence,
            metadata={
                'shots': shots,
                'avg_acceleration': accel_magnitude.mean(),
                'max_acceleration': accel_magnitude.max(),
                'algorithm': 'accelerometer_peak_detection'
            }
        )
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on accelerometer data quality."""
        accel_fields = ['accelerometer_x', 'accelerometer_y', 'accelerometer_z']
        available_fields = [field for field in accel_fields if field in df.columns]
        
        if len(available_fields) == 3:
            completeness = 1.0
        else:
            completeness = len(available_fields) / 3.0
        
        if result > 0:
            # Confidence based on shot count reasonableness
            # Typical range is 50-500 shots per session
            if 50 <= result <= 500:
                reasonableness = 1.0
            else:
                reasonableness = max(0.3, 1.0 - abs(result - 200) * 0.001)
            
            return min(completeness * reasonableness, 1.0)
        
        return completeness * 0.5

if __name__ == "__main__":
    # Test the additional detectors
    from core.metrics_framework import MetricsFramework
    
    framework = MetricsFramework()
    
    # Register all detectors
    framework.register_detector(SessionDurationDetector())
    framework.register_detector(PlayingTimeDetector())
    framework.register_detector(LongestRallyDetector())
    framework.register_detector(RalliesPerGameDetector())
    framework.register_detector(RestBetweenGamesDetector())
    framework.register_detector(AccelerometerShotDetector())
    
    print("All available metrics:", framework.get_available_metrics())
