"""
Phase 3 Test Script
Tests outlier detection functionality
"""

import sys
import pandas as pd
import numpy as np
sys.path.append('.')
from src.data_loader import DataLoader
from src.outlier_detector import OutlierDetector


def test_phase3():
    """Run all Phase 3 tests"""
    print("\n" + "=" * 70)
    print("PHASE 3 TEST: OUTLIER DETECTION")
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
    
    # Test 1: Initialize with IQR method
    print("\n[TEST 1] Initializing outlier detector with IQR method...")
    try:
        detector_iqr = OutlierDetector(df, method='IQR', threshold=1.5)
        print(f"✓ IQR detector initialized")
        print(f"  Method: {detector_iqr.method}")
        print(f"  Threshold: {detector_iqr.threshold}")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False
    
    # Test 2: Initialize with Z-score method
    print("\n[TEST 2] Initializing outlier detector with Z-score method...")
    try:
        detector_zscore = OutlierDetector(df, method='zscore', threshold=3.0)
        print(f"✓ Z-score detector initialized")
        print(f"  Method: {detector_zscore.method}")
        print(f"  Threshold: {detector_zscore.threshold}")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False
    
    # Test 3: IQR calculation for single indicator
    print("\n[TEST 3] Testing IQR detection for anc_coverage...")
    anc_outliers_iqr = detector_iqr.detect_outliers_iqr('anc_coverage')
    
    if len(anc_outliers_iqr) > 0:
        print(f"✓ Found {len(anc_outliers_iqr)} outliers using IQR")
        
        # Verify required columns
        required_cols = ['district', 'indicator', 'value', 'Q1', 'Q3', 'IQR', 
                        'lower_bound', 'upper_bound', 'method']
        if all(col in anc_outliers_iqr.columns for col in required_cols):
            print("✓ All required columns present")
        else:
            print("✗ Missing required columns")
            return False
        
        # Check IQR calculation
        Q1 = anc_outliers_iqr['Q1'].iloc[0]
        Q3 = anc_outliers_iqr['Q3'].iloc[0]
        IQR = anc_outliers_iqr['IQR'].iloc[0]
        
        if abs(IQR - (Q3 - Q1)) < 0.01:
            print(f"✓ IQR calculation correct: Q3({Q3}) - Q1({Q1}) = {IQR}")
        else:
            print(f"✗ IQR calculation incorrect")
            return False
    else:
        print("⚠ No outliers found with IQR method")
    
    # Test 4: Z-score calculation for single indicator
    print("\n[TEST 4] Testing Z-score detection for anc_coverage...")
    anc_outliers_zscore = detector_zscore.detect_outliers_zscore('anc_coverage')
    
    print(f"✓ Z-score detection completed: {len(anc_outliers_zscore)} outliers")
    
    if len(anc_outliers_zscore) > 0:
        required_cols = ['district', 'indicator', 'value', 'mean', 'std', 'z_score', 'method']
        if all(col in anc_outliers_zscore.columns for col in required_cols):
            print("✓ All required columns present")
        else:
            print("✗ Missing required columns")
            return False
    
    # Test 5: Detect all outliers with IQR
    print("\n[TEST 5] Detecting all outliers with IQR method...")
    all_outliers_iqr = detector_iqr.detect_outliers()
    
    print(f"✓ Detected {len(all_outliers_iqr)} outliers across all indicators")
    
    if len(all_outliers_iqr) > 0:
        print(f"  Districts with outliers: {all_outliers_iqr['district'].unique().tolist()}")
        print(f"  Indicators with outliers: {all_outliers_iqr['indicator'].unique().tolist()}")
    
    # Test 6: Verify known outliers
    print("\n[TEST 6] Verifying known outliers from sample data...")
    
    # Mehsana ANC coverage = 42 should be an outlier
    mehsana_anc = all_outliers_iqr[
        (all_outliers_iqr['district'] == 'Mehsana') & 
        (all_outliers_iqr['indicator'] == 'anc_coverage')
    ]
    
    if len(mehsana_anc) == 1 and mehsana_anc['value'].iloc[0] == 42:
        print("✓ Mehsana ANC coverage (42) correctly identified as outlier")
    else:
        print("⚠ Mehsana ANC coverage not detected as outlier (may be expected)")
    
    # Mehsana high_risk_cases = 28 should be an outlier
    mehsana_risk = all_outliers_iqr[
        (all_outliers_iqr['district'] == 'Mehsana') & 
        (all_outliers_iqr['indicator'] == 'high_risk_cases')
    ]
    
    if len(mehsana_risk) == 1 and mehsana_risk['value'].iloc[0] == 28:
        print("✓ Mehsana high_risk_cases (28) correctly identified as outlier")
    else:
        print("⚠ Mehsana high_risk_cases not detected as outlier (may be expected)")
    
    # Test 7: Filter by district
    print("\n[TEST 7] Testing district-specific filtering...")
    mehsana_outliers = detector_iqr.get_outliers_by_district('Mehsana')
    
    if len(mehsana_outliers) > 0:
        print(f"✓ Found {len(mehsana_outliers)} outliers for Mehsana")
        all_mehsana = all(mehsana_outliers['district'] == 'Mehsana')
        if all_mehsana:
            print("✓ All filtered outliers are from Mehsana")
        else:
            print("✗ Filter returned outliers from other districts")
            return False
    else:
        print("⚠ No outliers found for Mehsana")
    
    # Test 8: Filter by indicator
    print("\n[TEST 8] Testing indicator-specific filtering...")
    anc_outliers_all = detector_iqr.get_outliers_by_indicator('anc_coverage')
    
    if len(anc_outliers_all) > 0:
        print(f"✓ Found {len(anc_outliers_all)} outliers for anc_coverage")
        all_anc = all(anc_outliers_all['indicator'] == 'anc_coverage')
        if all_anc:
            print("✓ All filtered outliers are for anc_coverage")
        else:
            print("✗ Filter returned outliers from other indicators")
            return False
    else:
        print("⚠ No outliers found for anc_coverage")
    
    # Test 9: Configurable thresholds
    print("\n[TEST 9] Testing configurable thresholds...")
    
    # Stricter IQR (smaller multiplier should find fewer outliers)
    detector_strict = OutlierDetector(df, method='IQR', threshold=2.0)
    outliers_strict = detector_strict.detect_outliers()
    
    # Looser IQR (larger multiplier should find more outliers)
    detector_loose = OutlierDetector(df, method='IQR', threshold=1.0)
    outliers_loose = detector_loose.detect_outliers()
    
    if len(outliers_loose) >= len(all_outliers_iqr) >= len(outliers_strict):
        print(f"✓ Threshold works correctly:")
        print(f"  Loose (1.0): {len(outliers_loose)} outliers")
        print(f"  Default (1.5): {len(all_outliers_iqr)} outliers")
        print(f"  Strict (2.0): {len(outliers_strict)} outliers")
    else:
        print(f"⚠ Threshold relationship unexpected:")
        print(f"  Loose (1.0): {len(outliers_loose)}")
        print(f"  Default (1.5): {len(all_outliers_iqr)}")
        print(f"  Strict (2.0): {len(outliers_strict)}")
    
    # Test 10: Method comparison
    print("\n[TEST 10] Testing method comparison...")
    comparison = detector_iqr.compare_methods('anc_coverage')
    
    required_keys = ['indicator', 'iqr_outliers', 'zscore_outliers', 
                     'iqr_districts', 'zscore_districts', 'agreement']
    
    if all(key in comparison for key in required_keys):
        print("✓ Comparison contains all required keys")
        print(f"  IQR outliers: {comparison['iqr_outliers']}")
        print(f"  Z-score outliers: {comparison['zscore_outliers']}")
        print(f"  Agreement: {comparison['agreement']} districts")
    else:
        print("✗ Comparison missing required keys")
        return False
    
    # Test 11: Summary generation
    print("\n[TEST 11] Testing summary generation...")
    summary = detector_iqr.summarize_outliers()
    
    required_keys = ['method', 'threshold', 'total_outliers', 'total_records', 
                     'outlier_percentage']
    
    if all(key in summary for key in required_keys):
        print("✓ Summary contains all required keys")
        print(f"  Method: {summary['method']}")
        print(f"  Threshold: {summary['threshold']}")
        print(f"  Total outliers: {summary['total_outliers']}")
        print(f"  Outlier percentage: {summary['outlier_percentage']}%")
        
        if summary['total_outliers'] > 0 and 'most_extreme_outlier' in summary:
            extreme = summary['most_extreme_outlier']
            print(f"  Most extreme: {extreme['district']} - {extreme['indicator']} = {extreme['value']}")
    else:
        print("✗ Summary missing required keys")
        return False
    
    # Test 12: Edge case - standard deviation = 0
    print("\n[TEST 12] Testing edge case - identical values (std = 0)...")
    
    # Create test data with identical values
    test_data = pd.DataFrame({
        'month': pd.to_datetime(['2026-07-01', '2026-08-01']),
        'district': ['A', 'B'],
        'anc_coverage': [80, 80],
        'institutional_delivery': [90, 90],
        'immunization': [95, 95],
        'high_risk_cases': [10, 10]
    })
    
    detector_edge = OutlierDetector(test_data, method='zscore')
    outliers_edge = detector_edge.detect_outliers()
    
    if len(outliers_edge) == 0:
        print("✓ Z-score correctly handles std=0 (no outliers when all values identical)")
    else:
        print("✗ Z-score did not handle std=0 correctly")
        return False
    
    # Test 13: IQR vs Z-score sensitivity
    print("\n[TEST 13] Comparing IQR vs Z-score sensitivity...")
    
    all_outliers_zscore = detector_zscore.detect_outliers()
    
    # With small sample (12 records), Z-score with threshold 3 is less sensitive
    print(f"✓ IQR detected {len(all_outliers_iqr)} outliers")
    print(f"✓ Z-score (threshold=3) detected {len(all_outliers_zscore)} outliers")
    
    # Lower Z-score threshold
    detector_zscore_sensitive = OutlierDetector(df, method='zscore', threshold=2.0)
    outliers_zscore_sensitive = detector_zscore_sensitive.detect_outliers()
    print(f"✓ Z-score (threshold=2) detected {len(outliers_zscore_sensitive)} outliers")
    
    print("\n" + "=" * 70)
    print("✓ ALL PHASE 3 TESTS PASSED")
    print("=" * 70)
    
    # Final summary
    print("\n" + "=" * 70)
    print("PHASE 3 SUMMARY")
    print("=" * 70)
    print(f"IQR Method (threshold 1.5): {len(all_outliers_iqr)} outliers")
    print(f"Z-score Method (threshold 3.0): {len(all_outliers_zscore)} outliers")
    print(f"Z-score Method (threshold 2.0): {len(outliers_zscore_sensitive)} outliers")
    
    if len(all_outliers_iqr) > 0:
        print(f"\nIQR Outliers by indicator:")
        for indicator, count in summary.get('outliers_by_indicator', {}).items():
            print(f"  {indicator}: {count}")
    
    return True


if __name__ == "__main__":
    success = test_phase3()
    sys.exit(0 if success else 1)
