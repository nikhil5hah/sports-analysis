"""
Squash Performance Analysis - Event Detection Module

Algorithms to automatically identify key events in squash sessions:
- Warm-up periods
- Rallies and shots
- Rest periods
- Game boundaries
"""

import pandas as pd
import numpy as np
from scipy import signal
from scipy.stats import zscore
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class EventDetector:
    """Detects key events in squash performance data."""
    
    def __init__(self, hand_position: str = 'playing_hand', session_type: str = 'training'):
        self.hand_position = hand_position
        self.session_type = session_type
        self.events = {}
        
    def detect_warm_up(self, df: pd.DataFrame, heart_rate_col: str = 'heart_rate') -> Dict:
        """
        Detect warm-up period based on heart rate patterns.
        Warm-up typically shows gradual increase in HR with lower variability.
        """
        if heart_rate_col not in df.columns:
            logger.warning("Heart rate data not available for warm-up detection")
            return {'start_time': 0, 'end_time': 0, 'duration_minutes': 0}
        
        hr_data = df[heart_rate_col].dropna()
        if len(hr_data) < 10:
            return {'start_time': 0, 'end_time': 0, 'duration_minutes': 0}
        
        # Calculate rolling statistics
        window_size = min(30, len(hr_data) // 4)  # 30 points or 25% of data
        rolling_mean = hr_data.rolling(window=window_size, center=True).mean()
        rolling_std = hr_data.rolling(window=window_size, center=True).std()
        
        # Find period where HR is increasing and variability is low
        hr_diff = rolling_mean.diff()
        low_variability = rolling_std < rolling_std.quantile(0.3)
        increasing_hr = hr_diff > 0
        
        # Warm-up typically occurs in first 20% of session
        max_warmup_time = len(hr_data) * 0.2
        warmup_mask = (low_variability & increasing_hr) & (hr_data.index <= max_warmup_time)
        
        if warmup_mask.any():
            warmup_start = hr_data.index[warmup_mask].min()
            warmup_end = hr_data.index[warmup_mask].max()
            
            # Extend warm-up to include initial low-intensity period
            initial_low_hr = hr_data.iloc[:int(len(hr_data) * 0.1)].mean()
            extended_start = hr_data[hr_data <= initial_low_hr * 1.1].index.min()
            
            warmup_duration = (warmup_end - warmup_start) * df['time_diff'].mean() / 60
            
            return {
                'start_time': extended_start,
                'end_time': warmup_end,
                'duration_minutes': warmup_duration,
                'avg_heart_rate': hr_data.iloc[warmup_start:warmup_end].mean()
            }
        
        return {'start_time': 0, 'end_time': 0, 'duration_minutes': 0}
    
    def detect_rallies(self, df: pd.DataFrame, 
                      heart_rate_col: str = 'heart_rate',
                      cadence_col: str = 'cadence') -> List[Dict]:
        """
        Detect rally periods based on elevated heart rate and movement patterns.
        """
        rallies = []
        
        if heart_rate_col not in df.columns:
            logger.warning("Heart rate data not available for rally detection")
            return rallies
        
        hr_data = df[heart_rate_col].dropna()
        if len(hr_data) < 10:
            return rallies
        
        # Calculate baseline heart rate (excluding warm-up)
        warmup_info = self.detect_warm_up(df, heart_rate_col)
        if warmup_info['end_time'] > 0:
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
        for start_idx, end_idx in rally_periods:
            # Use the actual indices from hr_data to get time differences
            actual_start_idx = hr_data.index[start_idx]
            actual_end_idx = hr_data.index[end_idx-1] if end_idx < len(hr_data) else hr_data.index[-1]
            rally_duration = (actual_end_idx - actual_start_idx) * df['time_diff'].mean() / 60
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
        
        logger.info(f"Detected {len(rallies)} rallies")
        return rallies
    
    def detect_rest_periods(self, df: pd.DataFrame, 
                           heart_rate_col: str = 'heart_rate') -> List[Dict]:
        """
        Detect rest periods between rallies based on heart rate recovery.
        """
        rest_periods = []
        
        if heart_rate_col not in df.columns:
            return rest_periods
        
        hr_data = df[heart_rate_col].dropna()
        if len(hr_data) < 10:
            return rest_periods
        
        # Calculate baseline heart rate
        baseline_hr = hr_data.quantile(0.2)
        rest_threshold = baseline_hr + (hr_data.max() - baseline_hr) * 0.15
        
        # Find periods below threshold
        below_threshold = hr_data < rest_threshold
        
        # Group consecutive periods
        rest_periods_list = []
        current_start = None
        
        for i, is_rest in enumerate(below_threshold):
            if is_rest and current_start is None:
                current_start = i
            elif not is_rest and current_start is not None:
                # End of rest period
                if i - current_start >= 3:  # Minimum rest duration
                    rest_periods_list.append((current_start, i))
                current_start = None
        
        # Convert to rest period information
        for start_idx, end_idx in rest_periods_list:
            # Use the actual indices from hr_data to get time differences
            actual_start_idx = hr_data.index[start_idx]
            actual_end_idx = hr_data.index[end_idx-1] if end_idx < len(hr_data) else hr_data.index[-1]
            rest_duration = (actual_end_idx - actual_start_idx) * df['time_diff'].mean() / 60
            avg_hr = hr_data.iloc[start_idx:end_idx].mean()
            
            rest_periods.append({
                'start_time': actual_start_idx,
                'end_time': actual_end_idx,
                'duration_minutes': rest_duration,
                'avg_heart_rate': avg_hr,
                'recovery_rate': self._calculate_recovery_rate(hr_data, start_idx, end_idx)
            })
        
        logger.info(f"Detected {len(rest_periods)} rest periods")
        return rest_periods
    
    def detect_shots(self, df: pd.DataFrame, 
                    cadence_col: str = 'cadence',
                    hand_position: str = None) -> List[Dict]:
        """
        Detect individual shots based on movement patterns.
        Different algorithms for playing hand vs non-playing hand.
        """
        shots = []
        
        if cadence_col not in df.columns:
            logger.warning("Cadence data not available for shot detection")
            return shots
        
        cadence_data = df[cadence_col].dropna()
        if len(cadence_data) < 10:
            return shots
        
        hand_pos = hand_position or self.hand_position
        
        if hand_pos == 'playing_hand':
            # For playing hand, look for sharp spikes in cadence/movement
            # Apply smoothing first
            smoothed = signal.savgol_filter(cadence_data, 
                                         window_length=min(5, len(cadence_data)//2*2+1), 
                                         polyorder=2)
            
            # Find peaks (shots)
            peaks, properties = signal.find_peaks(smoothed, 
                                                height=cadence_data.mean() + cadence_data.std(),
                                                distance=3)  # Minimum 3 seconds between shots
            
            for peak in peaks:
                shots.append({
                    'timestamp': df.iloc[peak]['timestamp'],
                    'cadence': cadence_data.iloc[peak],
                    'intensity': properties['peak_heights'][list(peaks).index(peak)]
                })
        
        else:  # non_playing_hand
            # For non-playing hand, look for sudden changes in movement patterns
            cadence_diff = cadence_data.diff().abs()
            shot_threshold = cadence_diff.quantile(0.8)
            
            shot_indices = cadence_diff[cadence_diff > shot_threshold].index
            
            for idx in shot_indices:
                shots.append({
                    'timestamp': df.iloc[idx]['timestamp'],
                    'cadence': cadence_data.iloc[idx],
                    'intensity': cadence_diff.iloc[idx]
                })
        
        logger.info(f"Detected {len(shots)} shots")
        return shots
    
    def _calculate_intensity(self, hr_segment: pd.Series) -> float:
        """Calculate intensity score for a rally segment."""
        if len(hr_segment) == 0:
            return 0
        
        # Intensity based on average HR relative to max observed
        avg_hr = hr_segment.mean()
        max_hr = hr_segment.max()
        
        # Simple intensity score (0-1)
        intensity = (avg_hr - hr_segment.min()) / (max_hr - hr_segment.min()) if max_hr > hr_segment.min() else 0
        return min(intensity, 1.0)
    
    def _calculate_recovery_rate(self, hr_data: pd.Series, start_idx: int, end_idx: int) -> float:
        """Calculate heart rate recovery rate during rest period."""
        if end_idx - start_idx < 2:
            return 0
        
        segment = hr_data.iloc[start_idx:end_idx]
        if len(segment) < 2:
            return 0
        
        # Calculate recovery rate (HR drop per minute)
        hr_drop = segment.iloc[0] - segment.iloc[-1]
        time_minutes = (end_idx - start_idx) * 0.0167  # Assuming ~1 second intervals
        
        return hr_drop / time_minutes if time_minutes > 0 else 0
    
    def analyze_session(self, df: pd.DataFrame) -> Dict:
        """Run complete event detection analysis on the session."""
        logger.info("Starting session analysis...")
        
        # Detect all events
        warmup = self.detect_warm_up(df)
        rallies = self.detect_rallies(df)
        rest_periods = self.detect_rest_periods(df)
        shots = self.detect_shots(df)
        
        # Compile results
        analysis = {
            'warmup': warmup,
            'rallies': rallies,
            'rest_periods': rest_periods,
            'shots': shots,
            'session_summary': {
                'total_rallies': len(rallies),
                'total_shots': len(shots),
                'avg_rally_duration': np.mean([r['duration_minutes'] for r in rallies]) if rallies else 0,
                'longest_rally_duration': max([r['duration_minutes'] for r in rallies]) if rallies else 0,
                'warmup_duration': warmup.get('duration_minutes', 0)
            }
        }
        
        logger.info("Session analysis completed")
        return analysis


if __name__ == "__main__":
    # Test with sample data
    import pandas as pd
    import numpy as np
    
    # Create sample data
    np.random.seed(42)
    timestamps = pd.date_range('2024-01-01 10:00:00', periods=1000, freq='1s')
    
    # Simulate a squash session with warm-up, rallies, and rest
    hr_data = []
    cadence_data = []
    
    # Warm-up (first 200 points)
    hr_data.extend(np.linspace(80, 120, 200))
    cadence_data.extend(np.random.normal(60, 5, 200))
    
    # Rallies and rest periods
    for i in range(200, 1000):
        if (i - 200) % 50 < 30:  # Rally period
            hr_data.append(140 + np.random.normal(0, 10))
            cadence_data.append(100 + np.random.normal(0, 15))
        else:  # Rest period
            hr_data.append(100 + np.random.normal(0, 5))
            cadence_data.append(70 + np.random.normal(0, 5))
    
    sample_df = pd.DataFrame({
        'timestamp': timestamps,
        'heart_rate': hr_data,
        'cadence': cadence_data,
        'time_diff': 1.0
    })
    
    # Test event detection
    detector = EventDetector()
    analysis = detector.analyze_session(sample_df)
    
    print("Analysis Results:")
    print(f"Warm-up duration: {analysis['warmup']['duration_minutes']:.1f} minutes")
    print(f"Number of rallies: {analysis['session_summary']['total_rallies']}")
    print(f"Number of shots: {analysis['session_summary']['total_shots']}")
    print(f"Average rally duration: {analysis['session_summary']['avg_rally_duration']:.1f} minutes")
