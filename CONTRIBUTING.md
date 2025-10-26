# Contributing to Sports Performance Analysis Platform

## 🎯 Project Goals

This project aims to build a comprehensive sports performance analysis platform that:
- Starts with squash analysis
- Extends to tennis, badminton, table tennis, and padel
- Provides AI-driven insights from historical data
- Integrates with smart fitness trackers
- Follows a modular, extensible architecture

## 🏗️ Architecture Overview

### Core Principles
1. **Modularity**: Each sport and metric is an independent module
2. **Consistency**: Unified framework across all sports
3. **Extensibility**: Easy to add new sports or metrics
4. **Data-Driven**: All insights based on actual sensor data

### Current Structure
```
sports-analysis/
├── core/                          # Framework files
│   ├── metrics_framework.py       # Base framework
│   └── modular_analysis.py       # Analysis orchestrator
│
├── sports/
│   └── squash/                    # Squash-specific modules
│       └── (to be expanded)
│
├── data/
│   ├── ingestion.py              # Data import
│   └── (processing modules)
│
└── app.py                         # Streamlit interface
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- pip
- Git

### Installation
```bash
git clone https://github.com/your-username/sports-analysis.git
cd sports-analysis
pip install -r requirements.txt
```

### Running the App
```bash
streamlit run app.py
```

## 📝 How to Contribute

### Adding a New Sport

1. **Create sport directory**
   ```bash
   mkdir -p sports/{sport_name}/detectors
   ```

2. **Create base detector** (use squash as template)
   ```python
   # sports/{sport_name}/detectors/rallies.py
   from core.metrics_framework import BaseMetricDetector
   
   class {Sport}RallyDetector(BaseMetricDetector):
       def __init__(self):
           super().__init__("number_of_rallies", MetricType.COUNT)
       
       def detect(self, df, context=None):
           # Your detection logic
           pass
   ```

3. **Register detector**
   ```python
   # In modular_analysis.py
   from sports.{sport_name}.detectors import {Sport}RallyDetector
   
   framework.register_detector({Sport}RallyDetector())
   ```

### Adding a New Metric

1. **Create detector class** inheriting from `BaseMetricDetector`

2. **Implement required methods:**
   ```python
   def get_required_data_fields(self):
       return ['heart_rate', 'timestamp']
   
   def detect(self, df, context=None):
       # Detection logic
       pass
   ```

3. **Add confidence scoring:**
   ```python
   def get_confidence_score(self, df, result):
       # Calculate confidence 0.0-1.0
       return confidence
   ```

### Improving Existing Algorithms

1. **Increment algorithm version**
   ```python
   self.algorithm_version = "1.2"
   ```

2. **Update detection logic**
   - Test with sample data
   - Validate with real user data
   - Document changes

3. **Update tests**
   - Add unit tests
   - Verify accuracy improvements
   - Check performance impact

## 🧪 Testing

### Running Tests
```bash
# Unit tests
python3 -m pytest tests/unit/

# Integration tests
python3 -m pytest tests/integration/

# All tests
python3 test_mvp.py
```

### Test Data
- Use `sample_squash_session.gpx` for testing
- Create sport-specific sample data
- Document test scenarios

## 📊 Data Requirements

### Minimum Data Fields
- `timestamp` - Required for all sports
- `heart_rate` - Required for most metrics

### Optional Data Fields (Improves Accuracy)
- `cadence` - Better movement detection
- `speed` - Court movement analysis
- `accelerometer_x/y/z` - Shot detection
- `gyroscope_x/y/z` - Rotation patterns

## 🎯 Coding Standards

### Python Style
- Follow PEP 8
- Use type hints
- Document all functions
- Keep functions focused (< 50 lines)

### Naming Conventions
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Documentation
- Docstrings for all functions/classes
- Inline comments for complex logic
- Update README for user-facing changes

## 🔄 Workflow

### Feature Development
1. Create feature branch: `git checkout -b feature/{sport-or-metric}`
2. Make changes
3. Add tests
4. Run tests
5. Submit pull request

### Bug Fixes
1. Create bug fix branch: `git checkout -b fix/{issue-number}`
2. Fix the issue
3. Add regression test
4. Submit pull request

### Pull Request Process
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📋 Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] README updated (if needed)
- [ ] All tests passing
- [ ] No linting errors
- [ ] Backward compatibility maintained

## 🤝 Areas for Contribution

### High Priority
- [ ] Tennis detection algorithms
- [ ] Badminton detection algorithms
- [ ] Table tennis detection algorithms
- [ ] Padel detection algorithms
- [ ] Algorithm accuracy improvements

### Medium Priority
- [ ] Mobile app development
- [ ] Web dashboard
- [ ] API development
- [ ] Historical analysis features
- [ ] Export functionality

### Nice to Have
- [ ] Additional sports support
- [ ] Enhanced visualizations
- [ ] Social features
- [ ] Coach dashboards
- [ ] Team analytics

## 💡 Getting Help

- Open an issue for bugs
- Start a discussion for features
- Check existing issues before creating new ones
- Provide detailed error messages and stack traces

## 📜 License

This project is licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md
- Project documentation
- Release notes

