# Test Suite Documentation

This folder contains all test files for the Auto-Analytics Engine project.

## Test Files

### test_phase1.py - Data Loading & Validation
**Tests: 10**

Validates the data loading module:
- CSV file loading
- Schema validation
- Missing value detection
- Data type verification
- Filter functions (district, month, indicator)
- Data summary generation

**Run:**
```bash
python tests/test_phase1.py
```

---

### test_phase2.py - Trend Detection
**Tests: 10**

Validates trend detection functionality:
- Percentage change calculation
- Edge cases (division by zero, missing data)
- Trend detection across all districts
- Significant trend filtering
- Known trend verification
- District and indicator filtering
- Configurable thresholds
- Summary generation

**Run:**
```bash
python tests/test_phase2.py
```

**Key Validations:**
- Ahmedabad ANC: -18.82% change
- Mehsana high_risk_cases: +154.55% change

---

### test_phase3.py - Outlier Detection
**Tests: 13**

Validates outlier detection using IQR and Z-score methods:
- IQR method initialization
- Z-score method initialization
- IQR calculation for single indicator
- Z-score calculation for single indicator
- Outlier detection across all indicators
- Known outlier verification
- District and indicator filtering
- Configurable thresholds
- Method comparison
- Summary generation
- Edge case (std=0)

**Run:**
```bash
python tests/test_phase3.py
```

**Key Validations:**
- Mehsana ANC coverage (42): outlier
- Mehsana high_risk_cases (28): outlier
- IQR more sensitive than Z-score for small samples

---

### test_phase4.py - Correlation Analysis
**Tests: 15**

Validates correlation detection:
- Correlation matrix generation
- Matrix properties (symmetry, diagonal=1)
- Correlation pair extraction
- Pearson coefficient calculation
- Strength classification
- Significant correlation filtering
- Known correlation verification
- Indicator filtering
- Strongest/weakest correlation finding
- Configurable thresholds
- Summary generation
- CSV export
- Sample size warning
- P-value calculation

**Run:**
```bash
python tests/test_phase4.py
```

**Key Validations:**
- institutional_delivery ↔ immunization: r=0.979 (very strong positive)
- anc_coverage ↔ high_risk_cases: r=-0.933 (very strong negative)

---

### test_phase5.py - Automated Insight Generation
**Tests: 18**

Validates the complete insight generation system:
- Insight generator initialization
- Total insight generation
- Required column verification
- Insight ID uniqueness
- Valid insight types
- Valid severity levels
- No hardcoded values verification
- Trend insight generation
- Outlier insight generation
- Correlation insight generation
- Severity classification
- Filtering by severity, type, and entity
- CSV export
- Summary generation
- Natural language quality
- Duplicate detection

**Run:**
```bash
python tests/test_phase5.py
```

**Key Validations:**
- 12 insights generated (6 trends, 4 outliers, 2 correlations)
- 6 High severity, 6 Low severity
- All insights data-driven (no hardcoded values)
- Natural language explanations generated dynamically

---

## Running All Tests

To run all test suites at once:

**Windows:**
```bash
run_all_tests.bat
```

**Manual:**
```bash
python tests/test_phase1.py
python tests/test_phase2.py
python tests/test_phase3.py
python tests/test_phase4.py
python tests/test_phase5.py
```

---

## Test Results Summary

All 66 tests should pass:
- Phase 1: 10/10 ✓
- Phase 2: 10/10 ✓
- Phase 3: 13/13 ✓
- Phase 4: 15/15 ✓
- Phase 5: 18/18 ✓

**Total: 66/66 tests passing**

---

## Understanding Test Output

### Success Indicators
- ✓ Green checkmarks indicate passed tests
- Test names describe what is being validated
- Expected vs actual values shown for verification

### Failure Indicators
- ✗ Red X marks indicate failed tests
- Error messages explain what went wrong
- Tests stop on first failure for clarity

### Warnings
- ⚠ Yellow warnings indicate potential issues that aren't failures
- Common warnings: small sample size, unstable correlations

---

## Test Coverage

The test suite validates:
- **Data Loading**: File I/O, validation, filtering
- **Statistical Methods**: Percentage change, IQR, Z-score, Pearson correlation
- **Edge Cases**: Division by zero, missing data, identical values
- **Configuration**: All thresholds are adjustable
- **Output Quality**: Structured format, natural language, no hardcoded values
- **Integration**: All components work together

---

## Adding New Tests

When adding features, create tests that verify:
1. **Functionality**: Does it work as expected?
2. **Edge Cases**: How does it handle unusual inputs?
3. **Integration**: Does it work with other components?
4. **Output Quality**: Is the output correct and well-formatted?

Follow the existing test structure:
```python
def test_feature():
    print("\n[TEST X] Testing feature...")
    # Setup
    # Execute
    # Verify
    # Report
```

---

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError`, the path setup is incorrect.
All tests use `sys.path.append('.')` to add the project root.
Ensure you run tests from the project root directory.

### Data File Not Found
Tests expect `data/healthcare_data.csv` to exist.
Run tests from the project root, not from the tests folder.

### Different Results
If test results differ from expected:
1. Check if the data file has changed
2. Verify Python version (3.8+)
3. Ensure all dependencies are installed
4. Check for data corruption

---

## Test Maintenance

Tests should be:
- **Fast**: Complete in seconds
- **Isolated**: Don't depend on each other
- **Deterministic**: Same input = same output
- **Clear**: Easy to understand what failed

Update tests when:
- Adding new features
- Changing calculation methods
- Modifying data structures
- Fixing bugs

---

## For Interviews

Be prepared to explain:
1. Why each test is important
2. What edge cases are covered
3. How tests verify "no hardcoded values"
4. Why certain thresholds are used
5. How tests ensure data-driven insights

Key talking points:
- 100% test pass rate
- Comprehensive coverage (66 tests)
- Edge case handling
- Statistical method validation
- Integration testing
