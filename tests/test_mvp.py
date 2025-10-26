"""
Test script for Squash Performance Analysis MVP

This script tests all the core functionality with sample data.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# Import our modules
from data.ingestion.data_ingestion import FitnessDataImporter
from sports.squash.detectors.event_detection import EventDetector
from sports.squash.detectors.performance_analysis import PerformanceAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_realistic_sample_data():
    """Create realistic sample squash session data."""
    np.random.seed(42)
    
    # Session parameters
    session_duration_minutes = 45
    total_points = session_duration_minutes * 60  # 1-second intervals
    
    timestamps = pd.date_range(
        start='2024-01-15 18:00:00',
        periods=total_points,
        freq='1s'
    )
    
    # Initialize data arrays
    hr_data = []
    cadence_data = []
    speed_data = []
    
    # Phase 1: Warm-up (5 minutes)
    warmup_duration = 5 * 60
    for i in range(warmup_duration):
        # Gradual HR increase during warm-up
        base_hr = 75 + (i / warmup_duration) * 25  # 75 to 100 bpm
        hr_data.append(base_hr + np.random.normal(0, 3))
        cadence_data.append(50 + np.random.normal(0, 5))
        speed_data.append(2 + np.random.normal(0, 0.5))
    
    # Phase 2: Main session (35 minutes)
    main_session_duration = 35 * 60
    
    for i in range(main_session_duration):
        cycle_position = i % 90  # 90-second cycles (60s rally + 30s rest)
        
        if cycle_position < 60:  # Rally period
            # High intensity during rallies
            base_hr = 120 + np.random.normal(0, 15)
            hr_data.append(base_hr)
            cadence_data.append(90 + np.random.normal(0, 15))
            speed_data.append(8 + np.random.normal(0, 2))
        else:  # Rest period
            # Recovery during rest
            base_hr = 100 + np.random.normal(0, 8)
            hr_data.append(base_hr)
            cadence_data.append(60 + np.random.normal(0, 8))
            speed_data.append(3 + np.random.normal(0, 1))
    
    # Phase 3: Cool-down (5 minutes)
    cooldown_duration = 5 * 60
    for i in range(cooldown_duration):
        # Gradual HR decrease during cool-down
        progress = i / cooldown_duration
        base_hr = 100 - progress * 25  # 100 to 75 bpm
        hr_data.append(base_hr + np.random.normal(0, 3))
        cadence_data.append(50 + np.random.normal(0, 5))
        speed_data.append(2 + np.random.normal(0, 0.5))
    
    # Add performance deterioration in the last 10 minutes
    deterioration_start = 35 * 60  # Start deterioration 35 minutes in
    for i in range(deterioration_start, total_points):
        deterioration_factor = (i - deterioration_start) / (total_points - deterioration_start)
        hr_data[i] += deterioration_factor * 10  # HR drift
        cadence_data[i] -= deterioration_factor * 5  # Reduced movement
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'heart_rate': hr_data,
        'cadence': cadence_data,
        'speed': speed_data,
        'time_diff': 1.0,
        'cumulative_time': np.arange(total_points)
    })
    
    return df

def test_data_ingestion():
    """Test the data ingestion module."""
    logger.info("Testing data ingestion...")
    
    importer = FitnessDataImporter()
    
    # Test with sample data
    sample_df = create_realistic_sample_data()
    processed_df = importer.preprocess_data(sample_df)
    
    # Set session context
    importer.set_session_context('playing_hand', 'training')
    
    logger.info(f"✅ Data ingestion test passed")
    logger.info(f"   - Processed {len(processed_df)} data points")
    logger.info(f"   - Session duration: {importer.session_info['duration_minutes']:.1f} minutes")
    
    return processed_df

def test_event_detection(df):
    """Test the event detection module."""
    logger.info("Testing event detection...")
    
    detector = EventDetector(hand_position='playing_hand', session_type='training')
    analysis = detector.analyze_session(df)
    
    logger.info(f"✅ Event detection test passed")
    logger.info(f"   - Warm-up duration: {analysis['warmup']['duration_minutes']:.1f} minutes")
    logger.info(f"   - Rallies detected: {analysis['session_summary']['total_rallies']}")
    logger.info(f"   - Shots detected: {analysis['session_summary']['total_shots']}")
    logger.info(f"   - Rest periods: {len(analysis['rest_periods'])}")
    
    return analysis

def test_performance_analysis(df, event_analysis):
    """Test the performance analysis module."""
    logger.info("Testing performance analysis...")
    
    analyzer = PerformanceAnalyzer()
    analysis = analyzer.comprehensive_analysis(
        df,
        rallies=event_analysis.get('rallies'),
        rest_periods=event_analysis.get('rest_periods')
    )
    
    logger.info(f"✅ Performance analysis test passed")
    
    # Check deterioration detection
    deterioration = analysis['deterioration']
    if deterioration['deterioration_point'] is not None:
        logger.info(f"   - Performance deterioration detected at {deterioration['time_minutes']:.1f} minutes")
        logger.info(f"   - Confidence: {deterioration['confidence']:.1%}")
    else:
        logger.info("   - No significant performance deterioration detected")
    
    # Check intensity zones
    zones = analysis['intensity_zones']['zone_distribution']
    logger.info(f"   - Time in anaerobic zone: {zones['anaerobic']['percentage']:.1f}%")
    logger.info(f"   - Time in threshold zone: {zones['threshold']['percentage']:.1f}%")
    
    return analysis

def run_comprehensive_test():
    """Run comprehensive test of all modules."""
    logger.info("🚀 Starting comprehensive test of Squash Performance Analysis MVP")
    
    try:
        # Test 1: Data Ingestion
        df = test_data_ingestion()
        
        # Test 2: Event Detection
        event_analysis = test_event_detection(df)
        
        # Test 3: Performance Analysis
        performance_analysis = test_performance_analysis(df, event_analysis)
        
        # Test 4: Integration Test
        logger.info("Testing integration...")
        
        # Verify data consistency
        assert len(df) > 0, "Data should not be empty"
        assert 'heart_rate' in df.columns, "Heart rate data should be present"
        assert 'cadence' in df.columns, "Cadence data should be present"
        
        # Verify event detection results
        assert event_analysis['warmup']['duration_minutes'] > 0, "Warm-up should be detected"
        assert event_analysis['session_summary']['total_rallies'] > 0, "Rallies should be detected"
        
        # Verify performance analysis results
        assert performance_analysis['session_summary']['total_duration_minutes'] > 0, "Session duration should be positive"
        assert performance_analysis['intensity_zones']['zone_distribution'], "Intensity zones should be calculated"
        
        logger.info("✅ Integration test passed")
        
        # Summary
        logger.info("\n🎉 All tests passed successfully!")
        logger.info("\n📊 Test Summary:")
        logger.info(f"   - Session Duration: {performance_analysis['session_summary']['total_duration_minutes']:.1f} minutes")
        logger.info(f"   - Average HR: {performance_analysis['session_summary']['avg_heart_rate']:.0f} bpm")
        logger.info(f"   - Max HR: {performance_analysis['session_summary']['max_heart_rate']:.0f} bpm")
        logger.info(f"   - Total Rallies: {performance_analysis['session_summary']['total_rallies']}")
        logger.info(f"   - Warm-up Duration: {event_analysis['warmup']['duration_minutes']:.1f} minutes")
        
        if performance_analysis['deterioration']['deterioration_point'] is not None:
            logger.info(f"   - Performance Deterioration: {performance_analysis['deterioration']['time_minutes']:.1f} minutes")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def create_sample_gpx_file():
    """Create a sample GPX file for testing."""
    import gpxpy
    import gpxpy.gpx
    
    # Create GPX object
    gpx = gpxpy.gpx.GPX()
    
    # Create track
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    
    # Create segment
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    
    # Add points with sample data
    base_time = datetime.now()
    for i in range(100):
        point_time = base_time + timedelta(seconds=i)
        gpx_point = gpxpy.gpx.GPXTrackPoint(
            latitude=37.7749 + i * 0.0001,
            longitude=-122.4194 + i * 0.0001,
            elevation=100 + i * 0.1,
            time=point_time
        )
        gpx_segment.points.append(gpx_point)
    
    # Write to file
    with open('sample_squash_session.gpx', 'w') as f:
        f.write(gpx.to_xml())
    
    logger.info("✅ Sample GPX file created: sample_squash_session.gpx")

if __name__ == "__main__":
    # Run comprehensive test
    success = run_comprehensive_test()
    
    if success:
        print("\n🎯 MVP is ready for use!")
        print("\nTo run the Streamlit app:")
        print("   streamlit run app.py")
        print("\nTo test with your own data:")
        print("   1. Export your Strava activity as GPX")
        print("   2. Upload it through the Streamlit interface")
        print("   3. Configure hand position and session type")
        print("   4. View your performance analysis!")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
    
    # Create sample GPX file
    create_sample_gpx_file()
