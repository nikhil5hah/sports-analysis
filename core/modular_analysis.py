"""
Squash Performance Analysis - Modular Analysis Engine

Uses the metrics framework to provide comprehensive, extensible analysis.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional
from .metrics_framework import MetricsFramework, MetricResult, MetricType
from sports.squash.detectors.additional_metrics import (
    SessionDurationDetector, PlayingTimeDetector, LongestRallyDetector,
    RalliesPerGameDetector, RestBetweenGamesDetector, AccelerometerShotDetector
)

logger = logging.getLogger(__name__)

class ModularAnalysisEngine:
    """Main analysis engine using the modular metrics framework."""
    
    def __init__(self):
        self.framework = MetricsFramework()
        self._register_all_detectors()
        self.session_context = {}
    
    def _register_all_detectors(self):
        """Register all available metric detectors."""
        # Core metrics from metrics_framework
        from .metrics_framework import WarmUpDetector, CoolDownDetector, GameDetector, RallyDetector
        
        self.framework.register_detector(WarmUpDetector())
        self.framework.register_detector(CoolDownDetector())
        self.framework.register_detector(GameDetector())
        self.framework.register_detector(RallyDetector())
        
        # Additional metrics
        self.framework.register_detector(SessionDurationDetector())
        self.framework.register_detector(PlayingTimeDetector())
        self.framework.register_detector(LongestRallyDetector())
        self.framework.register_detector(RalliesPerGameDetector())
        self.framework.register_detector(RestBetweenGamesDetector())
        self.framework.register_detector(AccelerometerShotDetector())
        
        logger.info(f"Registered {len(self.framework.get_available_metrics())} metric detectors")
    
    def set_session_context(self, hand_position: str, session_type: str):
        """Set context for analysis."""
        self.session_context = {
            'hand_position': hand_position,
            'session_type': session_type
        }
        logger.info(f"Session context set: {hand_position}, {session_type}")
    
    def analyze_session(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run comprehensive analysis using all registered detectors."""
        logger.info("Starting modular session analysis...")
        
        # Prepare context with session info
        context = self.session_context.copy()
        context['session_duration'] = df['cumulative_time'].iloc[-1] / 60 if 'cumulative_time' in df.columns else 0
        
        # Run all metric detectors
        results = self.framework.detect_all_metrics(df, context)
        
        # Build comprehensive analysis
        analysis = {
            'metrics': results,
            'session_summary': self._build_session_summary(df, results),
            'data_quality': self._assess_data_quality(df),
            'recommendations': self._generate_recommendations(results),
            'session_context': self.session_context
        }
        
        logger.info("Modular session analysis completed")
        return analysis
    
    def _build_session_summary(self, df: pd.DataFrame, results: Dict[str, MetricResult]) -> Dict[str, Any]:
        """Build high-level session summary from metric results."""
        summary = {
            'total_duration_minutes': results.get('total_session_duration', MetricResult('', 0, 0, {})).value or 0,
            'data_points': len(df),
            'available_data_fields': [col for col in df.columns if col != 'timestamp'],
            'metrics_detected': len([r for r in results.values() if r.confidence > 0.5]),
            'metrics_total': len(results)
        }
        
        # Add specific metrics if available
        if 'heart_rate' in df.columns:
            summary.update({
                'avg_heart_rate': df['heart_rate'].mean(),
                'max_heart_rate': df['heart_rate'].max(),
                'min_heart_rate': df['heart_rate'].min()
            })
        
        # Add metric-specific summaries
        warmup_result = results.get('warm_up_length')
        if warmup_result and warmup_result.confidence > 0.5:
            summary['warmup_duration'] = warmup_result.value
        
        rallies_result = results.get('number_of_rallies')
        if rallies_result and rallies_result.confidence > 0.5:
            summary['total_rallies'] = rallies_result.value
            summary['avg_rally_duration'] = rallies_result.metadata.get('avg_rally_duration', 0)
            summary['longest_rally_duration'] = rallies_result.metadata.get('longest_rally_duration', 0)
        
        games_result = results.get('number_of_games')
        if games_result and games_result.confidence > 0.5:
            summary['total_games'] = games_result.value
        
        cooldown_result = results.get('cool_down_length')
        if cooldown_result and cooldown_result.confidence > 0.5:
            summary['cooldown_duration'] = cooldown_result.value
        
        return summary
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess the quality and completeness of the data."""
        quality = {
            'total_data_points': len(df),
            'session_duration_minutes': df['cumulative_time'].iloc[-1] / 60 if 'cumulative_time' in df.columns else 0,
            'data_completeness': {},
            'recommended_metrics': [],
            'missing_data_warnings': []
        }
        
        # Check data completeness for each field
        important_fields = ['heart_rate', 'cadence', 'speed', 'accelerometer_x', 'accelerometer_y', 'accelerometer_z']
        
        for field in important_fields:
            if field in df.columns:
                completeness = (df[field].notna().sum() / len(df)) * 100
                quality['data_completeness'][field] = completeness
                
                if completeness > 80:
                    quality['recommended_metrics'].append(field)
                elif completeness < 50:
                    quality['missing_data_warnings'].append(f"{field}: Only {completeness:.1f}% complete")
        
        # Assess overall data quality
        if quality['data_completeness'].get('heart_rate', 0) > 90:
            quality['overall_quality'] = 'excellent'
        elif quality['data_completeness'].get('heart_rate', 0) > 70:
            quality['overall_quality'] = 'good'
        elif quality['data_completeness'].get('heart_rate', 0) > 50:
            quality['overall_quality'] = 'fair'
        else:
            quality['overall_quality'] = 'poor'
        
        return quality
    
    def _generate_recommendations(self, results: Dict[str, MetricResult]) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Check confidence levels
        low_confidence_metrics = [name for name, result in results.items() if result.confidence < 0.5]
        if low_confidence_metrics:
            recommendations.append(f"Consider improving data quality for: {', '.join(low_confidence_metrics)}")
        
        # Check for missing accelerometer data
        if 'shots_detected' in results and results['shots_detected'].confidence == 0:
            recommendations.append("Enable accelerometer data collection for better shot detection")
        
        # Check warm-up duration
        warmup_result = results.get('warm_up_length')
        if warmup_result and warmup_result.confidence > 0.5:
            if warmup_result.value < 3:
                recommendations.append("Consider longer warm-up periods (5-10 minutes recommended)")
            elif warmup_result.value > 15:
                recommendations.append("Warm-up duration seems long - consider optimizing")
        
        # Check cool-down
        cooldown_result = results.get('cool_down_length')
        if cooldown_result and cooldown_result.confidence > 0.5:
            if cooldown_result.value < 2:
                recommendations.append("Consider adding a proper cool-down period (5-10 minutes)")
        
        # Check rally patterns
        rallies_result = results.get('number_of_rallies')
        if rallies_result and rallies_result.confidence > 0.5:
            avg_duration = rallies_result.metadata.get('avg_rally_duration', 0)
            if avg_duration > 2:
                recommendations.append("Rallies seem long - consider shorter, more intense rallies")
            elif avg_duration < 0.5:
                recommendations.append("Rallies seem short - consider longer rallies for better endurance")
        
        return recommendations
    
    def get_metric_result(self, metric_name: str) -> Optional[MetricResult]:
        """Get result for a specific metric."""
        return self.framework.get_metric_result(metric_name)
    
    def get_available_metrics(self) -> List[str]:
        """Get list of all available metrics."""
        return self.framework.get_available_metrics()
    
    def get_metrics_by_type(self, metric_type: MetricType) -> List[str]:
        """Get metrics of a specific type."""
        return self.framework.get_metrics_by_type(metric_type)
    
    def get_metric_detector_info(self, metric_name: str) -> Dict[str, Any]:
        """Get information about a specific metric detector."""
        detector = self.framework.detectors.get(metric_name)
        if detector:
            return {
                'name': detector.metric_name,
                'type': detector.metric_type.value,
                'version': detector.algorithm_version,
                'required_fields': detector.get_required_data_fields(),
                'optional_fields': detector.get_optional_data_fields()
            }
        return {}

# Example usage and testing
if __name__ == "__main__":
    # Test the modular analysis engine
    engine = ModularAnalysisEngine()
    
    print("Available metrics:", engine.get_available_metrics())
    print("Temporal metrics:", engine.get_metrics_by_type(MetricType.TEMPORAL))
    print("Count metrics:", engine.get_metrics_by_type(MetricType.COUNT))
    
    # Test with sample data
    import pandas as pd
    import numpy as np
    
    # Create sample data
    timestamps = pd.date_range('2024-01-01 10:00:00', periods=1000, freq='1s')
    hr_data = np.random.normal(120, 20, 1000)
    
    sample_df = pd.DataFrame({
        'timestamp': timestamps,
        'heart_rate': hr_data,
        'time_diff': 1.0,
        'cumulative_time': np.arange(1000)
    })
    
    # Set context and analyze
    engine.set_session_context('playing_hand', 'training')
    analysis = engine.analyze_session(sample_df)
    
    print("\nAnalysis Summary:")
    print(f"Session Duration: {analysis['session_summary']['total_duration_minutes']:.1f} minutes")
    print(f"Metrics Detected: {analysis['session_summary']['metrics_detected']}/{analysis['session_summary']['metrics_total']}")
    print(f"Data Quality: {analysis['data_quality']['overall_quality']}")
    print(f"Recommendations: {len(analysis['recommendations'])}")
