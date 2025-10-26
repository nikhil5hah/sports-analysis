"""
Squash Performance Analysis - Streamlit App

Main application for visualizing and analyzing squash performance data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
from datetime import datetime, timedelta
import io
from typing import Any

# Import our custom modules
from data.ingestion.data_ingestion import FitnessDataImporter
from core.modular_analysis import ModularAnalysisEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Squash Performance Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">📈 Squash Performance Analysis</h1>', unsafe_allow_html=True)
    
    # Sidebar for user inputs
    st.sidebar.header("Session Configuration")
    
    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload Fitness Data",
        type=['gpx', 'fit'],
        help="Upload GPX (Strava export) or FIT files from your fitness tracker"
    )
    
    # Session parameters
    hand_position = st.sidebar.selectbox(
        "Watch Position",
        options=['playing_hand', 'non_playing_hand'],
        help="Was the watch worn on your racket playing hand?"
    )
    
    session_type = st.sidebar.selectbox(
        "Session Type",
        options=['training', 'match'],
        help="Was this a training session or match?"
    )
    
    # Analysis options
    st.sidebar.header("Analysis Options")
    show_detailed_analysis = st.sidebar.checkbox("Show Detailed Analysis", value=True)
    show_event_detection = st.sidebar.checkbox("Show Event Detection", value=True)
    show_performance_trends = st.sidebar.checkbox("Show Performance Trends", value=True)
    
    # Initialize session state
    if 'analysis_data' not in st.session_state:
        st.session_state.analysis_data = None
    if 'raw_data' not in st.session_state:
        st.session_state.raw_data = None
    
    # Main content area
    if uploaded_file is not None:
        try:
            # Process uploaded file
            with st.spinner("Processing fitness data..."):
                data = process_uploaded_file(uploaded_file, hand_position, session_type)
                
            if data is not None:
                st.session_state.raw_data = data['raw_data']
                st.session_state.analysis_data = data['analysis']
                
                # Display results
                display_analysis_results(st.session_state.analysis_data, st.session_state.raw_data)
            else:
                st.error("Failed to process the uploaded file. Please check the file format.")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            logger.error(f"Error processing file: {e}")
    
    else:
        # Show sample data option
        st.info("👆 Upload a GPX or FIT file to get started, or use sample data below for testing.")
        
        if st.button("Generate Sample Data"):
            with st.spinner("Generating sample data..."):
                sample_data = generate_sample_data()
                st.session_state.raw_data = sample_data['raw_data']
                st.session_state.analysis_data = sample_data['analysis']
                
                st.success("Sample data generated successfully!")
                display_analysis_results(st.session_state.analysis_data, st.session_state.raw_data)

def process_uploaded_file(uploaded_file, hand_position, session_type):
    """Process the uploaded fitness data file."""
    try:
        # Initialize components
        importer = FitnessDataImporter()
        analyzer = ModularAnalysisEngine()
        
        # Read file content
        file_content = uploaded_file.read()
        
        # Determine file type and process
        if uploaded_file.name.lower().endswith('.gpx'):
            # Save temporary file for GPX processing
            with open('temp_file.gpx', 'wb') as f:
                f.write(file_content)
            
            df = importer.import_gpx_file('temp_file.gpx')
            df = importer.preprocess_data(df)
            
        elif uploaded_file.name.lower().endswith('.fit'):
            # Save temporary file for FIT processing
            with open('temp_file.fit', 'wb') as f:
                f.write(file_content)
            
            df = importer.import_fit_file('temp_file.fit')
            df = importer.preprocess_data(df)
        
        else:
            st.error("Unsupported file format. Please upload GPX or FIT files.")
            return None
        
        # Set session context and run analysis
        analyzer.set_session_context(hand_position, session_type)
        analysis = analyzer.analyze_session(df)
        
        # Combine results
        result = {
            'raw_data': df,
            'analysis': analysis,
            'session_info': importer.session_info
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise e

def generate_sample_data():
    """Generate sample squash session data for testing."""
    np.random.seed(42)
    
    # Create sample data
    timestamps = pd.date_range('2024-01-01 10:00:00', periods=1200, freq='1s')
    
    # Simulate a squash session
    hr_data = []
    cadence_data = []
    
    # Warm-up (first 300 points - 5 minutes)
    for i in range(300):
        hr_data.append(80 + i * 0.1 + np.random.normal(0, 5))
        cadence_data.append(60 + np.random.normal(0, 5))
    
    # Main session with rallies and rest
    for i in range(300, 1200):
        cycle_position = (i - 300) % 60
        
        if cycle_position < 40:  # Rally period
            hr_data.append(140 + np.random.normal(0, 15))
            cadence_data.append(100 + np.random.normal(0, 20))
        else:  # Rest period
            hr_data.append(110 + np.random.normal(0, 8))
            cadence_data.append(70 + np.random.normal(0, 10))
    
    # Add some performance deterioration towards the end
    for i in range(900, 1200):
        deterioration_factor = (i - 900) / 300
        hr_data[i] += deterioration_factor * 10
        cadence_data[i] -= deterioration_factor * 5
    
    sample_df = pd.DataFrame({
        'timestamp': timestamps,
        'heart_rate': hr_data,
        'cadence': cadence_data,
        'time_diff': 1.0,
        'cumulative_time': np.arange(1200)
    })
    
    # Run analysis using modular framework
    analyzer = ModularAnalysisEngine()
    analyzer.set_session_context('playing_hand', 'training')
    analysis = analyzer.analyze_session(sample_df)
    
    # Add session info for compatibility
    analysis['session_info'] = {
        'hand_position': 'playing_hand',
        'session_type': 'training',
        'duration_minutes': 20.0
    }
    
    return {
        'raw_data': sample_df,
        'analysis': analysis
    }

def format_time_duration(minutes: float) -> str:
    """Format duration in minutes to MM:SS format."""
    if minutes <= 0:
        return "0:00"
    
    total_seconds = int(minutes * 60)
    mins = total_seconds // 60
    secs = total_seconds % 60
    return f"{mins}:{secs:02d}"

def format_metric_value(value: Any, metric_name: str) -> str:
    """Format metric values based on type."""
    if value is None:
        return "N/A"
    
    # Round up integer metrics
    integer_metrics = ['number_of_games', 'number_of_rallies', 'rallies_per_game', 'shots_detected']
    if metric_name in integer_metrics:
        return str(int(np.ceil(value)) if isinstance(value, (int, float)) else value)
    
    # Format duration metrics as MM:SS
    duration_metrics = ['warm_up_length', 'cool_down_length', 'total_session_duration', 
                       'total_playing_time', 'longest_rally_length', 'rest_between_games']
    if metric_name in duration_metrics:
        return format_time_duration(value) if isinstance(value, (int, float)) else str(value)
    
    # Default formatting
    return str(value)

def display_analysis_results(analysis_data, raw_data):
    """Display the analysis results in the Streamlit interface."""
    
    # Session Overview
    st.header("📊 Session Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        duration = analysis_data['session_summary']['total_duration_minutes']
        st.metric("Duration", format_time_duration(duration))
    
    with col2:
        avg_hr = analysis_data['session_summary'].get('avg_heart_rate', 0)
        st.metric("Avg Heart Rate", f"{avg_hr:.0f} bpm")
    
    with col3:
        max_hr = analysis_data['session_summary'].get('max_heart_rate', 0)
        st.metric("Max Heart Rate", f"{max_hr:.0f} bpm")
    
    with col4:
        rallies = analysis_data['session_summary'].get('total_rallies', 0)
        st.metric("Total Rallies", format_metric_value(rallies, 'number_of_rallies'))
    
    # Key Insights
    st.header("🔍 Key Insights")
    
    # Display metric results
    metrics = analysis_data['metrics']
    
    # Warm-up
    warmup_result = metrics.get('warm_up_length')
    if warmup_result and warmup_result.confidence > 0.5:
        st.info(f"🔥 Warm-up Duration: {format_metric_value(warmup_result.value, 'warm_up_length')}")
    
    # Cool-down
    cooldown_result = metrics.get('cool_down_length')
    if cooldown_result and cooldown_result.confidence > 0.5:
        st.info(f"❄️ Cool-down Duration: {format_metric_value(cooldown_result.value, 'cool_down_length')}")
    
    # Games
    games_result = metrics.get('number_of_games')
    if games_result and games_result.confidence > 0.5:
        st.info(f"🎾 Number of Games: {format_metric_value(games_result.value, 'number_of_games')}")
    
    # Playing time
    playing_time_result = metrics.get('total_playing_time')
    if playing_time_result and playing_time_result.confidence > 0.5:
        st.info(f"⏱️ Total Playing Time: {format_metric_value(playing_time_result.value, 'total_playing_time')}")
    
    # Longest rally
    longest_rally_result = metrics.get('longest_rally_length')
    if longest_rally_result and longest_rally_result.confidence > 0.5:
        st.info(f"🏆 Longest Rally: {format_metric_value(longest_rally_result.value, 'longest_rally_length')} (both players)")
    
    # Data Quality
    st.header("📈 Data Quality")
    quality = analysis_data['data_quality']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Overall Quality", quality['overall_quality'].title())
        st.metric("Data Points", f"{quality['total_data_points']:,}")
    
    with col2:
        st.metric("Metrics Detected", f"{analysis_data['session_summary']['metrics_detected']}/{analysis_data['session_summary']['metrics_total']}")
        
        # Show available data fields
        available_fields = analysis_data['session_summary']['available_data_fields']
        st.write("**Available Data:**")
        for field in available_fields:
            st.write(f"• {field}")
    
    # Recommendations
    if analysis_data['recommendations']:
        st.header("💡 Recommendations")
        for recommendation in analysis_data['recommendations']:
            st.warning(recommendation)
    
    # Visualizations
    st.header("📈 Performance Visualizations")
    
    # Heart Rate Over Time
    fig_hr = create_heart_rate_chart(raw_data, analysis_data)
    st.plotly_chart(fig_hr, use_container_width=True)
    
    # Metric Confidence Chart
    fig_confidence = create_confidence_chart(analysis_data['metrics'])
    st.plotly_chart(fig_confidence, use_container_width=True)
    
    # Detailed Analysis (if requested)
    if st.checkbox("Show Detailed Analysis"):
        st.header("🔬 Detailed Analysis")
        
        # Show all metric results
        for metric_name, result in analysis_data['metrics'].items():
            st.subheader(f"{metric_name.replace('_', ' ').title()}")
            st.write(f"**Value:** {format_metric_value(result.value, metric_name)}")
            st.write(f"**Confidence:** {result.confidence:.2f}")
            st.write(f"**Algorithm:** {result.metadata.get('algorithm', 'N/A')}")
            
            if result.metadata:
                st.write("**Metadata:**")
                for key, value in result.metadata.items():
                    if key != 'algorithm':
                        st.write(f"• {key}: {value}")
            
            st.write("---")

def create_heart_rate_chart(raw_data, analysis_data):
    """Create heart rate over time chart with event annotations."""
    fig = go.Figure()
    
    # Add heart rate line
    fig.add_trace(go.Scatter(
        x=raw_data['timestamp'],
        y=raw_data['heart_rate'],
        mode='lines',
        name='Heart Rate',
        line=dict(color='red', width=2)
    ))
    
    # Add warm-up period
    warmup_result = analysis_data['metrics'].get('warm_up_length')
    if warmup_result and warmup_result.confidence > 0.5:
        warmup_data_points = warmup_result.data_points
        if warmup_data_points:
            start_idx, end_idx = warmup_data_points[0]
            warmup_start_time = raw_data['timestamp'].iloc[start_idx]
            warmup_end_time = raw_data['timestamp'].iloc[end_idx]
            fig.add_vrect(
                x0=warmup_start_time,
                x1=warmup_end_time,
                fillcolor="lightblue",
                opacity=0.3,
                annotation_text="Warm-up",
                annotation_position="top left"
            )
    
    # Add cool-down period
    cooldown_result = analysis_data['metrics'].get('cool_down_length')
    if cooldown_result and cooldown_result.confidence > 0.5:
        cooldown_data_points = cooldown_result.data_points
        if cooldown_data_points:
            start_idx, end_idx = cooldown_data_points[0]
            cooldown_start_time = raw_data['timestamp'].iloc[start_idx]
            cooldown_end_time = raw_data['timestamp'].iloc[end_idx]
            fig.add_vrect(
                x0=cooldown_start_time,
                x1=cooldown_end_time,
                fillcolor="lightgreen",
                opacity=0.3,
                annotation_text="Cool-down",
                annotation_position="top right"
            )
    
    fig.update_layout(
        title="Heart Rate Over Time",
        xaxis_title="Time",
        yaxis_title="Heart Rate (bpm)",
        height=400
    )
    
    return fig

def create_confidence_chart(metrics):
    """Create chart showing confidence levels for all metrics."""
    metric_names = []
    confidence_values = []
    
    for metric_name, result in metrics.items():
        metric_names.append(metric_name.replace('_', ' ').title())
        confidence_values.append(result.confidence)
    
    fig = go.Figure(data=[
        go.Bar(
            x=metric_names,
            y=confidence_values,
            marker_color=['green' if c > 0.7 else 'orange' if c > 0.4 else 'red' for c in confidence_values]
        )
    ])
    
    fig.update_layout(
        title="Metric Detection Confidence",
        xaxis_title="Metrics",
        yaxis_title="Confidence (0-1)",
        height=400,
        xaxis_tickangle=-45
    )
    
    return fig

if __name__ == "__main__":
    main()
