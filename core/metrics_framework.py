"""
Squash Performance Analysis - Modular Metrics Framework

A flexible, extensible framework for detecting and analyzing squash performance metrics.
Each metric is implemented as a separate module for easy iteration and improvement.
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics that can be detected."""
    TEMPORAL = "temporal"  # Time-based metrics (duration, timing)
    COUNT = "count"        # Counting metrics (number of events)
    INTENSITY = "intensity" # Intensity-based metrics
    MOVEMENT = "movement"   # Movement-based metrics
    COMPOSITE = "composite" # Metrics combining multiple data sources

@dataclass
class MetricResult:
    """Standardized result format for all metrics."""
    metric_name: str
    value: Any
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any]
    data_points: Optional[List[Tuple[int, int]]] = None  # Start/end indices for events
    algorithm_version: str = "1.0"

class BaseMetricDetector(ABC):
    """Base class for all metric detectors."""
    
    def __init__(self, metric_name: str, metric_type: MetricType):
        self.metric_name = metric_name
        self.metric_type = metric_type
        self.algorithm_version = "1.0"
        self.required_data_fields = []
        self.optional_data_fields = []
    
    @abstractmethod
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Detect the metric from the data."""
        pass
    
    @abstractmethod
    def get_required_data_fields(self) -> List[str]:
        """Return list of required data fields for this metric."""
        pass
    
    def get_optional_data_fields(self) -> List[str]:
        """Return list of optional data fields that can improve this metric."""
        return []
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validate that required data fields are present."""
        required_fields = self.get_required_data_fields()
        missing_fields = [field for field in required_fields if field not in df.columns]
        
        if missing_fields:
            logger.warning(f"Missing required fields for {self.metric_name}: {missing_fields}")
            return False
        return True
    
    def format_time_duration(self, minutes: float) -> str:
        """Format duration in minutes to MM:SS format."""
        if minutes <= 0:
            return "0:00"
        
        total_seconds = int(minutes * 60)
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins}:{secs:02d}"
    
    def format_rounded_value(self, value: Any, metric_name: str) -> Any:
        """Format values based on metric type - round integers, keep decimals for durations."""
        if value is None:
            return value
        
        # Round up integer metrics
        integer_metrics = ['number_of_games', 'number_of_rallies', 'rallies_per_game', 'shots_detected']
        if metric_name in integer_metrics:
            return int(np.ceil(value)) if isinstance(value, (int, float)) else value
        
        # Keep decimal precision for duration metrics
        duration_metrics = ['warm_up_length', 'cool_down_length', 'total_session_duration', 
                           'total_playing_time', 'longest_rally_length', 'rest_between_games']
        if metric_name in duration_metrics:
            return round(value, 1) if isinstance(value, (int, float)) else value
        
        return value

class WarmUpDetector(BaseMetricDetector):
    """Detects warm-up period using heart rate patterns."""
    
    def __init__(self):
        super().__init__("warm_up_length", MetricType.TEMPORAL)
        self.algorithm_version = "1.1"
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate', 'timestamp']
    
    def get_optional_data_fields(self) -> List[str]:
        return ['cadence', 'speed', 'accelerometer_x', 'accelerometer_y', 'accelerometer_z']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Detect warm-up period based on heart rate patterns."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing required data fields'}
            )
        
        hr_data = df['heart_rate'].dropna()
        if len(hr_data) < 10:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Insufficient heart rate data'}
            )
        
        # Calculate rolling statistics
        window_size = min(30, len(hr_data) // 4)
        rolling_mean = hr_data.rolling(window=window_size, center=True).mean()
        rolling_std = hr_data.rolling(window=window_size, center=True).std()
        
        # Find period where HR is increasing and variability is low
        hr_diff = rolling_mean.diff()
        low_variability = rolling_std < rolling_std.quantile(0.3)
        increasing_hr = hr_diff > 0
        
        # Improved warm-up detection
        # Warm-up: first 3-10 minutes where HR gradually increases
        baseline_hr = hr_data.iloc[:10].mean()
        max_hr = hr_data.max()
        
        # Find where HR reaches 70% of max (typically end of warm-up)
        threshold_hr = baseline_hr + (max_hr - baseline_hr) * 0.3
        
        # Look in first 15% of session only
        max_search_points = int(len(hr_data) * 0.15)
        
        # Find first point where HR crosses threshold
        warmup_end_idx = None
        for i in range(min(100, max_search_points)):  # Check first points
            if hr_data.iloc[i] >= threshold_hr:
                warmup_end_idx = i
                break
        
        # If no threshold crossed, use 10% of session as default
        if warmup_end_idx is None:
            warmup_end_idx = min(int(len(hr_data) * 0.1), 600)  # Max 10 minutes
        
        # Ensure warm-up is reasonable (3-10 minutes)
        if warmup_end_idx < 180:  # Less than 3 minutes
            warmup_end_idx = 180  # Minimum 3 minutes
        
        if warmup_end_idx > 600:  # More than 10 minutes
            warmup_end_idx = 600  # Maximum 10 minutes
        
        warmup_start_idx = 0
        extended_start_int = warmup_start_idx
        warmup_end_int = warmup_end_idx
        
        # Calculate duration
        if 'time_diff' in df.columns:
            warmup_duration = (warmup_end_int - extended_start_int) * df['time_diff'].mean() / 60
        else:
            warmup_duration = (warmup_end_int - extended_start_int) / 60
        
        confidence = self.get_confidence_score(df, warmup_duration)
        
        return MetricResult(
            metric_name=self.metric_name,
            value=warmup_duration,
            confidence=confidence,
            metadata={
                'start_time': df['timestamp'].iloc[warmup_start_idx],
                'end_time': df['timestamp'].iloc[warmup_end_int],
                'baseline_hr': baseline_hr,
                'threshold_hr': threshold_hr,
                'algorithm': 'warm_up_v1.2_improved'
            },
            data_points=[(warmup_start_idx, warmup_end_int)]
        )
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on data quality and pattern strength."""
        hr_data = df['heart_rate'].dropna()
        
        # Base confidence on data completeness
        completeness = len(hr_data) / len(df)
        
        # Adjust based on pattern strength
        if result > 0:
            pattern_strength = min(result / 10.0, 1.0)  # Normalize to 0-1
            return min(completeness * pattern_strength, 1.0)
        
        return completeness * 0.5

class CoolDownDetector(BaseMetricDetector):
    """Detects cool-down period using heart rate decrease patterns."""
    
    def __init__(self):
        super().__init__("cool_down_length", MetricType.TEMPORAL)
        self.algorithm_version = "1.0"
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate', 'timestamp']
    
    def get_optional_data_fields(self) -> List[str]:
        return ['cadence', 'speed']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Detect cool-down period based on heart rate decrease patterns."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing required data fields'}
            )
        
        hr_data = df['heart_rate'].dropna()
        if len(hr_data) < 20:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Insufficient heart rate data'}
            )
        
        # Look for gradual HR decrease in the last portion of session
        # Cool-down typically occurs in last 20% of session
        cooldown_start_idx = int(len(hr_data) * 0.8)
        cooldown_data = hr_data.iloc[cooldown_start_idx:]
        
        if len(cooldown_data) < 10:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Insufficient data for cool-down detection'}
            )
        
        # Calculate rolling average to smooth the data
        window_size = min(10, len(cooldown_data) // 3)
        rolling_mean = cooldown_data.rolling(window=window_size, center=True).mean()
        
        # Find period where HR is decreasing
        hr_diff = rolling_mean.diff()
        decreasing_hr = hr_diff < 0
        
        # Look for sustained decrease
        if decreasing_hr.sum() > len(decreasing_hr) * 0.6:  # 60% of points show decrease
            # Find the start of sustained decrease
            cooldown_start = cooldown_data.index[0]
            cooldown_end = hr_data.index[-1]
            
            # Calculate duration using time_diff if available
            if 'time_diff' in df.columns:
                cooldown_duration = (cooldown_end - cooldown_start) * df['time_diff'].mean() / 60
            else:
                # Fallback: calculate from timestamps
                cooldown_duration = (df['timestamp'].iloc[cooldown_end] - df['timestamp'].iloc[cooldown_start]).total_seconds() / 60
            
            confidence = self.get_confidence_score(df, cooldown_duration)
            
            return MetricResult(
                metric_name=self.metric_name,
                value=cooldown_duration,
                confidence=confidence,
                metadata={
                    'start_time': cooldown_start,
                    'end_time': cooldown_end,
                    'avg_heart_rate': cooldown_data.mean(),
                    'hr_decrease': hr_data.iloc[0] - hr_data.iloc[-1],
                    'algorithm': 'hr_decrease_analysis'
                },
                data_points=[(cooldown_start, cooldown_end)]
            )
        
        return MetricResult(
            metric_name=self.metric_name,
            value=0,
            confidence=0.0,
            metadata={'error': 'No cool-down pattern detected'}
        )
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on HR decrease pattern."""
        hr_data = df['heart_rate'].dropna()
        
        if result > 0:
            # Confidence based on HR decrease amount
            hr_decrease = hr_data.iloc[0] - hr_data.iloc[-1]
            decrease_strength = min(hr_decrease / 30.0, 1.0)  # Normalize to 0-1
            
            # Data completeness
            completeness = len(hr_data) / len(df)
            
            return min(completeness * decrease_strength, 1.0)
        
        return 0.0

class GameDetector(BaseMetricDetector):
    """Detects games by identifying longer rest periods between games vs rallies."""
    
    def __init__(self):
        super().__init__("number_of_games", MetricType.COUNT)
        self.algorithm_version = "1.0"
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate', 'timestamp']
    
    def get_optional_data_fields(self) -> List[str]:
        return ['cadence', 'speed']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Detect games by analyzing rest period durations."""
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
            # Ensure indices are numeric
            start_int = int(start_idx) if isinstance(start_idx, (int, np.integer)) else int(hr_data.index[start_idx])
            end_int = int(end_idx) if isinstance(end_idx, (int, np.integer)) else int(hr_data.index[end_idx])
            
            # Calculate duration using time_diff if available
            if 'time_diff' in df.columns:
                duration = (end_int - start_int) * df['time_diff'].mean() / 60
            else:
                # Fallback: calculate from timestamps
                duration = (df['timestamp'].iloc[end_int] - df['timestamp'].iloc[start_int]).total_seconds() / 60
            rest_durations.append(duration)
        
        # Distinguish game breaks (>2 minutes) from rally breaks (<30 seconds)
        game_break_threshold = 2.0  # minutes
        rally_break_threshold = 0.5  # minutes
        
        game_breaks = [d for d in rest_durations if d > game_break_threshold]
        rally_breaks = [d for d in rest_durations if d < rally_break_threshold]
        
        # Number of games = number of game breaks + 1
        num_games = len(game_breaks) + 1
        
        confidence = self.get_confidence_score(df, num_games)
        
        return MetricResult(
            metric_name=self.metric_name,
            value=num_games,
            confidence=confidence,
            metadata={
                'game_breaks': len(game_breaks),
                'rally_breaks': len(rally_breaks),
                'avg_game_break_duration': np.mean(game_breaks) if game_breaks else 0,
                'avg_rally_break_duration': np.mean(rally_breaks) if rally_breaks else 0,
                'algorithm': 'rest_period_analysis'
            }
        )
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on rest period pattern clarity."""
        hr_data = df['heart_rate'].dropna()
        
        if result > 0:
            # Confidence based on data completeness and pattern clarity
            completeness = len(hr_data) / len(df)
            
            # Pattern clarity based on number of games detected
            pattern_clarity = min(result / 5.0, 1.0)  # Normalize to 0-1
            
            return min(completeness * pattern_clarity, 1.0)
        
        return 0.0

class RallyDetector(BaseMetricDetector):
    """Detects rallies using heart rate and optional movement data."""
    
    def __init__(self):
        super().__init__("number_of_rallies", MetricType.COUNT)
        self.algorithm_version = "1.2"
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate', 'timestamp']
    
    def get_optional_data_fields(self) -> List[str]:
        return ['cadence', 'speed', 'accelerometer_x', 'accelerometer_y', 'accelerometer_z']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Detect rallies using heart rate and movement data."""
        if not self.validate_data(df):
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Missing required data fields'}
            )
        
        hr_data = df['heart_rate'].dropna()
        if len(hr_data) < 10:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Insufficient heart rate data'}
            )
        
        # Calculate baseline heart rate (excluding warm-up)
        warmup_info = context.get('warmup_info', {}) if context else {}
        if warmup_info.get('end_time', 0) > 0:
            baseline_hr = hr_data.iloc[warmup_info['end_time']:].quantile(0.2)
        else:
            baseline_hr = hr_data.quantile(0.2)
        
        # Define rally threshold (elevated HR above baseline)
        rally_threshold = baseline_hr + (hr_data.max() - baseline_hr) * 0.3
        
        # Find periods above threshold
        above_threshold = hr_data > rally_threshold
        
        # Group consecutive periods
        rally_periods = []
        current_start = None
        
        for i, is_rally in enumerate(above_threshold):
            if is_rally and current_start is None:
                current_start = i
            elif not is_rally and current_start is not None:
                # End of rally period
                if i - current_start >= 5:  # Minimum rally duration (5 data points)
                    rally_periods.append((current_start, i))
                current_start = None
        
        # Handle case where rally continues to end of data
        if current_start is not None and len(hr_data) - current_start >= 5:
            rally_periods.append((current_start, len(hr_data)))
        
        # Convert to rally information
        rallies = []
        for start_idx, end_idx in rally_periods:
            actual_start_idx = hr_data.index[start_idx]
            actual_end_idx = hr_data.index[end_idx-1] if end_idx < len(hr_data) else hr_data.index[-1]
            
            # Calculate duration - ensure indices are numeric
            if isinstance(actual_start_idx, (int, np.integer)) and isinstance(actual_end_idx, (int, np.integer)):
                rally_duration = (actual_end_idx - actual_start_idx) * df['time_diff'].mean() / 60
            else:
                # Use index difference for integer indices
                start_int = int(actual_start_idx)
                end_int = int(actual_end_idx)
                rally_duration = (end_int - start_int) * df['time_diff'].mean() / 60
            avg_hr = hr_data.iloc[start_idx:end_idx].mean()
            max_hr = hr_data.iloc[start_idx:end_idx].max()
            
            rallies.append({
                'start_time': actual_start_idx,
                'end_time': actual_end_idx,
                'duration_minutes': rally_duration,
                'avg_heart_rate': avg_hr,
                'max_heart_rate': max_hr,
                'intensity': self._calculate_intensity(hr_data.iloc[start_idx:end_idx])
            })
        
        confidence = self.get_confidence_score(df, len(rallies))
        
        return MetricResult(
            metric_name=self.metric_name,
            value=len(rallies),
            confidence=confidence,
            metadata={
                'rallies': rallies,
                'avg_rally_duration': np.mean([r['duration_minutes'] for r in rallies]) if rallies else 0,
                'longest_rally_duration': max([r['duration_minutes'] for r in rallies]) if rallies else 0,
                'total_rally_time': sum([r['duration_minutes'] for r in rallies]),
                'algorithm': 'hr_threshold_analysis'
            }
        )
    
    def _calculate_intensity(self, hr_segment: pd.Series) -> float:
        """Calculate intensity score for a rally segment."""
        if len(hr_segment) == 0:
            return 0
        
        avg_hr = hr_segment.mean()
        max_hr = hr_segment.max()
        
        intensity = (avg_hr - hr_segment.min()) / (max_hr - hr_segment.min()) if max_hr > hr_segment.min() else 0
        return min(intensity, 1.0)
    
    def get_confidence_score(self, df: pd.DataFrame, result: Any) -> float:
        """Calculate confidence based on rally detection quality."""
        hr_data = df['heart_rate'].dropna()
        
        if result > 0:
            # Confidence based on data completeness and rally count
            completeness = len(hr_data) / len(df)
            
            # Rally count confidence (more rallies = higher confidence)
            rally_confidence = min(result / 20.0, 1.0)  # Normalize to 0-1
            
            return min(completeness * rally_confidence, 1.0)
        
        return 0.0

class MetricsFramework:
    """Main framework for managing and running metric detectors."""
    
    def __init__(self):
        self.detectors = {}
        self.results = {}
    
    def register_detector(self, detector: BaseMetricDetector):
        """Register a metric detector."""
        self.detectors[detector.metric_name] = detector
        logger.info(f"Registered detector: {detector.metric_name} v{detector.algorithm_version}")
    
    def detect_all_metrics(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> Dict[str, MetricResult]:
        """Run all registered detectors on the data."""
        results = {}
        
        for metric_name, detector in self.detectors.items():
            try:
                result = detector.detect(df, context)
                results[metric_name] = result
                logger.info(f"Detected {metric_name}: {result.value} (confidence: {result.confidence:.2f})")
            except Exception as e:
                logger.error(f"Error detecting {metric_name}: {e}")
                results[metric_name] = MetricResult(
                    metric_name=metric_name,
                    value=None,
                    confidence=0.0,
                    metadata={'error': str(e)}
                )
        
        self.results = results
        return results
    
    def get_metric_result(self, metric_name: str) -> Optional[MetricResult]:
        """Get result for a specific metric."""
        return self.results.get(metric_name)
    
    def get_available_metrics(self) -> List[str]:
        """Get list of available metrics."""
        return list(self.detectors.keys())
    
    def get_metrics_by_type(self, metric_type: MetricType) -> List[str]:
        """Get metrics of a specific type."""
        return [name for name, detector in self.detectors.items() 
                if detector.metric_type == metric_type]

# Example usage and testing
if __name__ == "__main__":
    # Initialize framework
    framework = MetricsFramework()
    
    # Register detectors
    framework.register_detector(WarmUpDetector())
    framework.register_detector(CoolDownDetector())
    framework.register_detector(GameDetector())
    framework.register_detector(RallyDetector())
    
    print("Available metrics:", framework.get_available_metrics())
    print("Temporal metrics:", framework.get_metrics_by_type(MetricType.TEMPORAL))
    print("Count metrics:", framework.get_metrics_by_type(MetricType.COUNT))
