# Auto-Analytics Engine for Healthcare Performance Data

An automated system that ingests district-level healthcare data and generates insights about trends, outliers, and correlations without hardcoded logic.

## Project Status

**Phase 1: COMPLETED ✓**
- Data loading and validation
- CSV parsing with Pandas
- Schema validation
- Missing value detection
- Data filtering by district, month, and indicator

**Phase 2: COMPLETED ✓**
- Trend detection with percentage change calculation
- Configurable threshold (default 10%)
- Edge case handling (division by zero, missing data)
- Filtering by district and indicator
- Trend summary statistics

**Phase 3: COMPLETED ✓**
- Outlier detection using IQR method
- Outlier detection using Z-score method
- Configurable thresholds for both methods
- Method comparison functionality
- Edge case handling (std=0 for Z-score)

**Phase 4: COMPLETED ✓**
- Correlation detection using Pearson coefficient
- Full correlation matrix generation
- Configurable significance threshold (default 0.70)
- P-value calculation for statistical significance
- Strength classification (very_weak to very_strong)
- CSV export functionality
- Sample size validation warning

**Phase 5: COMPLETED ✓**
- Automated insight generation combining all detectors
- Dynamic natural language templates (NO hardcoded values)
- Data-driven severity classification (Low/Medium/High)
- Structured insight format with all required fields
- CSV export for insights
- Filtering by severity, type, and entity
- Comprehensive summary statistics

**Phase 6: COMPLETED ✓**
- Interactive Streamlit dashboard with light theme
- Configurable threshold sliders (trend, outlier, correlation)
- Live filters for district, month, and indicator
- Four visualization tabs:
  - Insights table grouped by severity
  - Charts (severity bar, type pie, trend lines)
  - Correlation heatmap with significant pairs
  - About/documentation page
- Metrics dashboard (total insights, high severity count)
- Professional styling with clean UI

## Project Structure

```
equilym_aiml/
├── .streamlit/
│   └── config.toml                # Streamlit configuration (light theme)
├── data/
│   └── healthcare_data.csv        # Sample healthcare performance data
├── src/
│   ├── data_loader.py            # Data loading and validation module
│   ├── trend_detector.py         # Trend detection module
│   ├── outlier_detector.py       # Outlier detection module (IQR & Z-score)
│   ├── correlation_detector.py   # Correlation detection module (Pearson)
│   └── insight_generator.py      # Automated insight generation engine
├── tests/
│   ├── test_phase1.py            # Phase 1 test suite
│   ├── test_phase2.py            # Phase 2 test suite
│   ├── test_phase3.py            # Phase 3 test suite
│   ├── test_phase4.py            # Phase 4 test suite
│   └── test_phase5.py            # Phase 5 test suite
├── outputs/                      # Generated insights and reports
│   ├── insights.csv              # Generated insights
│   └── correlation_matrix.csv    # Correlation matrix
├── app.py                        # Streamlit dashboard application
├── run_app.bat                   # Quick start script for Windows
├── requirements.txt              # Python dependencies
├── QUICKSTART.md                 # Quick start guide
└── README.md                     # This file
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- pandas==2.1.4
- numpy==1.26.2
- scipy==1.11.4
- plotly==5.18.0
- streamlit==1.29.0
- seaborn==0.13.0
- matplotlib==3.8.2

## Usage

### Phase 1: Data Loading and Validation

Run the test suite:
```bash
python src/test_phase1.py
```

Use the DataLoader class:
```python
from src.data_loader import DataLoader

# Load data
loader = DataLoader("data/healthcare_data.csv")
df = loader.load_data()

# Validate schema
is_valid, errors = loader.validate_schema()

# Get data summary
loader.print_data_summary()

# Filter data
ahmedabad_data = loader.get_filtered_data(district="Ahmedabad")
july_data = loader.get_filtered_data(month="2026-07-01")
anc_data = loader.get_filtered_data(indicator="anc_coverage")
```

### Phase 2: Trend Detection

Run the test suite:
```bash
python src/test_phase2.py
```

Use the TrendDetector class:
```python
from src.data_loader import DataLoader
from src.trend_detector import TrendDetector

# Load data
loader = DataLoader("data/healthcare_data.csv")
df = loader.load_data()

# Create trend detector with 10% threshold
detector = TrendDetector(df, threshold=10.0)

# Detect all trends
all_trends = detector.detect_trends()

# Get only significant trends
significant_trends = detector.get_significant_trends()

# Filter by district
ahmedabad_trends = detector.get_trends_by_district("Ahmedabad")

# Filter by indicator
anc_trends = detector.get_trends_by_indicator("anc_coverage")

### Phase 3: Outlier Detection

Run the test suite:
```bash
python src/test_phase3.py
```

Use the OutlierDetector class:
```python
from src.data_loader import DataLoader
from src.outlier_detector import OutlierDetector

# Load data
loader = DataLoader("data/healthcare_data.csv")
df = loader.load_data()

# Create outlier detector with IQR method
detector_iqr = OutlierDetector(df, method='IQR', threshold=1.5)
outliers = detector_iqr.detect_outliers()

# Create outlier detector with Z-score method
detector_zscore = OutlierDetector(df, method='zscore', threshold=3.0)
outliers_z = detector_zscore.detect_outliers()

# Filter by district
mehsana_outliers = detector_iqr.get_outliers_by_district('Mehsana')

# Compare methods
comparison = detector_iqr.compare_methods('anc_coverage')

# Get summary
summary = detector_iqr.summarize_outliers()
```

### Phase 4: Correlation Detection

Run the test suite:
```bash
python src/test_phase4.py
```

Use the CorrelationDetector class:
```python
from src.data_loader import DataLoader
from src.correlation_detector import CorrelationDetector

# Load data
loader = DataLoader("data/healthcare_data.csv")
df = loader.load_data()

# Create correlation detector
detector = CorrelationDetector(df, threshold=0.70)

# Get correlation matrix
corr_matrix = detector.calculate_correlation_matrix()

# Get all correlation pairs
pairs = detector.get_correlation_pairs()

# Get significant correlations only
significant = detector.get_significant_correlations()

# Analyze specific indicator
analysis = detector.analyze_indicator_relationships('anc_coverage')

# Export matrix
detector.export_correlation_matrix("outputs/correlation_matrix.csv")

# Get summary
summary = detector.summarize_correlations()
```

### Phase 5: Automated Insight Generation

Run the test suite:
```bash
python src/test_phase5.py
```

Use the InsightGenerator class:
```python
from src.data_loader import DataLoader
from src.insight_generator import InsightGenerator

# Load data
loader = DataLoader("data/healthcare_data.csv")
df = loader.load_data()

# Create insight generator
generator = InsightGenerator(
    df,
    trend_threshold=10.0,
    outlier_method='IQR',
    outlier_threshold=1.5,
    correlation_threshold=0.70
)

# Generate all insights
insights = generator.generate_all_insights()

# Filter by severity
high_severity = generator.get_insights_by_severity('High')

# Filter by type
trend_insights = generator.get_insights_by_type('trend')

# Filter by entity
mehsana_insights = generator.get_insights_by_entity('Mehsana')

# Export to CSV
generator.export_insights("outputs/insights.csv")

# Get summary
summary = generator.summarize_insights()
```

### Phase 6: Interactive UI

Run the Streamlit dashboard:

**Windows:**
```bash
run_app.bat
```

**Or manually:**
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

**Features:**
- **Sidebar Configuration**:
  - Adjust trend threshold (5-30%)
  - Select outlier method (IQR/Z-score) and threshold
  - Set correlation threshold (0.50-0.95)
  - Filter by district, month, indicator

- **Main Dashboard**:
  - Metrics overview (total insights, high severity, districts, periods)
  - Insights tab: Browse insights grouped by severity
  - Visualizations tab: Charts and trend lines
  - Correlations tab: Heatmap and significant pairs
  - About tab: Documentation and usage guide

- **Interactive Features**:
  - Real-time updates when thresholds change
  - Live filtering of insights
  - Expandable insight cards
  - Hover tooltips on charts

## Dataset

The healthcare performance dataset includes:
- **month**: Monthly timestamp
- **district**: District name
- **anc_coverage**: Antenatal care coverage (%)
- **institutional_delivery**: Institutional delivery rate (%)
- **immunization**: Immunization coverage (%)
- **high_risk_cases**: Count of high-risk cases

Sample size: 6 districts × 2 months = 12 records

## Features Implemented

### Phase 1 (Current)
- ✓ CSV loading with Pandas
- ✓ Schema validation
- ✓ Missing value detection and reporting
- ✓ Data type validation
- ✓ Filtering by district, month, and indicator
- ✓ Data summary generation with head(), info(), describe()

### Phase 2 (Current)
- ✓ Trend detection with configurable thresholds
- ✓ Percentage change calculation
- ✓ Significance flagging based on threshold
- ✓ Edge case handling (division by zero, missing data)
- ✓ Filter trends by district or indicator
- ✓ Trend summary statistics

### Phase 3 (Current)
- ✓ Outlier detection using IQR method
- ✓ Outlier detection using Z-score method
- ✓ Configurable thresholds (IQR multiplier, Z-score threshold)
- ✓ Method comparison and agreement analysis
- ✓ Filter outliers by district or indicator
- ✓ Edge case handling (std=0)

### Phase 4 (Current)
- ✓ Correlation detection using Pearson coefficient
- ✓ Full correlation matrix generation (4×4)
- ✓ Configurable significance threshold
- ✓ P-value calculation for statistical testing
- ✓ Strength classification (very_weak, weak, moderate, strong, very_strong)
- ✓ Filter correlations by indicator
- ✓ Export correlation matrix to CSV
- ✓ Sample size validation (warns if n < 30)

### Phase 5 (Current)
- ✓ Automated insight generation engine
- ✓ Combines trend, outlier, and correlation detections
- ✓ Dynamic natural language templates
- ✓ Data-driven severity classification
- ✓ Structured insights with all required fields:
  - insight_id, type, indicator, entity, period
  - value, prev_value, change_pct, metric
  - severity (Low/Medium/High), explanation
- ✓ CSV export functionality
- ✓ Filter insights by severity/type/entity
- ✓ Comprehensive summary statistics

### Phase 6 (Current)
- ✓ Interactive Streamlit dashboard
- ✓ Light theme with professional styling
- ✓ Configurable threshold sliders:
  - Trend threshold (5-30%)
  - Outlier method (IQR/Z-score) with threshold
  - Correlation threshold (0.50-0.95)
- ✓ Live filters (district, month, indicator)
- ✓ Metrics dashboard (4 key metrics)
- ✓ Four tabs:
  - Insights: Grouped by severity with expandable cards
  - Visualizations: Bar chart, pie chart, line charts
  - Correlations: Heatmap + significant pairs list
  - About: Documentation and usage guide
- ✓ Real-time updates on threshold/filter changes
- Outlier detection using IQR and Z-score methods
- Configurable outlier thresholds

### Phase 4 (Planned)
- Correlation detection using Pearson coefficient
- Correlation matrix generation

### Phase 5 (Planned)
- Automated insight generation with dynamic templates
- Severity classification (Low/Medium/High)
- Natural language explanations

### Phase 6 (Planned)
- Interactive UI with Streamlit
- Visualizations (line charts, bar charts, heatmaps)
- Configurable threshold sliders

## Test Results

All test suites are located in the `tests/` folder. Run them individually or all at once.

**Run all tests:**
```bash
run_all_tests.bat
```

**Run individual phases:**
```bash
python tests/test_phase1.py
python tests/test_phase2.py
python tests/test_phase3.py
python tests/test_phase4.py
python tests/test_phase5.py
```

**Phase 1 tests: ALL PASSED ✓**

```
[TEST 1] Data loading: ✓
[TEST 2] Schema validation: ✓
[TEST 3] Required columns: ✓
[TEST 4] Missing values: ✓ (0 missing)
[TEST 5] Data summary: ✓
[TEST 6] Filter functions: ✓
[TEST 7] District filter: ✓
[TEST 8] Month filter: ✓
[TEST 9] Indicator filter: ✓
[TEST 10] Data types: ✓
```

**Phase 2 tests: ALL PASSED ✓**

```
[TEST 1] Trend detector initialization: ✓
[TEST 2] Percentage change calculation: ✓
[TEST 3] Edge case handling: ✓
[TEST 4] Trend detection (24 trends): ✓
[TEST 5] Significant trend filtering (6 significant): ✓
[TEST 6] Known trend verification: ✓
  - Ahmedabad ANC: -18.82% ✓
  - Mehsana high_risk_cases: +154.55% ✓
[TEST 7] District filtering: ✓
[TEST 8] Indicator filtering: ✓
[TEST 9] Configurable threshold: ✓
[TEST 10] Summary generation: ✓
```

**Key Findings from Sample Data:**
- Total trends detected: 24 (6 districts × 4 indicators)
- Significant trends (>10% change): 6
- Largest increase: Mehsana high_risk_cases (+154.55%)
- Largest decrease: Mehsana anc_coverage (-50.0%)

**Phase 3 tests: ALL PASSED ✓**

```
[TEST 1] IQR detector initialization: ✓
[TEST 2] Z-score detector initialization: ✓
[TEST 3] IQR detection for single indicator: ✓
[TEST 4] Z-score detection for single indicator: ✓
[TEST 5] Detect all outliers (4 with IQR): ✓
[TEST 6] Known outlier verification: ✓
  - Mehsana ANC (42): ✓
  - Mehsana high_risk_cases (28): ✓
[TEST 7] District filtering: ✓
[TEST 8] Indicator filtering: ✓
[TEST 9] Configurable thresholds: ✓
  - Loose (1.0): 8 outliers
  - Default (1.5): 4 outliers
  - Strict (2.0): 2 outliers
[TEST 10] Method comparison: ✓
[TEST 11] Summary generation: ✓
[TEST 12] Edge case (std=0): ✓
[TEST 13] IQR vs Z-score sensitivity: ✓
```

**Key Findings:**
- IQR method (threshold 1.5): 4 outliers
- Z-score method (threshold 3.0): 0 outliers
- Z-score method (threshold 2.0): 2 outliers
- Most extreme outlier: Mehsana ANC coverage = 42
- IQR is more sensitive with small sample sizes (12 records)

**Phase 4 tests: ALL PASSED ✓**

```
[TEST 1] Correlation detector initialization: ✓
[TEST 2] Correlation matrix calculation: ✓
  - Matrix shape (4×4): ✓
  - Diagonal = 1.0: ✓
  - Symmetric: ✓
[TEST 3] All correlation pairs (6 pairs): ✓
[TEST 4] Correlation calculation verification: ✓
[TEST 5] Strength classification: ✓
[TEST 6] Significant correlation filtering: ✓
[TEST 7] Known correlation verification: ✓
  - institutional_delivery <-> immunization: r=0.979 ✓
  - anc_coverage <-> high_risk_cases: r=-0.933 ✓
[TEST 8] Indicator filtering: ✓
[TEST 9] Strongest/weakest finding: ✓
[TEST 10] Configurable thresholds: ✓
[TEST 11] Summary generation: ✓
[TEST 12] Indicator relationship analysis: ✓
[TEST 13] CSV export: ✓
[TEST 14] Sample size warning: ✓
[TEST 15] P-value calculation: ✓
```

**Key Findings:**
- Total correlation pairs: 6 (from 4 indicators)
- Significant correlations (|r| ≥ 0.70): 2
  - **institutional_delivery <-> immunization**: r = 0.979 (very strong positive)
  - **anc_coverage <-> high_risk_cases**: r = -0.933 (very strong negative)
- Sample size limitation: Only 12 records (recommended: n ≥ 30)
- Both significant correlations have p < 0.0001

**Phase 5 tests: ALL PASSED ✓**

```
[TEST 1] Insight generator initialization: ✓
[TEST 2] Generated 12 insights: ✓
[TEST 3] All required columns present: ✓
[TEST 4] All insight IDs unique: ✓
[TEST 5] Valid insight types (trend, outlier, correlation): ✓
[TEST 6] Valid severity levels (Low, Medium, High): ✓
[TEST 7] No hardcoded values (data-driven): ✓
[TEST 8] Trend insights: 6 generated ✓
[TEST 9] Outlier insights: 4 generated ✓
[TEST 10] Correlation insights: 2 generated ✓
[TEST 11] Severity classification: ✓
[TEST 12] Severity filtering: ✓
[TEST 13] Type filtering: ✓
[TEST 14] Entity filtering: ✓
[TEST 15] CSV export: ✓
[TEST 16] Summary generation: ✓
[TEST 17] Natural language quality: ✓
[TEST 18] No duplicate insights: ✓
```

**Insights Generated:**
- **Total**: 12 insights
- **By Type**: 6 trends, 4 outliers, 2 correlations
- **By Severity**: 6 High, 6 Low
- **High Severity Examples**:
  - "Anc Coverage in Mehsana dropped by 50.0% compared to the previous month"
  - "High Risk Cases in Mehsana increased by 154.6% compared to the previous month"
  - "Mehsana's Anc Coverage of 42 is 46.4% below the state mean (78.3)"

**Key Validation Points:**
- ✓ All insights are DATA-DRIVEN (no hardcoded district names or values)
- ✓ Severity calculated using data-driven rules (multiples of threshold)
- ✓ Natural language generated dynamically from templates
- ✓ All required fields present and properly formatted
- ✓ Ready for UI consumption

## Assignment Requirements

This project is built for the **Automated Insight Generation** assignment with focus on:
1. General-purpose analytics (no hardcoded district-specific logic)
2. Data-driven insights using templates with dynamic values
3. Configurable thresholds for all detection methods
4. Statistical methods: trend analysis, outlier detection, correlation analysis
5. Clean, modular code architecture

## Next Steps

1. ~~Implement trend detector (Phase 2)~~ ✓ DONE
2. ~~Implement outlier detector (Phase 3)~~ ✓ DONE
3. ~~Implement correlation analyzer (Phase 4)~~ ✓ DONE
4. ~~Build insight generator (Phase 5)~~ ✓ DONE
5. ~~Create UI with visualizations (Phase 6)~~ ✓ DONE

## 🎉 Project Complete!

All phases of the Auto-Analytics Engine are complete and fully functional.

## License

Educational project for placement assignment.
