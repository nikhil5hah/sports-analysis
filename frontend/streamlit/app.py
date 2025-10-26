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

# Custom CSS - Modern Professional Dashboard
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Main styling */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 3rem;
        letter-spacing: -0.02em;
    }
    
    /* Apply to all Streamlit elements for a cleaner look */
    .element-container {
        background: white !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        margin-bottom: 1rem !important;
        border: 1px solid #e8e8e8 !important;
    }
    
    .element-container:hover {
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15) !important;
        border-color: #667eea !important;
        transform: translateY(-1px) !important;
        transition: all 0.2s ease !important;
    }
    
    /* Metrics value styling */
    [data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Metrics label styling */
    [data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Delta styling */
    [data-testid="stMetricDelta"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Section headers */
    h2 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1e293b;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    /* Subsection headers */
    h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #475569;
        margin-bottom: 0.75rem;
    }
    
    /* Warning box */
    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Success box */
    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
    """Format duration in minutes to readable format (e.g., "1 min 23 secs" or "1 hr 3 mins 45 secs")."""
    if minutes <= 0:
        return "0 secs"
    
    total_seconds = int(minutes * 60)
    
    hours = total_seconds // 3600
    mins = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours} hr")
        if hours > 1:
            parts[-1] = parts[-1] + "s"
    
    if mins > 0:
        parts.append(f"{mins} min")
        if mins > 1:
            parts[-1] = parts[-1] + "s"
    
    if secs > 0:
        parts.append(f"{secs} sec")
        if secs > 1:
            parts[-1] = parts[-1] + "s"
    
    if total_seconds < 60:
        # For very short durations, always show seconds
        return f"{secs} sec{'s' if secs != 1 else ''}"
    
    return " ".join(parts)

def format_metric_value(value: Any, metric_name: str) -> str:
    """Format metric values based on type."""
    if value is None:
        return "N/A"
    
    # Round up integer metrics
    integer_metrics = ['number_of_games', 'number_of_rallies', 'rallies_per_game', 'shots_detected']
    if metric_name in integer_metrics:
        return str(int(np.ceil(value)) if isinstance(value, (int, float)) else value)
    
    # Format duration metrics as readable text
    duration_metrics = ['warm_up_length', 'cool_down_length', 'total_session_duration', 
                       'total_playing_time', 'total_rest_time', 'longest_rally_length', 'rest_between_games']
    if metric_name in duration_metrics:
        return format_time_duration(value) if isinstance(value, (int, float)) else str(value)
    
    # Default formatting
    return str(value)

def format_confidence(confidence: float) -> str:
    """Format confidence as percentage."""
    return f"{int(confidence * 100)}%"

def get_data_sources_for_metric(metric_name: str) -> str:
    """Get the data sources used for a metric."""
    data_sources_map = {
        'warm_up_length': 'Heart rate',
        'cool_down_length': 'Heart rate',
        'number_of_games': 'Heart rate',
        'number_of_rallies': 'Heart rate',
        'total_session_duration': 'Timestamp',
        'total_playing_time': 'Heart rate (Zone-based)',
        'total_rest_time': 'Heart rate (Zone-based)',
        'longest_rally_length': 'Heart rate',
        'rallies_per_game': 'Heart rate',
        'rest_between_games': 'Heart rate',
        'shots_detected': 'Accelerometer (X, Y, Z axes)',
        'avg_playing_heart_rate': 'Heart rate (Zones 3,4,5)',
        'avg_rest_heart_rate': 'Heart rate (Zones 1,2)'
    }
    return data_sources_map.get(metric_name, 'Multiple sensors')

def get_logic_for_metric(metric_name: str) -> str:
    """Get the logic/algorithm description for a metric."""
    logic_map = {
        'warm_up_length': 'HR spike detection + time cap (3-5 min)',
        'cool_down_length': 'Last 20% HR decrease pattern',
        'number_of_games': 'Count rest periods >2 min',
        'number_of_rallies': 'HR elevation periods (15% baseline)',
        'total_session_duration': 'Timestamp difference',
        'total_playing_time': 'Sum time in HR Zones 3, 4, 5',
        'total_rest_time': 'Sum time in HR Zones 1, 2',
        'longest_rally_length': 'Max rally duration (capped at 60s)',
        'rallies_per_game': 'Total rallies / games',
        'rest_between_games': 'Avg rest periods >2 min',
        'shots_detected': 'Accelerometer peak detection',
        'avg_playing_heart_rate': 'Mean HR during Zones 3, 4, 5',
        'avg_rest_heart_rate': 'Mean HR during Zones 1, 2'
    }
    return logic_map.get(metric_name, 'Pattern detection')

def display_analysis_results(analysis_data, raw_data):
    """Display the analysis results in the Streamlit interface."""
    
    # Session Analysis with professional styling
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-family: 'Inter', sans-serif; font-size: 2.5rem; font-weight: 700; 
                   color: #1e293b; margin-bottom: 0.5rem;">📊 Session Analysis</h1>
        <div style="width: 80px; height: 4px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    metrics = analysis_data['metrics']
    
    # Create 3 columns
    col1, col2, col3 = st.columns(3)
    
    # Column 1: Timings ⏱️
    with col1:
        st.markdown('<div style="text-align: center; font-size: 2rem; margin-bottom: 1rem;">⏱️</div>', unsafe_allow_html=True)
        
        # Total Session Duration
        duration = analysis_data['session_summary']['total_duration_minutes']
        st.metric("Total Session Duration", format_time_duration(duration))
        
        # Warm-up Time
        warmup_result = metrics.get('warm_up_length')
        if warmup_result and warmup_result.value > 0:
            st.metric("Warm-up Time", format_metric_value(warmup_result.value, 'warm_up_length'))
        else:
            st.metric("Warm-up Time", "N/A")
        
        # Total Playing Time
        playing_time_result = metrics.get('total_playing_time')
        if playing_time_result and playing_time_result.value > 0:
            st.metric("Total Playing Time", format_metric_value(playing_time_result.value, 'total_playing_time'))
        else:
            st.metric("Total Playing Time", "N/A")
        
        # Total Rest Time
        rest_time_result = metrics.get('total_rest_time')
        if rest_time_result and rest_time_result.value > 0:
            st.metric("Total Rest Time", format_metric_value(rest_time_result.value, 'total_rest_time'))
        else:
            # Calculate as remainder
            warmup_val = warmup_result.value if (warmup_result and warmup_result.value > 0) else 0
            playing_val = playing_time_result.value if (playing_time_result and playing_time_result.value > 0) else 0
            cooldown_val = metrics.get('cool_down_length').value if (metrics.get('cool_down_length') and metrics.get('cool_down_length').value > 0) else 0
            rest_val = max(0, duration - warmup_val - playing_val - cooldown_val)
            st.metric("Total Rest Time", format_time_duration(rest_val))
        
        # Total Cool-down Time
        cooldown_result = metrics.get('cool_down_length')
        if cooldown_result and cooldown_result.value > 0:
            st.metric("Total Cool-down Time", format_metric_value(cooldown_result.value, 'cool_down_length'))
        else:
            st.metric("Total Cool-down Time", "N/A")
        
        # Longest Rally Length
        longest_rally_result = metrics.get('longest_rally_length')
        if longest_rally_result and longest_rally_result.confidence > 0.5:
            st.metric("Longest Rally (WIP)", format_metric_value(longest_rally_result.value, 'longest_rally_length'))
        else:
            st.metric("Longest Rally (WIP)", "N/A")
        
        # Avg Rest Between Games
        rest_between_result = metrics.get('rest_between_games')
        if rest_between_result and rest_between_result.confidence > 0.5:
            st.metric("Avg Rest Between Games", format_metric_value(rest_between_result.value, 'rest_between_games'))
        else:
            st.metric("Avg Rest Between Games", "N/A")
    
    # Column 2: Games & Rallies 🎾
    with col2:
        st.markdown('<div style="text-align: center; font-size: 2rem; margin-bottom: 1rem;">🎾</div>', unsafe_allow_html=True)
        
        # Total Number of Games
        games_result = metrics.get('number_of_games')
        if games_result and games_result.confidence > 0.5:
            st.metric("Total Games", format_metric_value(games_result.value, 'number_of_games'))
        else:
            st.metric("Total Games", "N/A")
        
        # Total Number of Rallies
        rallies_result = metrics.get('number_of_rallies')
        if rallies_result and rallies_result.confidence > 0.5:
            st.metric("Total Rallies (WIP)", format_metric_value(rallies_result.value, 'number_of_rallies'))
        else:
            st.metric("Total Rallies (WIP)", "N/A")
        
        # Avg Rallies Per Game
        rallies_per_game_result = metrics.get('rallies_per_game')
        if rallies_per_game_result and rallies_per_game_result.confidence > 0.5:
            st.metric("Avg Rallies/Game (WIP)", format_metric_value(rallies_per_game_result.value, 'rallies_per_game'))
        else:
            st.metric("Avg Rallies/Game (WIP)", "N/A")
        
        # Total Number of Shots
        shots_result = metrics.get('shots_detected')
        if shots_result and shots_result.confidence > 0.5:
            st.metric("Total Shots", format_metric_value(shots_result.value, 'shots_detected'))
        else:
            st.metric("Total Shots", "No Data")
        
        # Highest Shots Per Rally
        st.metric("Highest Shots/Rally", "TBD")  # To be implemented
        
        # Avg Shots Per Rally
        if shots_result and rallies_result and shots_result.confidence > 0.5 and rallies_result.confidence > 0.5:
            avg_shots = shots_result.value / rallies_result.value if rallies_result.value > 0 else 0
            st.metric("Avg Shots/Rally", f"{avg_shots:.1f}")
        else:
            st.metric("Avg Shots/Rally", "N/A")
    
    # Column 3: Heart Rate ❤️
    with col3:
        st.markdown('<div style="text-align: center; font-size: 2rem; margin-bottom: 1rem;">❤️</div>', unsafe_allow_html=True)
        
        # Avg Heart Rate
        avg_hr = analysis_data['session_summary'].get('avg_heart_rate', 0)
        if avg_hr > 0:
            st.metric("Avg Heart Rate", f"{avg_hr:.0f} bpm")
        else:
            st.metric("Avg Heart Rate", "N/A")
        
        # Max Heart Rate
        max_hr = analysis_data['session_summary'].get('max_heart_rate', 0)
        if max_hr > 0:
            st.metric("Max Heart Rate", f"{max_hr:.0f} bpm")
        else:
            st.metric("Max Heart Rate", "N/A")
        
        # Avg Playing Heart Rate
        avg_playing_hr_result = metrics.get('avg_playing_heart_rate')
        if avg_playing_hr_result and avg_playing_hr_result.value > 0:
            st.metric("Avg Playing HR", f"{avg_playing_hr_result.value:.0f} bpm")
        else:
            st.metric("Avg Playing HR", "N/A")
        
        # Avg Rest Heart Rate
        avg_rest_hr_result = metrics.get('avg_rest_heart_rate')
        if avg_rest_hr_result and avg_rest_hr_result.value > 0:
            st.metric("Avg Rest HR", f"{avg_rest_hr_result.value:.0f} bpm")
        else:
            st.metric("Avg Rest HR", "N/A")
    
    # Visualizations with professional styling
    st.markdown("""
    <div style="margin-top: 3rem; margin-bottom: 1rem;">
        <h1 style="font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 700; 
                   color: #1e293b; margin-bottom: 0.5rem;">📈 Performance Visualizations</h1>
        <div style="width: 80px; height: 4px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Session Breakdown Charts - Side by Side
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Session Breakdown")
        fig_pie = create_session_breakdown_chart(raw_data, analysis_data)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("Heart Rate Zone Distribution")
        fig_zones = create_zone_distribution_chart(raw_data, analysis_data)
        st.plotly_chart(fig_zones, use_container_width=True)
    
    # Heart Rate Over Time (Simple)
    st.subheader("Heart Rate Over Time")
    fig_hr = create_simple_heart_rate_chart(raw_data)
    st.plotly_chart(fig_hr, use_container_width=True)
    
    # Session Phases Timeline
    st.subheader("Session Phases Timeline (WIP)")
    fig_phases = create_session_phases_chart(raw_data, analysis_data)
    st.plotly_chart(fig_phases, use_container_width=True)
    
    # Data Quality (toggle)
    with st.expander("📊 Data Quality"):
        # Recommendations inside Data Quality
        if analysis_data['recommendations']:
            st.subheader("💡 Recommendations")
            for recommendation in analysis_data['recommendations']:
                st.warning(recommendation)
            
            st.divider()
        
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
    
    # Detailed Analysis with professional styling
    st.markdown("""
    <div style="margin-top: 3rem; margin-bottom: 1rem;">
        <h1 style="font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 700; 
                   color: #1e293b; margin-bottom: 0.5rem;">🔬 Detailed Analysis</h1>
        <div style="width: 80px; height: 4px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a table showing all metrics
    metric_table_data = []
    for metric_name, result in analysis_data['metrics'].items():
        metric_table_data.append({
            'Metric': metric_name.replace('_', ' ').title(),
            'Value': format_metric_value(result.value, metric_name),
            'Confidence': format_confidence(result.confidence),
            'Status': '✅ Good' if result.confidence > 0.7 else '⚠️ Moderate' if result.confidence > 0.4 else '❌ Low'
        })
    
    metric_df = pd.DataFrame(metric_table_data)
    st.dataframe(metric_df, use_container_width=True, hide_index=True)
    
    # Expandable sections for each metric with full details including logic
    # Note: Can't nest expanders, so showing all metrics directly
    for metric_name, result in analysis_data['metrics'].items():
        with st.expander(f"🔍 {metric_name.replace('_', ' ').title()}"):
            # Create a detailed table
            detail_data = {
                'Property': ['Metric Name', 'Value', 'Confidence', 'Algorithm', 'Data Source', 'Logic'],
                'Value': [
                    metric_name.replace('_', ' ').title(),
                    format_metric_value(result.value, metric_name),
                    format_confidence(result.confidence),
                    result.metadata.get('algorithm', 'N/A'),
                    get_data_sources_for_metric(metric_name),
                    get_logic_for_metric(metric_name)
                ]
            }
            detail_df = pd.DataFrame(detail_data)
            st.dataframe(detail_df, use_container_width=True, hide_index=True)
            
            # Show additional metadata
            if result.metadata and len(result.metadata) > 1:
                st.write("**Additional Metadata:**")
                metadata_df = pd.DataFrame([
                    {'Key': k, 'Value': str(v)}
                    for k, v in result.metadata.items()
                    if k not in ['algorithm', 'error']
                ])
                st.dataframe(metadata_df, use_container_width=True, hide_index=True)

def create_simple_heart_rate_chart(raw_data):
    """Create professional heart rate over time chart."""
    fig = go.Figure()
    
    # Add heart rate line with gradient effect
    fig.add_trace(go.Scatter(
        x=raw_data['timestamp'],
        y=raw_data['heart_rate'],
        mode='lines',
        name='Heart Rate',
        line=dict(
            color='#ef4444',
            width=3,
            shape='spline',
            smoothing=1.0
        ),
        fill='tonexty',
        fillcolor='rgba(239, 68, 68, 0.1)'
    ))
    
    # Add HR zones as backgrounds
    max_hr = raw_data['heart_rate'].max() * 1.05
    zones = [
        (0, max_hr * 0.5, 'Zone 0', '#f3f4f6'),
        (max_hr * 0.5, max_hr * 0.6, 'Zone 1', '#dbeafe'),
        (max_hr * 0.6, max_hr * 0.7, 'Zone 2', '#bfdbfe'),
        (max_hr * 0.7, max_hr * 0.8, 'Zone 3', '#93c5fd'),
        (max_hr * 0.8, max_hr * 0.9, 'Zone 4', '#60a5fa'),
        (max_hr * 0.9, max_hr, 'Zone 5', '#ef4444')
    ]
    
    fig.update_layout(
        title={
            'text': "Heart Rate Over Time",
            'font': {'size': 20, 'family': 'Inter'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Time",
        yaxis_title="Heart Rate (bpm)",
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        hovermode='x unified',
        xaxis=dict(
            showgrid=True,
            gridcolor='#f1f5f9',
            gridwidth=1
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#f1f5f9',
            gridwidth=1,
            range=[raw_data['heart_rate'].min() * 0.9, raw_data['heart_rate'].max() * 1.1]
        )
    )
    
    return fig

def create_session_phases_chart(raw_data, analysis_data):
    """Create timeline chart showing session phases (warm-up, games, rest, cool-down)."""
    fig = go.Figure()
    
    # Get session boundaries
    session_start = raw_data['timestamp'].iloc[0]
    session_end = raw_data['timestamp'].iloc[-1]
    
    # Track current position
    current_time = session_start
    
    # Warm-up phase
    warmup_result = analysis_data['metrics'].get('warm_up_length')
    if warmup_result and warmup_result.data_points:
        start_idx, end_idx = warmup_result.data_points[0]
        warmup_end = raw_data['timestamp'].iloc[end_idx]
        duration = (warmup_end - current_time).total_seconds() / 60
        
        fig.add_trace(go.Bar(
            x=[duration],
            y=['Phase'],
            name='Warm-up',
            marker_color='blue',
            text=f'Warm-up ({duration:.1f} min)',
            textposition='inside',
            orientation='h'
        ))
        current_time = warmup_end
    
    # Games and rest periods
    games_result = analysis_data['metrics'].get('number_of_games')
    if games_result and games_result.value > 0:
        num_games = int(games_result.value)
        remaining_duration = (session_end - current_time).total_seconds() / 60
        phase_duration = remaining_duration / (num_games * 2)  # Game + rest for each
        
        for i in range(num_games):
            # Game phase
            fig.add_trace(go.Bar(
                x=[phase_duration],
                y=['Phase'],
                name=f'Game {i+1}',
                marker_color='yellow',
                text=f'Game {i+1} ({phase_duration:.1f} min)',
                textposition='inside',
                orientation='h'
            ))
            
            # Rest phase (except after last game)
            if i < num_games - 1:
                fig.add_trace(go.Bar(
                    x=[phase_duration * 0.5],  # Rest is typically shorter
                    y=['Phase'],
                    name='Rest',
                    marker_color='green',
                    text=f'Rest ({phase_duration * 0.5:.1f} min)',
                    textposition='inside',
                    orientation='h'
                ))
    
    # Cool-down phase
    cooldown_result = analysis_data['metrics'].get('cool_down_length')
    if cooldown_result and cooldown_result.data_points:
        start_idx, end_idx = cooldown_result.data_points[0]
        cooldown_start = raw_data['timestamp'].iloc[start_idx]
        duration = (session_end - cooldown_start).total_seconds() / 60
        
        fig.add_trace(go.Bar(
            x=[duration],
            y=['Phase'],
            name='Cool-down',
            marker_color='lightblue',
            text=f'Cool-down ({duration:.1f} min)',
            textposition='inside',
            orientation='h'
        ))
    
    fig.update_layout(
        title="Session Phases Timeline",
        xaxis_title="Duration (minutes)",
        yaxis_title="",
        barmode='stack',
        height=300,
        showlegend=False
    )
    
    return fig

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
    session_start = raw_data['timestamp'].iloc[0]
    session_end = raw_data['timestamp'].iloc[-1]
    warmup_end_time = session_start  # Default to session start
    
    warmup_result = analysis_data['metrics'].get('warm_up_length')
    if warmup_result and warmup_result.data_points:
        start_idx, end_idx = warmup_result.data_points[0]
        warmup_start_time = raw_data['timestamp'].iloc[start_idx]
        warmup_end_time = raw_data['timestamp'].iloc[end_idx]
        fig.add_vrect(
            x0=warmup_start_time,
            x1=warmup_end_time,
            fillcolor="blue",
            opacity=0.2,
            annotation_text="Warm-up",
            annotation_position="top left",
            layer="below"
        )
    
    # Add game overlays
    games_result = analysis_data['metrics'].get('number_of_games')
    if games_result and games_result.value > 0:
        # Calculate game periods as equal segments
        num_games = int(games_result.value)
        session_duration = (session_end - session_start).total_seconds()
        
        # Calculate duration per game (after warm-up)
        post_warmup_duration = (session_end - warmup_end_time).total_seconds()
        game_duration = post_warmup_duration / num_games
        
        for i in range(num_games):
            # Ensure warmup_end_time is a Timestamp
            if not isinstance(warmup_end_time, pd.Timestamp):
                warmup_end_time = pd.to_datetime(warmup_end_time)
            
            game_start = warmup_end_time + pd.Timedelta(seconds=i * game_duration)
            game_end = warmup_end_time + pd.Timedelta(seconds=(i + 1) * game_duration)
            
            # Skip if past session end
            if game_start > session_end:
                break
            
            fig.add_vrect(
                x0=game_start,
                x1=min(game_end, session_end),
                fillcolor="yellow",
                opacity=0.15,
                annotation_text=f"Game {i+1}",
                annotation_position="bottom",
                layer="below"
            )
    
    # Add cool-down period
    cooldown_result = analysis_data['metrics'].get('cool_down_length')
    if cooldown_result and cooldown_result.data_points:
        start_idx, end_idx = cooldown_result.data_points[0]
        cooldown_start_time = raw_data['timestamp'].iloc[start_idx]
        cooldown_end_time = raw_data['timestamp'].iloc[end_idx]
        fig.add_vrect(
            x0=cooldown_start_time,
            x1=cooldown_end_time,
            fillcolor="green",
            opacity=0.2,
            annotation_text="Cool-down",
            annotation_position="top right",
            layer="below"
        )
    
    fig.update_layout(
        title="Heart Rate Over Time with Session Phases",
        xaxis_title="Time",
        yaxis_title="Heart Rate (bpm)",
        height=450,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
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

def create_session_breakdown_chart(raw_data, analysis_data):
    """Create modern session breakdown donut chart."""
    metrics = analysis_data['metrics']
    
    # Get session duration
    total_duration = metrics.get('total_session_duration')
    if total_duration and total_duration.value:
        total_mins = total_duration.value
    else:
        total_mins = analysis_data['session_summary'].get('total_duration_minutes', 0)
    
    if total_mins <= 0:
        fig = go.Figure()
        fig.update_layout(title="No Session Data Available", height=400)
        return fig
    
    # Get different components
    warmup_mins = metrics.get('warm_up_length')
    warmup_value = warmup_mins.value if warmup_mins and warmup_mins.value > 0 else 0
    
    cooldown_mins = metrics.get('cool_down_length')
    cooldown_value = cooldown_mins.value if cooldown_mins and cooldown_mins.value > 0 else 0
    
    playing_mins = metrics.get('total_playing_time')
    playing_value = playing_mins.value if playing_mins and playing_mins.value > 0 else 0
    
    # Calculate rest time as remainder
    accounted_time = warmup_value + playing_value + cooldown_value
    rest_value = max(0, total_mins - accounted_time)
    
    # Prepare data
    labels = []
    values = []
    colors = []
    
    components = [
        ('Warm-up', warmup_value, '#6366f1'),      # Indigo
        ('Playing Time', playing_value, '#ef4444'), # Red
        ('Rest', rest_value, '#10b981'),            # Green
        ('Cool-down', cooldown_value, '#6b7280')    # Grey
    ]
    
    for label, value, color in components:
        if value > 0:
            labels.append(f'{label}<br>{format_time_duration(value)}')
            values.append(value)
            colors.append(color)
    
    if not values:
        labels = [f'Full Session<br>{format_time_duration(total_mins)}']
        values = [total_mins]
        colors = ['#8b5cf6']
    
    # Create modern donut chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='outside',
        textfont_size=11,
        hole=0.4,
        marker=dict(
            line=dict(color='#ffffff', width=3)
        ),
        hovertemplate='<b>%{label}</b><br>Duration: %{customdata}<br>Percentage: %{percent}<extra></extra>',
        customdata=[format_time_duration(v) for v in values]
    )])
    
    fig.update_layout(
        title={
            'text': "Session Breakdown",
            'x': 0.5,
            'font': {'size': 18, 'family': 'Inter'},
            'xanchor': 'center'
        },
        height=450,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1,
            font=dict(family='Inter', size=11)
        ),
        font=dict(family='Inter'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        annotations=[
            dict(
                text=f'<b>{format_time_duration(total_mins)}</b>',
                x=0.5,
                y=0.5,
                font_size=16,
                showarrow=False,
                font_family='Inter'
            )
        ]
    )
    
    return fig

def create_zone_distribution_chart(raw_data, analysis_data):
    """Create pie chart showing time spent in each HR zone."""
    metrics = analysis_data['metrics']
    
    # Get zone information from playing time and rest time detectors
    playing_time_result = metrics.get('total_playing_time')
    rest_time_result = metrics.get('total_rest_time')
    
    # Get zone distribution from metadata if available
    playing_zones_dist = {}
    if playing_time_result and playing_time_result.metadata:
        playing_zones_dist = playing_time_result.metadata.get('zone_distribution', {})
    
    # Calculate zone times from metadata
    zone_data = {
        'Warm-up': 0,
        'Zone 1 (Rest)': 0,
        'Zone 2 (Light Activity)': 0,
        'Zone 3 (Aerobic)': 0,
        'Zone 4 (Hard)': 0,
        'Zone 5 (Max)': 0,
        'Cool-down': 0
    }
    
    # Get warm-up and cool-down times
    warmup_result = metrics.get('warm_up_length')
    if warmup_result and warmup_result.value > 0:
        zone_data['Warm-up'] = warmup_result.value
    
    cooldown_result = metrics.get('cool_down_length')
    if cooldown_result and cooldown_result.value > 0:
        zone_data['Cool-down'] = cooldown_result.value
    
    # Get playing time (typically zones 3, 4, 5)
    if playing_time_result and playing_time_result.value > 0:
        playing_time = playing_time_result.value
        # Distribute playing time across zones (estimate)
        zone_data['Zone 3 (Aerobic)'] = playing_time * 0.5
        zone_data['Zone 4 (Hard)'] = playing_time * 0.3
        zone_data['Zone 5 (Max)'] = playing_time * 0.2
    
    # Get rest time (typically zones 1, 2)
    if rest_time_result and rest_time_result.value > 0:
        rest_time = rest_time_result.value
        # Distribute rest time across zones (estimate)
        zone_data['Zone 1 (Rest)'] = rest_time * 0.6
        zone_data['Zone 2 (Light Activity)'] = rest_time * 0.4
    
    # Prepare data for pie chart
    labels = []
    values = []
    colors = []
    
    # Define colors for each zone
    zone_colors = {
        'Warm-up': '#87CEEB',           # Sky blue
        'Zone 1 (Rest)': '#90EE90',      # Light green
        'Zone 2 (Light Activity)': '#98FB98',  # Pale green
        'Zone 3 (Aerobic)': '#FFD700',    # Gold
        'Zone 4 (Hard)': '#FF8C00',       # Dark orange
        'Zone 5 (Max)': '#FF4500',        # Red orange
        'Cool-down': '#D3D3D3'           # Light grey
    }
    
    for zone, time in zone_data.items():
        if time > 0:
            labels.append(f'{zone}\n{format_time_duration(time)}')
            values.append(time)
            colors.append(zone_colors.get(zone, '#8B9DC3'))
    
    # Fallback if no zone data
    if not values:
        # Use session duration if available
        total_duration = metrics.get('total_session_duration')
        if total_duration and total_duration.value > 0:
            labels = [f'Full Session\n{format_time_duration(total_duration.value)}']
            values = [total_duration.value]
            colors = ['#8B9DC3']
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='percent',
        textposition='outside',
        textfont_size=10,
        hole=0.3,  # Donut chart
        hovertemplate='<b>%{label}</b><br>Duration: %{customdata}<extra></extra>',
        customdata=[format_time_duration(v) for v in values]
    )])
    
    fig.update_layout(
        title={
            'text': "Time in Heart Rate Zones",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 14}
        },
        height=450,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.05
        )
    )
    
    return fig

if __name__ == "__main__":
    main()
