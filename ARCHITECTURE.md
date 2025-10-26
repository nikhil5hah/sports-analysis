# Architecture Documentation

## 🏛️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User Layer                            │
├─────────────┬───────────────┬──────────────────────────┤
│  Streamlit  │  Mobile App   │   Web Dashboard          │
│  (Current)  │  (Future)    │   (Future)                │
└──────┬──────┴──────┬────────┴────────┬─────────────────┘
       │             │                  │
       └─────────────┼──────────────────┘
                     │
         ┌───────────▼────────────┐
         │   Analysis Engine      │
         │   (Modular Framework)  │
         └───────────┬────────────┘
                     │
         ┌───────────┼────────────┐
         │           │            │
    ┌────▼────┐ ┌───▼────┐ ┌────▼──────┐
    │ Sport   │ │ Metric │ │   AI      │
    │ Modules │ │Dectors │ │  Models   │
    └────┬────┘ └───┬────┘ └────┬──────┘
         │          │           │
         └──────────┼───────────┘
                    │
         ┌──────────▼────────────┐
         │   Data Layer          │
         │  (Ingestion & Storage) │
         └───────────┬────────────┘
                     │
         ┌───────────┼────────────┐
         │           │            │
    ┌────▼────┐ ┌───▼────┐ ┌───▼─────┐
    │  FIT    │ │  GPX   │ │  APIs   │
    │  Files  │ │ Files  │ │  (Future)│
    └─────────┘ └────────┘ └─────────┘
```

## 🧱 Component Layers

### 1. User Interface Layer
**Purpose**: Present insights and collect user inputs

**Current Implementation**:
- Streamlit web app
- Simple, functional interface
- Session upload and analysis display

**Future Implementations**:
- Native iOS/Android apps
- Advanced web dashboard
- Real-time analysis during sessions

### 2. Analysis Engine
**Purpose**: Orchestrate analysis across sports and metrics

**Components**:
- `ModularAnalysisEngine`: Main orchestrator
- `MetricsFramework`: Detector management
- `BaseMetricDetector`: Abstract base class

**Key Features**:
- Automatic metric registration
- Confidence scoring
- Data quality assessment
- Context-aware analysis (hand position, session type)

### 3. Sport Modules
**Purpose**: Sport-specific detection algorithms

**Structure**:
```
sports/
├── squash/
│   ├── detectors/
│   │   ├── warmup.py
│   │   ├── rallies.py
│   │   ├── games.py
│   │   └── cooldown.py
│   ├── metrics.py
│   └── algorithms.py
└── tennis/
    └── (similar structure)
```

**Key Principles**:
- Each sport is independent
- Consistent interface across sports
- Reusable components where possible

### 4. Metric Detectors
**Purpose**: Individual metric detection algorithms

**Base Interface**:
```python
class BaseMetricDetector:
    def __init__(self, metric_name, metric_type)
    def detect(self, df, context=None) -> MetricResult
    def get_required_data_fields(self) -> List[str]
    def get_optional_data_fields(self) -> List[str]
    def validate_data(self, df) -> bool
    def get_confidence_score(self, df, result) -> float
```

**Metric Types**:
- `TEMPORAL`: Time-based (warm-up, cool-down)
- `COUNT`: Integer counts (rallies, games)
- `INTENSITY`: High/low intensity measures
- `MOVEMENT`: Physical activity patterns
- `COMPOSITE`: Multiple data sources

### 5. Data Layer
**Purpose**: Import, process, and store sensor data

**Components**:
- `FitnessDataImporter`: GPX/FIT parsing
- `Preprocessor`: Data cleaning and interpolation
- `SessionStorage`: Database operations
- `TrackerAdapter`: API integrations

**Data Sources**:
- FIT files (Garmin, Pixel Watch, etc.)
- GPX files (Strava exports)
- Future: Direct tracker APIs

### 6. AI/ML Layer (Future)
**Purpose**: Historical analysis and predictive insights

**Components**:
- Pattern recognition models
- Predictive analytics
- Personalized recommendations
- Training load analysis

## 🔄 Data Flow

### Session Analysis Flow

```
1. User Uploads File
   │
   ▼
2. Data Ingestion
   ├─ Parse GPX/FIT
   ├─ Extract all available fields
   └─ Preprocess data
   │
   ▼
3. Context Setup
   ├─ Hand position
   ├─ Session type (training/match)
   └─ Sport type
   │
   ▼
4. Metric Detection
   ├─ Register all detectors
   ├─ Validate data availability
   ├─ Run detection algorithms
   └─ Calculate confidence scores
   │
   ▼
5. Analysis Aggregation
   ├─ Combine metric results
   ├─ Assess data quality
   ├─ Generate recommendations
   └─ Build session summary
   │
   ▼
6. Results Presentation
   ├─ Display metrics
   ├─ Visualizations
   ├─ Insights and recommendations
   └─ Export options
```

## 🎯 Design Patterns

### 1. Strategy Pattern
**Used in**: Metric detection algorithms
**Purpose**: Switch algorithms dynamically based on context

```python
# Different algorithms for playing vs non-playing hand
if hand_position == 'playing_hand':
    use_playing_hand_algorithm()
else:
    use_non_playing_hand_algorithm()
```

### 2. Factory Pattern
**Used in**: Detector creation
**Purpose**: Create appropriate detectors based on sport/context

```python
def create_detector(sport_type, metric_name):
    return detectors[sport_type][metric_name]()
```

### 3. Observer Pattern
**Used in**: Real-time analysis (future)
**Purpose**: Notify views when new data arrives

### 4. Template Method Pattern
**Used in**: BaseMetricDetector
**Purpose**: Define algorithm structure, allow subclasses to customize

## 🗄️ Data Models

### Session Model
```python
{
    'session_id': str,
    'user_id': str,
    'sport': str,
    'session_type': str,  # training/match
    'hand_position': str,
    'timestamp': datetime,
    'duration_minutes': float,
    'metrics': Dict[str, MetricResult],
    'data_quality': Dict,
    'recommendations': List[str]
}
```

### MetricResult Model
```python
{
    'metric_name': str,
    'value': Any,
    'confidence': float,  # 0.0-1.0
    'metadata': Dict[str, Any],
    'data_points': List[Tuple[int, int]],
    'algorithm_version': str
}
```

### Historical Analysis Model
```python
{
    'user_id': str,
    'sport': str,
    'sessions': List[Session],
    'trends': Dict,
    'insights': List[str],
    'benchmarks': Dict
}
```

## 🔐 Security & Privacy

### Data Security
- Local storage by default
- Encrypted data transmission
- No cloud upload without explicit consent
- Secure deletion options

### Privacy Considerations
- Minimal data collection
- User controls what's stored
- Export own data anytime
- Delete all data option

## ⚡ Performance Optimization

### Current Optimizations
- Streaming data processing
- Lazy loading of visualizations
- Caching of intermediate results
- Efficient data structures

### Future Optimizations
- Database indexing
- Query optimization
- CDN for static assets
- Edge computing for analysis

## 🔧 Configuration

### Environment Variables
```bash
DATA_DIR=/path/to/data
STORAGE_TYPE=sqlite  # or postgresql, mongodb
API_ENABLED=false
```

### Configuration Files
- `config.yaml`: General settings
- `sport_configs/`: Sport-specific settings
- `algorithm_configs/`: Algorithm parameters

## 📊 Monitoring & Analytics

### Metrics to Track
- Analysis accuracy
- Processing time
- User engagement
- Error rates
- Data quality scores

### Logging
- Structured logging with levels
- Error tracking and reporting
- Performance monitoring
- User analytics (anonymous)

## 🧪 Testing Strategy

### Unit Tests
- Individual detector testing
- Algorithm validation
- Data processing testing

### Integration Tests
- End-to-end analysis flows
- Multi-sport testing
- API endpoint testing

### Performance Tests
- Large dataset handling
- Concurrent analysis
- Memory usage testing

## 🚀 Deployment

### Current: Local Only
- Python environment
- Streamlit server
- Local storage

### Future: Cloud Deployment
- Containerized services
- Load balancing
- Auto-scaling
- Multi-region support

## 📈 Scalability Considerations

### Horizontal Scaling
- Stateless analysis workers
- Queue-based processing
- Distributed storage

### Caching Strategy
- Session results caching
- Algorithm result caching
- Historical analysis caching

### Database Scaling
- Read replicas
- Sharding by user_id
- Archival strategy

## 🔄 Version Control

### Algorithm Versioning
- Each detector tracks version
- A/B testing support
- Rollback capability

### Data Versioning
- Schema migrations
- Backward compatibility
- Data upgrade scripts

## 🎓 Learning Resources

### For Contributors
- Algorithm research papers
- Sport-specific knowledge bases
- Data science best practices
- Testing methodologies

### For Users
- User guides
- Video tutorials
- Best practices
- FAQ

