"""
Insight Generator Service
REUSES: core/metrics_framework.py, sports/squash/detectors/ (existing code)

This service generates insights using manual score labels + HR data.
"""
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Import existing code
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.metrics_framework import (
    MetricsFramework,
    RallyDetector,
    GameDetector,
    WarmUpDetector,
    CoolDownDetector,
    calculate_hr_zones
)

from backend.models import Session, Point, HeartRateData, Insight
from sqlalchemy.orm import Session as DBSession


class InsightGenerator:
    """
    Generate insights from session data.
    Combines existing metrics framework with new HR+score correlation.
    """

    def __init__(self, db: DBSession):
        self.db = db

        # Initialize metrics framework (REUSE existing)
        self.framework = MetricsFramework()
        self.framework.register_detector(WarmUpDetector())
        self.framework.register_detector(CoolDownDetector())
        self.framework.register_detector(GameDetector())
        self.framework.register_detector(RallyDetector())
        # Add other detectors as needed

    async def generate_session_insights(self, session_id: str) -> Dict:
        """
        Generate complete insights for a session.

        Returns insights dict ready to store in database.
        """
        # Fetch session data as DataFrame
        df = await self._fetch_session_dataframe(session_id)

        if df is None or len(df) == 0:
            return {"error": "No data available for analysis"}

        # Run existing metrics framework
        metric_results = self.framework.detect_all_metrics(df)

        # Convert to serializable format
        metrics_json = self._serialize_metric_results(metric_results)

        # Generate HR + Score correlation (NEW)
        hr_score_insights = await self._analyze_hr_vs_scores(session_id)

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics_json, hr_score_insights)

        # Store insights in database
        session = self.db.query(Session).filter_by(session_id=session_id).first()

        insight = Insight(
            session_id=session_id,
            user_id=session.user_id,
            insight_type="session_analysis",
            metrics=metrics_json,
            hr_score_correlation=hr_score_insights,
            recommendations=recommendations,
            algorithm_version="1.0"
        )

        self.db.add(insight)
        self.db.commit()

        return {
            "metrics": metrics_json,
            "hr_score_correlation": hr_score_insights,
            "recommendations": recommendations
        }

    async def _fetch_session_dataframe(self, session_id: str) -> pd.DataFrame:
        """
        Fetch session HR data as DataFrame (format expected by metrics framework).
        """
        hr_data = self.db.query(HeartRateData).filter_by(session_id=session_id).order_by(HeartRateData.time).all()

        if not hr_data:
            return None

        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'timestamp': record.time,
                'heart_rate': record.heart_rate,
                'hr_zone': record.hr_zone
            }
            for record in hr_data
        ])

        # Add time_diff and cumulative_time (needed by framework)
        df['time_diff'] = df['timestamp'].diff().dt.total_seconds().fillna(1.0)
        df['cumulative_time'] = df['time_diff'].cumsum()

        return df

    def _serialize_metric_results(self, results: Dict) -> Dict:
        """Convert MetricResult objects to JSON-serializable dict"""
        serialized = {}

        for metric_name, result in results.items():
            serialized[metric_name] = {
                'value': result.value,
                'confidence': result.confidence,
                'metadata': result.metadata,
                'algorithm_version': result.algorithm_version
            }

        return serialized

    async def _analyze_hr_vs_scores(self, session_id: str) -> Dict:
        """
        NEW: Analyze HR correlation with point outcomes.
        This is the key insight: "You win more points at X bpm"
        """
        points = self.db.query(Point).filter_by(session_id=session_id).order_by(Point.timestamp).all()

        if not points:
            return {"error": "No points recorded for this session"}

        won_points_hr = []
        lost_points_hr = []

        for point in points:
            # Get HR in 5-second window before point
            hr_window = self.db.query(HeartRateData).filter(
                HeartRateData.session_id == session_id,
                HeartRateData.time >= point.timestamp - timedelta(seconds=5),
                HeartRateData.time <= point.timestamp
            ).all()

            if not hr_window:
                continue

            avg_hr = sum(d.heart_rate for d in hr_window) / len(hr_window)

            if point.winner == 'me':
                won_points_hr.append(avg_hr)
            else:
                lost_points_hr.append(avg_hr)

        # Calculate insights
        insights = {
            'avg_hr_on_won_points': float(np.mean(won_points_hr)) if won_points_hr else 0,
            'avg_hr_on_lost_points': float(np.mean(lost_points_hr)) if lost_points_hr else 0,
            'hr_difference': float(np.mean(won_points_hr) - np.mean(lost_points_hr)) if won_points_hr and lost_points_hr else 0,
            'sample_size': {
                'won': len(won_points_hr),
                'lost': len(lost_points_hr)
            }
        }

        # Find optimal HR zone
        optimal_zone = await self._find_optimal_hr_zone(session_id)
        insights['optimal_zone'] = optimal_zone

        # Analyze recovery
        recovery_insights = await self._analyze_hr_recovery(session_id)
        insights['recovery'] = recovery_insights

        # Analyze fatigue by game
        fatigue_insights = await self._analyze_fatigue_by_game(session_id)
        insights['fatigue'] = fatigue_insights

        return insights

    async def _find_optimal_hr_zone(self, session_id: str) -> Dict:
        """Find which HR zone has best win rate"""
        points = self.db.query(Point).filter_by(session_id=session_id).all()

        zone_performance = {1: [], 2: [], 3: [], 4: [], 5: []}

        for point in points:
            # Get HR zone at point time
            hr_at_point = self.db.query(HeartRateData).filter(
                HeartRateData.session_id == session_id,
                HeartRateData.time <= point.timestamp
            ).order_by(HeartRateData.time.desc()).first()

            if hr_at_point and hr_at_point.hr_zone > 0:
                zone = hr_at_point.hr_zone
                zone_performance[zone].append(1 if point.winner == 'me' else 0)

        # Calculate win rate per zone
        zone_win_rates = {}
        for zone, outcomes in zone_performance.items():
            if outcomes:
                zone_win_rates[zone] = {
                    'win_rate': float(np.mean(outcomes)),
                    'points_in_zone': len(outcomes)
                }

        # Find best zone
        if zone_win_rates:
            best_zone = max(zone_win_rates.items(), key=lambda x: x[1]['win_rate'])
            return {
                'best_zone': best_zone[0],
                'win_rate': best_zone[1]['win_rate'],
                'all_zones': zone_win_rates
            }

        return {}

    async def _analyze_hr_recovery(self, session_id: str) -> Dict:
        """Analyze HR recovery between points"""
        points = self.db.query(Point).filter_by(session_id=session_id).order_by(Point.timestamp).all()

        if len(points) < 2:
            return {}

        recovery_rates = []

        for i in range(len(points) - 1):
            point_end = points[i]
            next_point_start = points[i + 1]

            # Get HR at point end and after 30 seconds
            hr_at_end = self.db.query(HeartRateData).filter(
                HeartRateData.session_id == session_id,
                HeartRateData.time <= point_end.timestamp
            ).order_by(HeartRateData.time.desc()).first()

            hr_after_30s = self.db.query(HeartRateData).filter(
                HeartRateData.session_id == session_id,
                HeartRateData.time >= point_end.timestamp + timedelta(seconds=30),
                HeartRateData.time <= next_point_start.timestamp
            ).first()

            if hr_at_end and hr_after_30s:
                recovery = hr_at_end.heart_rate - hr_after_30s.heart_rate
                recovery_rates.append(recovery)

        if recovery_rates:
            return {
                'avg_recovery_30s': float(np.mean(recovery_rates)),
                'avg_recovery_per_min': float(np.mean(recovery_rates) * 2),  # Extrapolate to per minute
                'sample_count': len(recovery_rates)
            }

        return {}

    async def _analyze_fatigue_by_game(self, session_id: str) -> Dict:
        """Analyze how performance changes across games (fatigue indicator)"""
        points = self.db.query(Point).filter_by(session_id=session_id).order_by(Point.game_number, Point.timestamp).all()

        if not points:
            return {}

        # Group by game
        games = {}
        for point in points:
            game_num = point.game_number
            if game_num not in games:
                games[game_num] = []
            games[game_num].append(point)

        game_insights = []

        for game_num, game_points in games.items():
            # Calculate avg HR for this game
            hr_values = []
            won_points = 0
            lost_points = 0

            for point in game_points:
                if point.winner == 'me':
                    won_points += 1
                else:
                    lost_points += 1

                # Get HR at point
                hr_data = self.db.query(HeartRateData).filter(
                    HeartRateData.session_id == session_id,
                    HeartRateData.time >= point.timestamp - timedelta(seconds=5),
                    HeartRateData.time <= point.timestamp
                ).all()

                if hr_data:
                    hr_values.extend([d.heart_rate for d in hr_data])

            if hr_values:
                game_insights.append({
                    'game_number': game_num,
                    'avg_hr': float(np.mean(hr_values)),
                    'max_hr': float(np.max(hr_values)),
                    'points_won': won_points,
                    'points_lost': lost_points,
                    'win_rate': won_points / (won_points + lost_points) if (won_points + lost_points) > 0 else 0
                })

        # Calculate fatigue indicator (HR increase across games)
        if len(game_insights) >= 2:
            first_game_hr = game_insights[0]['avg_hr']
            last_game_hr = game_insights[-1]['avg_hr']
            fatigue_indicator = (last_game_hr - first_game_hr) / first_game_hr

            return {
                'by_game': game_insights,
                'fatigue_indicator': float(fatigue_indicator),
                'interpretation': 'high' if fatigue_indicator > 0.08 else 'moderate' if fatigue_indicator > 0.04 else 'low'
            }

        return {'by_game': game_insights}

    def _generate_recommendations(self, metrics: Dict, hr_score: Dict) -> List[str]:
        """Generate actionable recommendations based on insights"""
        recommendations = []

        # HR vs performance recommendations
        if 'hr_difference' in hr_score:
            diff = hr_score['hr_difference']
            if diff > 5:
                recommendations.append(
                    f"You perform better at lower heart rates. "
                    f"Won points avg {hr_score['avg_hr_on_won_points']:.0f} bpm vs "
                    f"lost points {hr_score['avg_hr_on_lost_points']:.0f} bpm. "
                    f"Try to stay calm and control your breathing."
                )
            elif diff < -5:
                recommendations.append(
                    f"You perform better at higher intensities. "
                    f"Your win rate increases when HR is elevated. "
                    f"Don't be afraid to push the pace."
                )

        # Optimal zone recommendation
        if 'optimal_zone' in hr_score and 'best_zone' in hr_score['optimal_zone']:
            best_zone = hr_score['optimal_zone']['best_zone']
            win_rate = hr_score['optimal_zone']['win_rate']
            zone_names = {3: "Moderate (Zone 3)", 4: "Hard (Zone 4)", 5: "Maximum (Zone 5)"}

            if best_zone in zone_names:
                recommendations.append(
                    f"Your optimal performance zone is {zone_names[best_zone]} "
                    f"with a {win_rate*100:.0f}% win rate. "
                    f"Try to maintain this intensity during important rallies."
                )

        # Recovery recommendation
        if 'recovery' in hr_score and 'avg_recovery_per_min' in hr_score['recovery']:
            recovery_rate = hr_score['recovery']['avg_recovery_per_min']
            if recovery_rate > 20:
                recommendations.append(
                    f"Excellent recovery rate: {recovery_rate:.0f} bpm/min. "
                    f"Your cardiovascular fitness is strong."
                )
            elif recovery_rate < 12:
                recommendations.append(
                    f"Recovery rate is {recovery_rate:.0f} bpm/min. "
                    f"Consider adding interval training to improve recovery between points."
                )

        # Fatigue recommendation
        if 'fatigue' in hr_score and 'fatigue_indicator' in hr_score['fatigue']:
            fatigue = hr_score['fatigue']['interpretation']
            if fatigue == 'high':
                recommendations.append(
                    "Performance declined in later games. "
                    "Consider improving endurance with longer training sessions."
                )

        return recommendations
