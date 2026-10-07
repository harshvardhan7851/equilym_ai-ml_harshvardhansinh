"""
Phase 2 Test Script
Tests trend detection functionality
"""

import sys
sys.path.append('.')
from src.data_loader import DataLoader
from src.trend_detector import TrendDetector


def test_phase2():
    """Run all Phase 2 tests"""
    print("\n" + "=" * 70)
    print("PHASE 2 TEST: TREND DETECTION")
    print("=" * 70)
    
    # Load data
    print("\n[SETUP] Loading data...")
    try:
        loader = DataLoader("data/healthcare_data.csv")
        df = loader.load_data()
        print(f"✓ Loaded {len(df)} records")
    except Exception as e:
        print(f"✗ Failed to load data: {e}")
        return False
    
    # Test 1: Initialize trend detector
    print("\n[TEST 1] Initializing trend detector with default threshold (10%)...")
    try:
        detector = TrendDetector(df, threshold=10.0)
        print(f"✓ Trend detector initialized")
        print(f"  Threshold: {detector.threshold}%")
        print(f"  Indicators tracked: {detector.indicators}")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False
    
    # Test 2: Percentage change calculation
    print("\n[TEST 2] Testing percentage change calculation...")
    test_cases = [
        (85, 69, -18.82),  # Ahmedabad ANC: decrease
        (11, 28, 154.55),  # Mehsana high_risk: increase
        (90, 90, 0.0),     # No change
    ]
    
    for prev, curr, expected in test_cases:
        result = detector.calculate_percentage_change(curr, prev)
        if result is not None and abs(result - expected) < 0.1:
            print(f"✓ {prev} → {curr} = {result}% (expected {expected}%)")
        else:
            print(f"✗ {prev} → {curr} = {result}% (expected {expected}%)")
            return False
    
    # Test 3: Edge case - division by zero
    print("\n[TEST 3] Testing edge cases...")
    result_zero = detector.calculate_percentage_change(10, 0)
    if result_zero is None:
        print("✓ Division by zero handled correctly (returns None)")
    else:
        print(f"✗ Division by zero not handled correctly: {result_zero}")
        return False
    
    # Test 4: Edge case - missing data
    import pandas as pd
    result_nan = detector.calculate_percentage_change(pd.NA, 10)
    if result_nan is None:
        print("✓ Missing data handled correctly (returns None)")
    else:
        print(f"✗ Missing data not handled correctly: {result_nan}")
        return False
    
    # Test 5: Detect all trends
    print("\n[TEST 4] Detecting trends across all districts...")
    all_trends = detector.detect_trends()
    expected_trend_count = 24  # 6 districts × 4 indicators × 1 comparison
    
    if len(all_trends) == expected_trend_count:
        print(f"✓ Detected {len(all_trends)} trends (expected {expected_trend_count})")
    else:
        print(f"✗ Detected {len(all_trends)} trends (expected {expected_trend_count})")
        return False
    
    # Verify required columns
    required_cols = ['district', 'indicator', 'period', 'current_value', 
                     'previous_value', 'change_pct', 'is_significant']
    if all(col in all_trends.columns for col in required_cols):
        print(f"✓ All required columns present: {required_cols}")
    else:
        print(f"✗ Missing columns")
        return False
    
    # Test 6: Significant trends filtering
    print("\n[TEST 5] Filtering significant trends (|change| >= 10%)...")
    significant = detector.get_significant_trends()
    expected_significant = 6  # Based on sample data
    
    if len(significant) == expected_significant:
        print(f"✓ Found {len(significant)} significant trends (expected {expected_significant})")
    else:
        print(f"⚠ Found {len(significant)} significant trends (expected ~{expected_significant})")
    
    # Verify all are truly significant
    all_significant = all(significant['is_significant'] == True)
    if all_significant:
        print("✓ All filtered trends are marked as significant")
    else:
        print("✗ Some filtered trends are not marked as significant")
        return False
    
    # Test 7: Verify specific known trends
    print("\n[TEST 6] Verifying known trends from sample data...")
    
    # Ahmedabad ANC should show -18.82% (85 → 69)
    ahmedabad_anc = all_trends[
        (all_trends['district'] == 'Ahmedabad') & 
        (all_trends['indicator'] == 'anc_coverage')
    ]
    if len(ahmedabad_anc) == 1:
        change = ahmedabad_anc['change_pct'].iloc[0]
        if abs(change - (-18.82)) < 0.1:
            print(f"✓ Ahmedabad ANC: {change}% (expected -18.82%)")
        else:
            print(f"✗ Ahmedabad ANC: {change}% (expected -18.82%)")
            return False
    else:
        print("✗ Ahmedabad ANC trend not found")
        return False
    
    # Mehsana high_risk should show 154.55% (11 → 28)
    mehsana_risk = all_trends[
        (all_trends['district'] == 'Mehsana') & 
        (all_trends['indicator'] == 'high_risk_cases')
    ]
    if len(mehsana_risk) == 1:
        change = mehsana_risk['change_pct'].iloc[0]
        if abs(change - 154.55) < 0.1:
            print(f"✓ Mehsana high_risk_cases: {change}% (expected 154.55%)")
        else:
            print(f"✗ Mehsana high_risk_cases: {change}% (expected 154.55%)")
            return False
    else:
        print("✗ Mehsana high_risk_cases trend not found")
        return False
    
    # Test 8: Filter by district
    print("\n[TEST 7] Testing district-specific filtering...")
    ahmedabad_trends = detector.get_trends_by_district("Ahmedabad")
    expected_ahmedabad = 4  # 4 indicators
    
    if len(ahmedabad_trends) == expected_ahmedabad:
        print(f"✓ Ahmedabad trends: {len(ahmedabad_trends)} (expected {expected_ahmedabad})")
    else:
        print(f"✗ Ahmedabad trends: {len(ahmedabad_trends)} (expected {expected_ahmedabad})")
        return False
    
    # Test 9: Filter by indicator
    print("\n[TEST 8] Testing indicator-specific filtering...")
    anc_trends = detector.get_trends_by_indicator("anc_coverage")
    expected_anc = 6  # 6 districts
    
    if len(anc_trends) == expected_anc:
        print(f"✓ ANC coverage trends: {len(anc_trends)} (expected {expected_anc})")
    else:
        print(f"✗ ANC coverage trends: {len(anc_trends)} (expected {expected_anc})")
        return False
    
    # Test 10: Configurable threshold
    print("\n[TEST 9] Testing configurable threshold...")
    detector_5 = TrendDetector(df, threshold=5.0)
    significant_5 = detector_5.get_significant_trends()
    
    detector_20 = TrendDetector(df, threshold=20.0)
    significant_20 = detector_20.get_significant_trends()
    
    if len(significant_5) >= len(significant) >= len(significant_20):
        print(f"✓ Threshold works correctly:")
        print(f"  5% threshold: {len(significant_5)} significant trends")
        print(f"  10% threshold: {len(significant)} significant trends")
        print(f"  20% threshold: {len(significant_20)} significant trends")
    else:
        print(f"✗ Threshold filtering not working correctly")
        print(f"  5%: {len(significant_5)}, 10%: {len(significant)}, 20%: {len(significant_20)}")
        return False
    
    # Test 11: Summary generation
    print("\n[TEST 10] Testing summary generation...")
    summary = detector.summarize_trends()
    
    required_keys = ['total_trends_detected', 'significant_trends', 'threshold_used',
                     'districts_analyzed', 'indicators_analyzed']
    
    if all(key in summary for key in required_keys):
        print("✓ Summary contains all required keys")
        print(f"  Total trends: {summary['total_trends_detected']}")
        print(f"  Significant: {summary['significant_trends']}")
        print(f"  Threshold: {summary['threshold_used']}%")
        print(f"  Districts: {summary['districts_analyzed']}")
        print(f"  Indicators: {summary['indicators_analyzed']}")
        
        if 'largest_increase' in summary:
            inc = summary['largest_increase']
            print(f"  Largest increase: {inc['district']} - {inc['indicator']} ({inc['change_pct']}%)")
        
        if 'largest_decrease' in summary:
            dec = summary['largest_decrease']
            print(f"  Largest decrease: {dec['district']} - {dec['indicator']} ({dec['change_pct']}%)")
    else:
        print("✗ Summary missing required keys")
        return False
    
    print("\n" + "=" * 70)
    print("✓ ALL PHASE 2 TESTS PASSED")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_phase2()
    sys.exit(0 if success else 1)
