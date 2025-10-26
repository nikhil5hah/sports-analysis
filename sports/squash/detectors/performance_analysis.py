"""
Squash Performance Analysis - Performance Analysis Module

Advanced algorithms for analyzing squash performance:
- Performance deterioration detection
- Intensity analysis
- Heart rate zone analysis
- Recovery analysis
- Performance trends
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.signal import find_peaks
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyzes performance metrics and trends in squash sessions."""
    
    def __init__(self):
        self.analysis_results = {}
    
    def detect_performance_deterioration(self, df: pd.DataFrame, 
                                       heart_rate_col: str = 'heart_rate',
                                       rallies: List[Dict] = None) -> Dict:
        """
        Detect when performance begins to decline during the session.
        Uses multiple indicators: HR drift, rally performance, recovery rates.
        """
        if heart_rate_col not in df.columns:
            logger.warning("Heart rate data not available for deterioration analysis")
            return {'deterioration_point': None, 'confidence': 0, 'indicators': []}
        
        hr_data = df[heart_rate_col].dropna()
        if len(hr_data) < 50:
            return {'deterioration_point': None, 'confidence': 0, 'indicators': []}
        
        indicators = []
        
        # 1. Heart Rate Drift Analysis
        hr_drift_point = self._analyze_hr_drift(hr_data, df)
        if hr_drift_point:
            indicators.append({
                'type': 'hr_drift',
                'point': hr_drift_point,
                'severity': self._calculate_drift_severity(hr_data, hr_drift_point)
            })
        
        # 2. Rally Performance Decline
        if rallies:
            rally_decline_point = self._analyze_rally_decline(rallies)
            if rally_decline_point:
                indicators.append({
                    'type': 'rally_decline',
                    'point': rally_decline_point,
                    'severity': self._calculate_rally_decline_severity(rallies, rally_decline_point)
                })
        
        # 3. Recovery Rate Decline
        recovery_decline_point = self._analyze_recovery_decline(df, heart_rate_col)
        if recovery_decline_point:
            indicators.append({
                'type': 'recovery_decline',
                'point': recovery_decline_point,
                'severity': self._calculate_recovery_decline_severity(df, recovery_decline_point, heart_rate_col)
            })
        
        # Determine overall deterioration point
        if indicators:
            # Weight different indicators
            weighted_points = []
            weights = {'hr_drift': 0.4, 'rally_decline': 0.4, 'recovery_decline': 0.2}
            
            for indicator in indicators:
                weight = weights.get(indicator['type'], 0.3)
                weighted_points.append(indicator['point'] * weight)
            
            deterioration_point = sum(weighted_points) / sum(weights.values())
            confidence = min(len(indicators) / 3.0, 1.0)  # Higher confidence with more indicators
            
            return {
                'deterioration_point': deterioration_point,
                'confidence': confidence,
                'indicators': indicators,
                'time_minutes': deterioration_point * df['time_diff'].mean() / 60 if 'time_diff' in df.columns else 0
            }
        
        return {'deterioration_point': None, 'confidence': 0, 'indicators': []}
    
    def analyze_intensity_zones(self, df: pd.DataFrame, 
                              heart_rate_col: str = 'heart_rate') -> Dict:
        """
        Analyze time spent in different heart rate zones.
        """
        if heart_rate_col not in df.columns:
            return {'zones': {}, 'zone_distribution': {}}
        
        hr_data = df[heart_rate_col].dropna()
        if len(hr_data) < 10:
            return {'zones': {}, 'zone_distribution': {}}
        
        # Calculate HR zones based on session data
        hr_max = hr_data.max()
        hr_min = hr_data.min()
        hr_range = hr_max - hr_min
        
        # Define zones (relative to session min/max)
        zones = {
            'recovery': (hr_min, hr_min + hr_range * 0.5),
            'aerobic': (hr_min + hr_range * 0.5, hr_min + hr_range * 0.7),
            'threshold': (hr_min + hr_range * 0.7, hr_min + hr_range * 0.85),
            'anaerobic': (hr_min + hr_range * 0.85, hr_max)
        }
        
        # Calculate time in each zone
        zone_distribution = {}
        total_time = len(hr_data) * df['time_diff'].mean() if 'time_diff' in df.columns else len(hr_data)
        
        for zone_name, (zone_min, zone_max) in zones.items():
            zone_mask = (hr_data >= zone_min) & (hr_data < zone_max)
            zone_time = zone_mask.sum() * df['time_diff'].mean() if 'time_diff' in df.columns else zone_mask.sum()
            zone_percentage = (zone_time / total_time) * 100 if total_time > 0 else 0
            
            zone_distribution[zone_name] = {
                'time_minutes': zone_time / 60,
                'percentage': zone_percentage,
                'avg_hr': hr_data[zone_mask].mean() if zone_mask.any() else 0
            }
        
        return {
            'zones': zones,
            'zone_distribution': zone_distribution,
            'session_stats': {
                'avg_hr': hr_data.mean(),
                'max_hr': hr_max,
                'min_hr': hr_min,
                'hr_variability': hr_data.std()
            }
        }
    
    def analyze_recovery_patterns(self, df: pd.DataFrame, 
                                 heart_rate_col: str = 'heart_rate',
                                 rest_periods: List[Dict] = None) -> Dict:
        """
        Analyze recovery patterns between rallies.
        """
        if heart_rate_col not in df.columns:
            return {'recovery_stats': {}, 'recovery_trend': {}}
        
        hr_data = df[heart_rate_col].dropna()
        if len(hr_data) < 20:
            return {'recovery_stats': {}, 'recovery_trend': {}}
        
        recovery_stats = {}
        
        if rest_periods:
            # Analyze recovery rates during rest periods
            recovery_rates = [rp.get('recovery_rate', 0) for rp in rest_periods if 'recovery_rate' in rp]
            
            if recovery_rates:
                recovery_stats = {
                    'avg_recovery_rate': np.mean(recovery_rates),
                    'max_recovery_rate': np.max(recovery_rates),
                    'min_recovery_rate': np.min(recovery_rates),
                    'recovery_consistency': 1 - (np.std(recovery_rates) / np.mean(recovery_rates)) if np.mean(recovery_rates) > 0 else 0
                }
        
        # Analyze overall recovery trend
        recovery_trend = self._calculate_recovery_trend(hr_data)
        
        return {
            'recovery_stats': recovery_stats,
            'recovery_trend': recovery_trend
        }
    
    def analyze_performance_trends(self, rallies: List[Dict]) -> Dict:
        """
        Analyze trends in rally performance over time.
        """
        if not rallies or len(rallies) < 3:
            return {'trends': {}, 'performance_score': 0}
        
        # Extract metrics over time
        rally_numbers = list(range(len(rallies)))
        durations = [r['duration_minutes'] for r in rallies]
        avg_hrs = [r['avg_heart_rate'] for r in rallies]
        intensities = [r.get('intensity', 0) for r in rallies]
        
        trends = {}
        
        # Analyze trends using linear regression
        for metric_name, values in [('duration', durations), ('avg_hr', avg_hrs), ('intensity', intensities)]:
            if len(values) >= 3:
                slope, intercept, r_value, p_value, std_err = stats.linregress(rally_numbers, values)
                trends[metric_name] = {
                    'slope': slope,
                    'r_squared': r_value ** 2,
                    'p_value': p_value,
                    'trend_direction': 'improving' if slope > 0 else 'declining' if slope < 0 else 'stable'
                }
        
        # Calculate overall performance score
        performance_score = self._calculate_performance_score(rallies, trends)
        
        return {
            'trends': trends,
            'performance_score': performance_score,
            'rally_count': len(rallies)
        }
    
    def _analyze_hr_drift(self, hr_data: pd.Series, df: pd.DataFrame) -> Optional[float]:
        """Analyze heart rate drift over time."""
        if len(hr_data) < 30:
            return None
        
        # Calculate rolling average
        window_size = min(20, len(hr_data) // 3)
        rolling_avg = hr_data.rolling(window=window_size, center=True).mean()
        
        # Find significant upward trend
        time_points = np.arange(len(rolling_avg))
        valid_mask = ~rolling_avg.isna()
        
        if valid_mask.sum() < 10:
            return None
        
        slope, _, r_value, p_value, _ = stats.linregress(
            time_points[valid_mask], 
            rolling_avg[valid_mask]
        )
        
        # Consider drift if significant upward trend
        if slope > 0 and p_value < 0.05 and r_value > 0.3:
            # Find where trend becomes significant
            for i in range(window_size, len(rolling_avg) - window_size):
                segment_slope, _, _, segment_p, _ = stats.linregress(
                    time_points[i-window_size:i+window_size],
                    rolling_avg[i-window_size:i+window_size]
                )
                if segment_slope > slope * 0.5 and segment_p < 0.1:
                    return i / len(hr_data)
        
        return None
    
    def _analyze_rally_decline(self, rallies: List[Dict]) -> Optional[float]:
        """Analyze decline in rally performance."""
        if len(rallies) < 5:
            return None
        
        # Calculate performance metrics over time
        rally_numbers = np.arange(len(rallies))
        durations = np.array([r['duration_minutes'] for r in rallies])
        intensities = np.array([r.get('intensity', 0) for r in rallies])
        
        # Look for declining trends
        duration_slope, _, _, duration_p, _ = stats.linregress(rally_numbers, durations)
        intensity_slope, _, _, intensity_p, _ = stats.linregress(rally_numbers, intensities)
        
        # Check for significant decline
        if (duration_slope < 0 and duration_p < 0.05) or (intensity_slope < 0 and intensity_p < 0.05):
            # Find the point where decline becomes significant
            for i in range(3, len(rallies) - 2):
                early_duration = np.mean(durations[:i])
                late_duration = np.mean(durations[i:])
                early_intensity = np.mean(intensities[:i])
                late_intensity = np.mean(intensities[i:])
                
                if (late_duration < early_duration * 0.9) or (late_intensity < early_intensity * 0.9):
                    return i / len(rallies)
        
        return None
    
    def _analyze_recovery_decline(self, df: pd.DataFrame, heart_rate_col: str) -> Optional[float]:
        """Analyze decline in recovery rates."""
        hr_data = df[heart_rate_col].dropna()
        if len(hr_data) < 50:
            return None
        
        # Calculate recovery rates in segments
        segment_size = len(hr_data) // 5  # Divide into 5 segments
        recovery_rates = []
        
        for i in range(0, len(hr_data) - segment_size, segment_size):
            segment = hr_data.iloc[i:i+segment_size]
            if len(segment) > 10:
                # Calculate recovery rate as HR drop rate
                hr_drop = segment.iloc[0] - segment.iloc[-1]
                time_minutes = segment_size * df['time_diff'].mean() / 60 if 'time_diff' in df.columns else segment_size / 60
                recovery_rate = hr_drop / time_minutes if time_minutes > 0 else 0
                recovery_rates.append(recovery_rate)
        
        if len(recovery_rates) < 3:
            return None
        
        # Check for declining recovery rates
        segment_numbers = np.arange(len(recovery_rates))
        slope, _, _, p_value, _ = stats.linregress(segment_numbers, recovery_rates)
        
        if slope < 0 and p_value < 0.1:
            # Find where decline becomes significant
            for i in range(1, len(recovery_rates)):
                if recovery_rates[i] < recovery_rates[0] * 0.8:
                    return i / len(recovery_rates)
        
        return None
    
    def _calculate_drift_severity(self, hr_data: pd.Series, drift_point: float) -> float:
        """Calculate severity of heart rate drift."""
        drift_idx = int(drift_point * len(hr_data))
        early_hr = hr_data.iloc[:drift_idx].mean()
        late_hr = hr_data.iloc[drift_idx:].mean()
        
        severity = (late_hr - early_hr) / early_hr if early_hr > 0 else 0
        return min(severity, 1.0)  # Cap at 100% increase
    
    def _calculate_rally_decline_severity(self, rallies: List[Dict], decline_point: float) -> float:
        """Calculate severity of rally performance decline."""
        decline_idx = int(decline_point * len(rallies))
        early_duration = np.mean([r['duration_minutes'] for r in rallies[:decline_idx]])
        late_duration = np.mean([r['duration_minutes'] for r in rallies[decline_idx:]])
        
        severity = (early_duration - late_duration) / early_duration if early_duration > 0 else 0
        return min(severity, 1.0)
    
    def _calculate_recovery_decline_severity(self, df: pd.DataFrame, decline_point: float, heart_rate_col: str) -> float:
        """Calculate severity of recovery rate decline."""
        hr_data = df[heart_rate_col].dropna()
        decline_idx = int(decline_point * len(hr_data))
        
        early_segment = hr_data.iloc[:decline_idx]
        late_segment = hr_data.iloc[decline_idx:]
        
        # Calculate recovery rates
        early_recovery = (early_segment.iloc[0] - early_segment.iloc[-1]) / (len(early_segment) / 60)
        late_recovery = (late_segment.iloc[0] - late_segment.iloc[-1]) / (len(late_segment) / 60)
        
        severity = (early_recovery - late_recovery) / early_recovery if early_recovery > 0 else 0
        return min(severity, 1.0)
    
    def _calculate_recovery_trend(self, hr_data: pd.Series) -> Dict:
        """Calculate overall recovery trend."""
        if len(hr_data) < 20:
            return {'trend': 'insufficient_data', 'slope': 0}
        
        # Calculate recovery rate over time
        time_points = np.arange(len(hr_data))
        slope, _, r_value, p_value, _ = stats.linregress(time_points, hr_data)
        
        if p_value < 0.05:
            if slope > 0:
                trend = 'declining_recovery'
            else:
                trend = 'improving_recovery'
        else:
            trend = 'stable_recovery'
        
        return {
            'trend': trend,
            'slope': slope,
            'r_squared': r_value ** 2,
            'p_value': p_value
        }
    
    def _calculate_performance_score(self, rallies: List[Dict], trends: Dict) -> float:
        """Calculate overall performance score (0-100)."""
        if not rallies:
            return 0
        
        score = 50  # Base score
        
        # Factor in rally count
        rally_count_score = min(len(rallies) * 2, 20)  # Up to 20 points for rally count
        score += rally_count_score
        
        # Factor in trends
        for metric, trend_data in trends.items():
            if trend_data['trend_direction'] == 'improving':
                score += 10
            elif trend_data['trend_direction'] == 'declining':
                score -= 10
        
        # Factor in average intensity
        avg_intensity = np.mean([r.get('intensity', 0) for r in rallies])
        intensity_score = avg_intensity * 20  # Up to 20 points for intensity
        score += intensity_score
        
        return max(0, min(100, score))  # Clamp between 0 and 100
    
    def comprehensive_analysis(self, df: pd.DataFrame, 
                             rallies: List[Dict] = None,
                             rest_periods: List[Dict] = None) -> Dict:
        """Run comprehensive performance analysis."""
        logger.info("Starting comprehensive performance analysis...")
        
        analysis = {
            'deterioration': self.detect_performance_deterioration(df, rallies=rallies),
            'intensity_zones': self.analyze_intensity_zones(df),
            'recovery_patterns': self.analyze_recovery_patterns(df, rest_periods=rest_periods),
            'performance_trends': self.analyze_performance_trends(rallies) if rallies else {},
            'session_summary': self._generate_session_summary(df, rallies, rest_periods)
        }
        
        logger.info("Comprehensive analysis completed")
        return analysis
    
    def _generate_session_summary(self, df: pd.DataFrame, 
                                rallies: List[Dict] = None,
                                rest_periods: List[Dict] = None) -> Dict:
        """Generate high-level session summary."""
        summary = {
            'total_duration_minutes': df['cumulative_time'].iloc[-1] / 60 if 'cumulative_time' in df.columns else 0,
            'data_points': len(df),
            'avg_heart_rate': df['heart_rate'].mean() if 'heart_rate' in df.columns else 0,
            'max_heart_rate': df['heart_rate'].max() if 'heart_rate' in df.columns else 0,
            'total_rallies': len(rallies) if rallies else 0,
            'total_rest_periods': len(rest_periods) if rest_periods else 0
        }
        
        if rallies:
            summary.update({
                'avg_rally_duration': np.mean([r['duration_minutes'] for r in rallies]),
                'longest_rally_duration': max([r['duration_minutes'] for r in rallies]),
                'total_rally_time': sum([r['duration_minutes'] for r in rallies])
            })
        
        return summary


if __name__ == "__main__":
    # Test with sample data
    import pandas as pd
    import numpy as np
    
    # Create sample data
    np.random.seed(42)
    timestamps = pd.date_range('2024-01-01 10:00:00', periods=1000, freq='1s')
    
    # Simulate performance deterioration
    hr_data = []
    for i in range(1000):
        base_hr = 120
        # Add drift over time
        drift = i * 0.02
        # Add random variation
        noise = np.random.normal(0, 10)
        hr_data.append(base_hr + drift + noise)
    
    sample_df = pd.DataFrame({
        'timestamp': timestamps,
        'heart_rate': hr_data,
        'time_diff': 1.0,
        'cumulative_time': np.arange(1000)
    })
    
    # Test performance analysis
    analyzer = PerformanceAnalyzer()
    analysis = analyzer.comprehensive_analysis(sample_df)
    
    print("Performance Analysis Results:")
    print(f"Deterioration point: {analysis['deterioration']['deterioration_point']}")
    print(f"Confidence: {analysis['deterioration']['confidence']:.2f}")
    print(f"Session duration: {analysis['session_summary']['total_duration_minutes']:.1f} minutes")
    print(f"Average HR: {analysis['session_summary']['avg_heart_rate']:.1f} bpm")
