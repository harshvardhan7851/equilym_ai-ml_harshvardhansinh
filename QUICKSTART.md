# Quick Start Guide

## Auto-Analytics Engine for Healthcare Performance

This guide will help you get the application running in minutes.

---

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- pandas (data manipulation)
- numpy (numerical operations)
- scipy (statistical functions)
- plotly (interactive charts)
- streamlit (web dashboard)
- seaborn (statistical visualization)
- matplotlib (plotting)

---

## Running the Application

### Option 1: Use the Quick Start Script (Windows)

```bash
run_app.bat
```

### Option 2: Manual Start

```bash
streamlit run app.py
```

The dashboard will automatically open in your browser at:
**http://localhost:8501**

---

## Testing Individual Phases

You can test each phase independently:

```bash
# Phase 1: Data Loading
python tests/test_phase1.py

# Phase 2: Trend Detection
python tests/test_phase2.py

# Phase 3: Outlier Detection
python tests/test_phase3.py

# Phase 4: Correlation Analysis
python tests/test_phase4.py

# Phase 5: Insight Generation
python tests/test_phase5.py
```

All tests should pass with ✓ marks.

---

## Using the Dashboard

### 1. Configure Detection Thresholds (Sidebar)

**Trend Threshold**: Controls sensitivity for detecting significant changes
- Lower values (5-10%): Detect more trends, including minor changes
- Higher values (15-30%): Only detect major changes

**Outlier Method**:
- **IQR**: More robust, recommended for small datasets
- **Z-score**: More sensitive, better for larger datasets

**Correlation Threshold**: Minimum strength to flag relationships
- 0.50: Moderate correlations
- 0.70: Strong correlations (default)
- 0.90: Very strong correlations only

### 2. Apply Filters

Use the filter dropdowns to focus on:
- Specific districts
- Particular months
- Individual indicators

Filters update the insights table and visualizations in real-time.

### 3. Explore the Tabs

**📋 Insights Tab**:
- View all generated insights
- Grouped by severity (High/Medium/Low)
- Expand cards for full details
- Filter by severity and type

**📈 Visualizations Tab**:
- Bar chart: Insights by severity
- Pie chart: Insights by type
- Line charts: Indicator trends over time

**🔗 Correlations Tab**:
- Heatmap showing all correlations
- List of significant correlations
- Statistical significance (p-values)

**ℹ️ About Tab**:
- Application documentation
- How to interpret insights
- Severity classification rules

---

## Understanding the Output

### Insight Types

1. **Trend**: Significant change between time periods
   - Example: "ANC Coverage in Ahmedabad dropped by 18.8%"

2. **Outlier**: Unusual value compared to other districts
   - Example: "Mehsana's ANC coverage of 42 is 46.4% below the state mean"

3. **Correlation**: Relationship between two indicators
   - Example: "Strong negative correlation between ANC Coverage and High Risk Cases"

### Severity Levels

- **High** (Red): Requires immediate attention (>3× threshold)
- **Medium** (Yellow): Noteworthy (>2× threshold)
- **Low** (Green): Minor but flagged (>1× threshold)

---

## Sample Insights from Demo Data

With default settings, you should see:

**High Severity Insights:**
- Mehsana ANC Coverage dropped 50%
- Mehsana High Risk Cases increased 154.6%
- Strong correlations detected

**Total Insights:** ~12 insights
- 6 Trends
- 4 Outliers
- 2 Correlations

---

## Customizing for Your Data

### Adding Your Own Data

1. Replace `data/healthcare_data.csv` with your data
2. Ensure your CSV has these columns:
   - `month` (YYYY-MM-DD format)
   - `district` (text)
   - Indicator columns (numeric)

3. Update `src/data_loader.py` if you have different indicators:
   ```python
   self.indicators = ['your_indicator1', 'your_indicator2', ...]
   ```

4. Restart the application

### Adjusting Detection Rules

Edit the default thresholds in `app.py`:
```python
# Line ~48-65
trend_threshold = st.sidebar.slider(
    "Trend Threshold (%)",
    min_value=5.0,
    max_value=30.0,
    value=10.0,  # Change this default
    step=1.0
)
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "FileNotFoundError: data/healthcare_data.csv"
**Solution**: Ensure you're running from the project root directory

### Issue: Port 8501 already in use
**Solution**: Stop other Streamlit apps or use a different port
```bash
streamlit run app.py --server.port 8502
```

### Issue: Charts not displaying
**Solution**: Clear Streamlit cache
- Press 'C' in the dashboard
- Or restart the application

---

## Performance Notes

- **Sample Size**: The demo has 12 records (6 districts × 2 months)
- **Recommended**: 30+ records for stable correlations
- **Warning**: With small samples, correlations may be unstable
- **Caching**: Results are cached for better performance

---

## Export Options

### Export Insights to CSV

The insights are automatically exported to:
```
outputs/insights.csv
```

Contains all fields:
- insight_id, type, indicator, entity, period
- value, prev_value, change_pct, metric
- severity, explanation

### Export Correlation Matrix

Available at:
```
outputs/correlation_matrix.csv
```

Standard correlation matrix format compatible with Excel.

---

## Interview Preparation

### Key Points to Explain

1. **No Hardcoded Logic**:
   - All insights are generated dynamically
   - Templates use data-driven values
   - Works with any district/indicator names

2. **Configurable Thresholds**:
   - All detection rules are adjustable
   - Users can control sensitivity
   - No magic numbers in the code

3. **Statistical Methods**:
   - Percentage change for trends
   - IQR and Z-score for outliers
   - Pearson correlation with p-values

4. **Sample Size Limitation**:
   - Acknowledge the 12-record sample
   - Explain why correlations may be unstable
   - Show awareness of statistical requirements

5. **Architecture**:
   - Modular design (each detector is independent)
   - Data layer → Analysis → Insights → UI
   - Easy to extend with new detectors

---

## Getting Help

If you encounter issues:
1. Check that all tests pass (`python src/test_phase*.py`)
2. Verify data file exists and is properly formatted
3. Ensure Python 3.8+ is installed
4. Check console output for error messages

---

Good luck with your placement interview! 🎯
