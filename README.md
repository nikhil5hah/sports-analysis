# Sports Performance Analysis Platform

A comprehensive dashboard for analyzing squash performance data using fitness tracker data (GPX/FIT files).

## Features

- 📊 **Session Analysis**: Total time, warm-up, playing time, rest
- 🎾 **Games & Rallies**: Detect games, rallies, and shots
- ❤️ **Heart Rate Tracking**: Analyze HR zones and patterns
- 📈 **Visualizations**: Interactive charts and graphs
- 🔧 **Modular Metrics Framework**: Easy to extend

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/nikhil5hah/sports-analysis.git
cd sports-analysis

# Install dependencies
pip install -r requirements.txt
```

### Running Locally

```bash
# Run the Streamlit app
streamlit run frontend/streamlit/app.py
```

The app will be available at `http://localhost:8501`

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository: `nikhil5hah/sports-analysis`
6. Main file path: `frontend/streamlit/app.py`
7. Click "Deploy!"

Your app will be live at `https://your-app-name.streamlit.app`

## Tech Stack

- **Backend**: Python, Pandas, NumPy
- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Custom modular framework

## Project Structure

```
sports-analysis/
├── frontend/streamlit/
│   └── app.py                 # Main Streamlit dashboard
├── core/
│   ├── metrics_framework.py  # Modular metrics system
│   └── modular_analysis.py   # Session analysis engine
├── data/
│   └── ingestion/
│       └── data_ingestion.py # GPX/FIT file processing
└── sports/squash/
    └── detectors/             # Sport-specific metric detectors
```

## Usage

1. Upload a GPX or FIT file from your fitness tracker
2. Select watch position and session type
3. View comprehensive session analysis
4. Explore detailed metrics and visualizations

## License

MIT License
