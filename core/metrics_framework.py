
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

def calculate_hr_zones(df: pd.DataFrame, max_hr: Optional[float] = None) -> Tuple[pd.DataFrame, float]:
    """
    Calculate HR zones for all data points.
    
    Zones:
    - Zone 0: Below 50% max HR (out of zones)
    - Zone 1: 50-60% max HR (Recovery/Rest)
    - Zone 2: 60-70% max HR (Active Recovery)
    - Zone 3: 70-80% max HR (Aerobic/Moderate)
    - Zone 4: 80-90% max HR (Anaerobic/Hard)
    - Zone 5: 90-100% max HR (Maximum)
    
    Returns:
        DataFrame with 'hr_zone' column added
        Estimated or provided max_hr
    """
    if 'heart_rate' not in df.columns:
        logger.error("heart_rate column required for zone calculation")
        return df, max_hr or 200
    
    hr_data = df['heart_rate'].dropna()
    
    if max_hr is None:
        # Estimate max HR from session data (observed max + 5% buffer)
        if len(hr_data) > 0:
            observed_max = hr_data.max()
            max_hr = observed_max * 1.05  # Add 5% buffer
            logger.info(f"Estimated max HR: {max_hr:.1f} (from observed max: {observed_max:.1f})")
        else:
            max_hr = 200  # Default fallback
    
    def assign_zone(hr: float) -> int:
        """Assign HR zone based on percentage of max HR."""
        if pd.isna(hr):
            return 0
        
        pct = (hr / max_hr) * 100
        
        if pct < 50:
            return 0  # Below zones
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
    
    df = df.copy()
    df['hr_zone'] = df['heart_rate'].apply(assign_zone)
    
    return df, max_hr

class MetricType(Enum):
    """Types of metrics that can be detected."""
    TEMPORAL = "temporal"  # Time-based metrics (duration, timing)
    COUNT = "count"        # Counting metrics (number of events)
    INTENSITY = "intensity" # Intensity-based metrics
    MOVEMENT = "movement"   # Movement-based metrics
    COMPOSITE = "composite" # Metrics combining multiple data sources
    PHYSIOLOGICAL = "physiological"  # Physiological metrics (heart rate, etc.)

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
        # Warm-up: HR spike followed by stabilization within first 5 mins
        # HR should not exceed 160 bpm during warm-up
        
        baseline_hr = hr_data.iloc[:10].mean()
        max_search_seconds = 300  # Only check first 5 minutes
        max_search_points = min(300, len(hr_data))  # 5 minutes max
        
        # Find first significant HR spike (>20 bpm increase from baseline)
        spike_threshold = baseline_hr + 20
        warmup_spike_idx = None
        
        for i in range(min(300, len(hr_data))):
            if hr_data.iloc[i] >= spike_threshold and hr_data.iloc[i] < 160:
                warmup_spike_idx = i
                break
        
        if warmup_spike_idx is None:
            # No clear spike, use 5 minutes as default
            warmup_end_idx = 300
        else:
            # Look for stabilization after spike (HR within 10 bpm range)
            spike_hr = hr_data.iloc[warmup_spike_idx]
            stabilized = False
            
            for i in range(warmup_spike_idx + 1, min(warmup_spike_idx + 60, len(hr_data))):
                current_hr = hr_data.iloc[i]
                if abs(current_hr - spike_hr) < 10:
                    stabilized = True
                    warmup_end_idx = i
                    break
            
            if not stabilized:
                warmup_end_idx = warmup_spike_idx + 60  # 1 minute after spike
            
            # Ensure max 5 minutes
            warmup_end_idx = min(warmup_end_idx, 300)
        
        # Ensure minimum 2 minutes
        warmup_end_idx = max(warmup_end_idx, 120)
        
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
                'spike_threshold': spike_threshold,
                'algorithm': 'warm_up_v1.3_spike_stabilization'
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
    """Detects rallies using zone-based transition detection."""
    
    def __init__(self):
        super().__init__("number_of_rallies", MetricType.COUNT)
        self.algorithm_version = "3.2"  # Drop-based detection (1 bpm drop, 1+ seconds sustained)
    
    def get_required_data_fields(self) -> List[str]:
        return ['heart_rate', 'timestamp']
    
    def get_optional_data_fields(self) -> List[str]:
        return ['cadence', 'speed', 'accelerometer_x', 'accelerometer_y', 'accelerometer_z']
    
    def detect(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> MetricResult:
        """Detect rallies using zone-based transition detection."""
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
        
        # Calculate HR zones
        df_with_zones, max_hr = calculate_hr_zones(df)
        
        if 'hr_zone' not in df_with_zones.columns:
            return MetricResult(
                metric_name=self.metric_name,
                value=0,
                confidence=0.0,
                metadata={'error': 'Failed to calculate HR zones'}
            )
        
        # IMPROVED RALLY DETECTION: Spike-based within high-intensity zones
        # In squash, HR stays elevated (zone 3-5) throughout, but spikes higher during rallies
        # Approach: Detect significant HR spikes above the baseline during active play
        
        hr_values = hr_data.values
        initial_rallies = []
        
        # DROP-BASED RALLY DETECTION (v3.2) - Ultra Sensitive
        # During game periods, ANY drop of 1+ bpm sustained for 1+ seconds = rally boundary
        # Expected: 60-120 rallies for 81-minute session (15-30 per game × 5 games)
        
        # Use rolling average to smooth HR data
        hr_smooth = pd.Series(hr_values).rolling(window=10, center=True).mean().fillna(method='bfill').fillna(method='ffill').values
        
        # Detect drops: 1+ bpm drop, sustained for 1+ seconds
        drop_threshold = 1  # Only 1 bpm drop needed
        min_sustained_duration = 1  # Must stay down for at least 1 second
        
        rally_boundaries = []
        in_drop = False
        drop_start_idx = None
        peak_hr_before_drop = None
        
        for i in range(10, len(hr_values) - 10):
            current_hr = hr_smooth[i]
            
            # Track peak HR in recent window (look back 15 seconds)
            lookback = max(0, i - 15)
            recent_max = hr_smooth[lookback:i].max()
            
            # Detect drop from recent peak
            drop_amount = recent_max - current_hr
            
            if drop_amount >= drop_threshold:
                # Start of a potential drop
                if not in_drop:
                    in_drop = True
                    drop_start_idx = i
                    peak_hr_before_drop = recent_max
            else:
                # Check if we're coming out of a sustained drop
                if in_drop:
                    drop_duration = i - drop_start_idx
                    
                    # If drop was sustained for 3+ seconds, it's a valid rally boundary
                    if drop_duration >= min_sustained_duration:
                        # Only add if not too close to previous boundary
                        if len(rally_boundaries) == 0 or drop_start_idx - rally_boundaries[-1] >= 3:
                            rally_boundaries.append(drop_start_idx)
                            logger.debug(f"Rally boundary at {drop_start_idx}: drop of {peak_hr_before_drop - hr_smooth[drop_start_idx]:.1f} bpm for {drop_duration}s")
                    
                    in_drop = False
                    drop_start_idx = None
                    peak_hr_before_drop = None
        
        # Sort boundaries and create rallies
        rally_boundaries = sorted(set(rally_boundaries))
        
        # Create rally segments from boundaries
        warmup_samples = min(300, len(hr_values) // 4)
        boundaries = [warmup_samples] + rally_boundaries + [len(hr_values)]
        
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1]
            duration = end_idx - start_idx
            
            # Rally must be between 5 seconds and 2 minutes
            if 5 <= duration <= 120:
                initial_rallies.append((start_idx, end_idx))
        
        logger.info(f"Drop-based detection (v3.2): {len(rally_boundaries)} boundaries found, {len(initial_rallies)} rallies")
        
        # Step 2: DON'T split further - the drop-based detection should give us the right number
        rally_periods = initial_rallies.copy()
        
        # Step 3: Apply minimum separation more carefully
        # Instead of merging rallies, just filter out boundaries that are too close together
        # This preserves the rally count better
        min_rally_duration = 2  # Minimum 2 seconds per rally (allows for very short rallies)
        filtered_rally_periods = []
        
        for start_idx, end_idx in rally_periods:
            duration = end_idx - start_idx
            if duration >= min_rally_duration:  # Only keep rallies that are long enough
                filtered_rally_periods.append((start_idx, end_idx))
        
        logger.info(f"After min duration filter ({min_rally_duration}s): {len(filtered_rally_periods)} rallies")
        rally_periods = filtered_rally_periods
        
        # Step 4: Filter by duration (final validation)
        filtered_rallies = []
        for start_idx, end_idx in rally_periods:
            duration_points = end_idx - start_idx
            if 5 <= duration_points <= 300:  # Final cap at 5 minutes
                filtered_rallies.append((start_idx, end_idx))
        
        logger.info(f"Spike-based rally detection (with peak splitting): {len(filtered_rallies)} rallies detected from {len(initial_rallies)} initial")
        
        # Convert to rally information
        rallies = []
        for start_idx, end_idx in filtered_rallies:
            actual_start_idx = hr_data.index[start_idx]
            actual_end_idx = hr_data.index[end_idx-1] if end_idx < len(hr_data) else hr_data.index[-1]
            
            # Calculate duration
            if isinstance(actual_start_idx, (int, np.integer)) and isinstance(actual_end_idx, (int, np.integer)):
                rally_duration = (actual_end_idx - actual_start_idx) * df['time_diff'].mean() / 60
            else:
                start_int = int(actual_start_idx)
                end_int = int(actual_end_idx)
                rally_duration = (end_int - start_int) * df['time_diff'].mean() / 60
            
            avg_hr = hr_data.iloc[start_idx:end_idx].mean()
            max_hr = hr_data.iloc[start_idx:end_idx].max()
            
            # Calculate avg zone if available
            if 'hr_zone' in df_with_zones.columns:
                avg_zone = df_with_zones['hr_zone'].iloc[start_idx:end_idx].mean()
            else:
                avg_zone = 0
            
            rallies.append({
                'start_time': actual_start_idx,
                'end_time': actual_end_idx,
                'duration_minutes': rally_duration,
                'avg_heart_rate': avg_hr,
                'max_heart_rate': max_hr,
                'avg_zone': avg_zone,
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
                'algorithm': 'drop_based_v3.2_1bpm_1s_sustained',
                'max_hr_used': max_hr
            }
        )
    
    def _split_long_rally(self, hr_data: pd.Series, df_with_zones: pd.DataFrame, start_idx: int, end_idx: int, min_samples_per_minute: float = 1.0) -> List[Tuple[int, int]]:
        """
        Split a long rally into multiple shorter rallies using HR minima.
        
        Looks for significant HR drops (>10 bpm for >3 seconds) within a sustained high-intensity period.
        These natural breakpoints indicate where rallies likely start/end.
        """
        if end_idx - start_idx < 60:
            return [(start_idx, end_idx)]
        
        hr_segment = hr_data.iloc[start_idx:end_idx].values
        if 'hr_zone' in df_with_zones.columns:
            zone_segment = df_with_zones['hr_zone'].iloc[start_idx:end_idx].values
        else:
            zone_segment = np.ones(end_idx - start_idx) * 3  # Default to zone 3
        
        # Calculate HR derivative to find peaks and valleys
        hr_diff = np.diff(hr_segment)
        
        # Find significant drops (potential rally boundaries) - MORE SENSITIVE
        # A drop is significant if HR decreases by >5 bpm and stays down for >2 seconds
        min_drop_bpm = 5  # Lower threshold for more splitting
        min_drop_duration = 2 * min_samples_per_minute  # 2 seconds in samples
        
        drop_points = []
        current_drop_start = None
        
        for i in range(len(hr_diff)):
            if hr_diff[i] < -min_drop_bpm:  # Significant drop
                if current_drop_start is None:
                    current_drop_start = i
            elif current_drop_start is not None:
                # Check if drop was sustained
                if i - current_drop_start >= min_drop_duration:
                    # Check if it stayed down (HR didn't immediately recover)
                    if i < len(hr_segment) - 5:
                        next_5_avg = hr_segment[i:i+5].mean()
                        drop_bottom = hr_segment[current_drop_start:i].min()
                        
                        # If HR is still significantly below the drop start
                        if next_5_avg < hr_segment[current_drop_start] - min_drop_bpm:
                            drop_points.append(start_idx + current_drop_start)
                            logger.debug(f"Found split point at index {start_idx + current_drop_start}, drop of {hr_segment[current_drop_start] - drop_bottom:.1f} bpm")
                current_drop_start = None
        
        # Also check for zone transitions within the rally
        # If zone drops significantly, that's likely a split point
        for i in range(1, len(zone_segment)):
            if zone_segment[i] < zone_segment[i-1] and zone_segment[i] < 3:
                # Significant zone drop, potential split
                if i not in drop_points:
                    drop_points.append(start_idx + i)
        
        # Create rally segments from drop points
        if not drop_points:
            # No natural splits found, return as one rally
            return [(start_idx, end_idx)]
        
        split_rallies = []
        previous_end = start_idx
        
        for drop_point in drop_points:
            if drop_point - previous_end >= 5:  # Minimum 5 seconds per rally (more aggressive)
                split_rallies.append((previous_end, drop_point))
                previous_end = drop_point
        
        # Add final segment
        if end_idx - previous_end >= 5:
            split_rallies.append((previous_end, end_idx))
        
        logger.info(f"Split long rally ({end_idx - start_idx} seconds) into {len(split_rallies)} rallies")
        return split_rallies if len(split_rallies) > 1 else [(start_idx, end_idx)]
    
    def _enforce_minimum_separation(self, rally_periods: List[Tuple[int, int]], min_gap_seconds: int = 2) -> List[Tuple[int, int]]:
        """
        Enforce minimum separation between rallies or merge if too close.
        
        If two rallies are separated by less than min_gap_seconds, merge them into one.
        This prevents over-counting due to brief HR drops during continuous play.
        """
        if len(rally_periods) <= 1:
            return rally_periods
        
        # Sort by start time
        sorted_rallies = sorted(rally_periods, key=lambda x: x[0])
        
        merged_rallies = []
        current_start, current_end = sorted_rallies[0]
        
        for next_start, next_end in sorted_rallies[1:]:
            gap_seconds = next_start - current_end
            
            if gap_seconds < min_gap_seconds:
                # Rallies too close, merge them
                current_end = next_end
                logger.debug(f"Merging rallies with {gap_seconds}s gap: ({current_start}, {next_end})")
            else:
                # Gap is sufficient, save current rally and move to next
                merged_rallies.append((current_start, current_end))
                current_start, current_end = next_start, next_end
        
        # Add final rally
        merged_rallies.append((current_start, current_end))
        
        if len(merged_rallies) < len(rally_periods):
            logger.info(f"Enforced separation: {len(rally_periods)} rallies → {len(merged_rallies)} rallies")
        
        return merged_rallies
    
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
        completeness = len(hr_data) / len(df)
        
        if result > 0:
            # For zone-based detection, ideal rally count is 50-150 for an 81-minute session
            # Normalize based on session duration
            session_duration = df['cumulative_time'].iloc[-1] / 60 if 'cumulative_time' in df.columns else 81
            
            # Estimate expected rally count (roughly 1 rally per minute for normal session)
            expected_rallies = session_duration * 1.2
            rally_ratio = result / expected_rallies if expected_rallies > 0 else 0
            
            # Confidence is high if rally count is reasonable (50-200% of expected)
            if 0.5 <= rally_ratio <= 2.0:
                rally_confidence = 1.0
            else:
                # Penalize if way too few or too many
                rally_confidence = max(0.4, 1.0 - abs(rally_ratio - 1.0) * 0.3)
            
            return min(completeness * rally_confidence, 1.0)
        
        return completeness * 0.3

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
