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
    """Detects total playing time using HR zones (Zone 3, 4, or 5)."""
    
    def __init__(self):
        super().__init__("total_playing_time", MetricType.TEMPORAL)
        self.algorithm_version = "2.0"  # Zone-based approach
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate', 'timestamp']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Calculate total playing time from HR zones."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing required data fields'}
            )
        
        # Calculate HR zones
        from core.metrics_framework import calculate_hr_zones
        df_with_zones, max_hr = calculate_hr_zones(df)
        
        if 'hr_zone' not in df_with_zones.columns:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Failed to calculate HR zones'}
            )
        
        # Calculate sampling rate for time conversion
        if 'time_diff' in df.columns and df['time_diff'].mean() > 0:
            samples_per_minute = 60.0 / df['time_diff'].mean()
        else:
            # Estimate from timestamps
            time_diffs = (df['timestamp'].diff().dt.total_seconds()).dropna()
            if len(time_diffs) > 0 and time_diffs.mean() > 0:
                samples_per_minute = 60.0 / time_diffs.mean()
            else:
                samples_per_minute = 1.0
        
        # Sum time spent in Zone 3, 4, or 5 (active play)
        high_zone_points = df_with_zones['hr_zone'].isin([3, 4, 5]).sum()
        total_playing_time = high_zone_points / samples_per_minute
        
        # Calculate zone distribution
        zone_counts = df_with_zones['hr_zone'].value_counts().to_dict()
        
        confidence = self.get_confidence_score(df, total_playing_time)
        
        return MetricResult(
            metric_name=self.metric_name,
            value=total_playing_time,
            confidence=confidence,
            metadata={
                'algorithm': 'hr_zone_based_v2.0',
                'max_hr_used': max_hr,
                'zone_distribution': zone_counts,
                'high_zone_points': high_zone_points,
                'total_points': len(df_with_zones)
            }
        )
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on playing time ratio."""
        hr_data = df['heart_rate'].dropna()
        completeness = len(hr_data) / len(df)
        
        if result > 0:
            # Confidence based on playing time ratio
            session_duration = df['cumulative_time'].iloc[-1] / 60 if 'cumulative_time' in df.columns else 0
            if session_duration > 0:
                playing_ratio = result / session_duration
                # Reasonable playing ratio is 20-60% of session time
                if 0.2 <= playing_ratio <= 0.6:
                    return completeness
                else:
                    # Penalize extreme ratios
                    ratio_penalty = abs(playing_ratio - 0.4) / 0.4  # Distance from ideal 40%
                    return completeness * max(0.3, 1.0 - ratio_penalty)
        
        return completeness * 0.3

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
        
        # Filter rallies: cap at 120 seconds (2 minutes) - typical range is 5-90 seconds
        # Rallies longer than 2 minutes are likely multiple rallies merged together
        max_rally_duration_minutes = 2.0  # 120 seconds
        filtered_rallies = [r for r in rallies if r['duration_minutes'] <= max_rally_duration_minutes]
        
        if not filtered_rallies:
            # If all rallies were too long, return 0
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'No rallies under 2 minute cap', 'total_rallies': len(rallies)}
            )
        
        # Find longest rally from filtered list
        longest_rally = max(filtered_rallies, key=lambda r: r['duration_minutes'])
        
        # Get actual duration (do not multiply)
        longest_rally_duration = longest_rally['duration_minutes']
        
        confidence = self.get_confidence_score(df, longest_rally_duration)
        
        return MetricResult(
            metric_name=self.metric_name,
            value=longest_rally_duration,
            confidence=confidence,
            metadata={
                'longest_rally': longest_rally,
                'total_rallies': len(rallies),
                'filtered_rallies': len(filtered_rallies),
                'algorithm': 'max_rally_duration_capped_at_120s',
                'note': 'Longest rally duration capped at 120 seconds'
            }
        )
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on rally detection quality."""
        hr_data = df['heart_rate'].dropna()
        completeness = len(hr_data) / len(df)
        
        if result > 0:
            # Confidence based on longest rally reasonableness
            # Typical range: 5-90 seconds, max reasonable: 120 seconds
            # Rallies in this range are considered reasonable
            if result <= 2.0:  # <= 120 seconds
                reasonableness = 1.0
            else:
                # Penalize for exceeding reasonable maximum
                reasonableness = 0.5
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

class RestTimeDetector(BaseMetricDetector):
    """Detects total rest time using HR zones (Zone 1 or 2, excluding warm-up/cool-down)."""
    
    def __init__(self):
        super().__init__("total_rest_time", MetricType.TEMPORAL)
        self.algorithm_version = "1.0"
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate', 'timestamp']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Calculate total rest time from HR zones."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing required data fields'}
            )
        
        # Calculate HR zones
        from core.metrics_framework import calculate_hr_zones
        df_with_zones, max_hr = calculate_hr_zones(df)
        
        if 'hr_zone' not in df_with_zones.columns:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Failed to calculate HR zones'}
            )
        
        # Calculate sampling rate for time conversion
        if 'time_diff' in df.columns and df['time_diff'].mean() > 0:
            samples_per_minute = 60.0 / df['time_diff'].mean()
        else:
            # Estimate from timestamps
            time_diffs = (df['timestamp'].diff().dt.total_seconds()).dropna()
            if len(time_diffs) > 0 and time_diffs.mean() > 0:
                samples_per_minute = 60.0 / time_diffs.mean()
            else:
                samples_per_minute = 1.0
        
        # Get warm-up and cool-down data points from context
        warmup_points = 0
        cooldown_points = 0
        
        # Get warm-up info if available
        warmup_result = context.get('warmup_result') if context else None
        if warmup_result and warmup_result.data_points:
            start_idx, end_idx = warmup_result.data_points[0]
            warmup_points = end_idx - start_idx
        
        # Get cool-down info if available
        cooldown_result = context.get('cooldown_result') if context else None
        if cooldown_result and cooldown_result.data_points:
            start_idx, end_idx = cooldown_result.data_points[0]
            cooldown_points = end_idx - start_idx
        
        # Sum time spent in Zone 1 or 2 (rest periods)
        low_zone_points = df_with_zones['hr_zone'].isin([1, 2]).sum()
        
        # Roughly estimate warm-up/cool-down portion in low zones
        # This is a simplification - could be improved with more precise tracking
        warmup_cooldown_low_zone_estimate = (warmup_points + cooldown_points) * 0.5
        
        # Calculate actual rest time (excluding warm-up/cool-down portions)
        actual_rest_points = low_zone_points - warmup_cooldown_low_zone_estimate
        actual_rest_points = max(0, actual_rest_points)  # Ensure non-negative
        
        total_rest_time = actual_rest_points / samples_per_minute
        
        confidence = self.get_confidence_score(df, total_rest_time)
        
        return MetricResult(
            metric_name=self.metric_name,
            value=total_rest_time,
            confidence=confidence,
            metadata={
                'algorithm': 'hr_zone_based_v1.0',
                'max_hr_used': max_hr,
                'total_low_zone_points': low_zone_points,
                'warmup_cooldown_estimate': warmup_cooldown_low_zone_estimate,
                'actual_rest_points': actual_rest_points
            }
        )
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on rest time reasonableness."""
        hr_data = df['heart_rate'].dropna()
        completeness = len(hr_data) / len(df)
        
        if result > 0:
            # Confidence based on rest time ratio
            session_duration = df['cumulative_time'].iloc[-1] / 60 if 'cumulative_time' in df.columns else 0
            if session_duration > 0:
                rest_ratio = result / session_duration
                # Reasonable rest ratio is 30-60% of session time
                if 0.3 <= rest_ratio <= 0.6:
                    return completeness
                else:
                    # Penalize extreme ratios
                    ratio_penalty = abs(rest_ratio - 0.45) / 0.45  # Distance from ideal 45%
                    return completeness * max(0.3, 1.0 - ratio_penalty)
        
        return completeness * 0.3

class AvgPlayingHeartRateDetector(BaseMetricDetector):
    """Calculates average heart rate during active play (Zones 3, 4, 5)."""
    
    def __init__(self):
        super().__init__("avg_playing_heart_rate", MetricType.PHYSIOLOGICAL)
        self.algorithm_version = "1.0"
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Calculate average HR during play."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing required data fields'}
            )
        
        from core.metrics_framework import calculate_hr_zones
        df_with_zones, max_hr = calculate_hr_zones(df)
        
        if 'hr_zone' not in df_with_zones.columns:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Failed to calculate HR zones'}
            )
        
        # Filter to playing zones (3, 4, 5)
        playing_mask = df_with_zones['hr_zone'].isin([3, 4, 5])
        playing_hr = df_with_zones.loc[playing_mask, 'heart_rate'].dropna()
        
        if len(playing_hr) == 0:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'No playing zone data'}
            )
        
        avg_playing_hr = playing_hr.mean()
        confidence = len(playing_hr) / len(df)  # Fraction of session in playing zones
        
        return MetricResult(
            metric_name=self.metric_name,
            value=round(avg_playing_hr, 1),
            confidence=confidence,
            metadata={
                'algorithm': 'zone_based_v1.0',
                'max_hr_used': max_hr,
                'playing_samples': len(playing_hr),
                'total_samples': len(df)
            }
        )

class AvgRestHeartRateDetector(BaseMetricDetector):
    """Calculates average heart rate during rest periods (Zones 1, 2)."""
    
    def __init__(self):
        super().__init__("avg_rest_heart_rate", MetricType.PHYSIOLOGICAL)
        self.algorithm_version = "1.0"
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Calculate average HR during rest."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing required data fields'}
            )
        
        from core.metrics_framework import calculate_hr_zones
        df_with_zones, max_hr = calculate_hr_zones(df)
        
        if 'hr_zone' not in df_with_zones.columns:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Failed to calculate HR zones'}
            )
        
        # Filter to rest zones (1, 2)
        rest_mask = df_with_zones['hr_zone'].isin([1, 2])
        rest_hr = df_with_zones.loc[rest_mask, 'heart_rate'].dropna()
        
        if len(rest_hr) == 0:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'No rest zone data'}
            )
        
        avg_rest_hr = rest_hr.mean()
        confidence = len(rest_hr) / len(df)  # Fraction of session in rest zones
        
        return MetricResult(
            metric_name=self.metric_name,
            value=round(avg_rest_hr, 1),
            confidence=confidence,
            metadata={
                'algorithm': 'zone_based_v1.0',
                'max_hr_used': max_hr,
                'rest_samples': len(rest_hr),
                'total_samples': len(df)
            }
        )

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
