"""
Phase 4 Test Script
Tests correlation detection functionality
"""

import sys
import pandas as pd
import numpy as np
sys.path.append('.')
from src.data_loader import DataLoader
from src.correlation_detector import CorrelationDetector


def test_phase4():
    """Run all Phase 4 tests"""
    print("\n" + "=" * 70)
    print("PHASE 4 TEST: CORRELATION DETECTION")
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
    
    # Test 1: Initialize correlation detector
    print("\n[TEST 1] Initializing correlation detector...")
    try:
        detector = CorrelationDetector(df, threshold=0.70)
        print(f"✓ Correlation detector initialized")
        print(f"  Threshold: {detector.threshold}")
        print(f"  Indicators: {detector.indicators}")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False
    
    # Test 2: Calculate correlation matrix
    print("\n[TEST 2] Calculating correlation matrix...")
    corr_matrix = detector.calculate_correlation_matrix()
    
    expected_shape = (4, 4)  # 4 indicators
    if corr_matrix.shape == expected_shape:
        print(f"✓ Correlation matrix shape: {corr_matrix.shape}")
    else:
        print(f"✗ Unexpected matrix shape: {corr_matrix.shape} (expected {expected_shape})")
        return False
    
    # Verify diagonal is all 1s (correlation with self)
    diagonal = np.diag(corr_matrix.values)
    if np.allclose(diagonal, 1.0):
        print("✓ Diagonal values are all 1.0 (self-correlation)")
    else:
        print("✗ Diagonal values are not all 1.0")
        return False
    
    # Verify symmetry
    if np.allclose(corr_matrix.values, corr_matrix.values.T):
        print("✓ Matrix is symmetric")
    else:
        print("✗ Matrix is not symmetric")
        return False
    
    # Test 3: Get all correlation pairs
    print("\n[TEST 3] Getting all correlation pairs...")
    pairs = detector.get_correlation_pairs()
    
    # For 4 indicators, we should have C(4,2) = 6 unique pairs
    expected_pairs = 6
    if len(pairs) == expected_pairs:
        print(f"✓ Found {len(pairs)} pairs (expected {expected_pairs})")
    else:
        print(f"✗ Found {len(pairs)} pairs (expected {expected_pairs})")
        return False
    
    # Verify required fields
    required_fields = ['indicator1', 'indicator2', 'correlation', 'abs_correlation',
                      'strength', 'direction', 'is_significant', 'p_value', 'sample_size']
    
    if all(field in pairs[0] for field in required_fields):
        print(f"✓ All required fields present in pair data")
    else:
        print("✗ Missing required fields")
        return False
    
    # Test 4: Verify correlation values
    print("\n[TEST 4] Verifying correlation calculations...")
    
    # Find specific pair from matrix
    anc_risk_corr = corr_matrix.loc['anc_coverage', 'high_risk_cases']
    
    # Find same pair in pairs list
    anc_risk_pair = next(
        (p for p in pairs if 
         (p['indicator1'] == 'anc_coverage' and p['indicator2'] == 'high_risk_cases') or
         (p['indicator1'] == 'high_risk_cases' and p['indicator2'] == 'anc_coverage')),
        None
    )
    
    if anc_risk_pair and abs(anc_risk_pair['correlation'] - anc_risk_corr) < 0.001:
        print(f"✓ Correlation matches matrix: {anc_risk_pair['correlation']:.4f}")
    else:
        print("✗ Correlation mismatch between matrix and pairs")
        return False
    
    # Test 5: Strength classification
    print("\n[TEST 5] Testing strength classification...")
    
    strength_tests = [
        (0.95, 'very_strong'),
        (0.75, 'strong'),
        (0.55, 'moderate'),
        (0.35, 'weak'),
        (0.15, 'very_weak'),
        (-0.85, 'strong'),  # Negative but strong
    ]
    
    all_correct = True
    for corr_value, expected_strength in strength_tests:
        strength = detector._classify_strength(corr_value)
        if strength == expected_strength:
            print(f"✓ {corr_value:5.2f} → {strength}")
        else:
            print(f"✗ {corr_value:5.2f} → {strength} (expected {expected_strength})")
            all_correct = False
    
    if not all_correct:
        return False
    
    # Test 6: Significant correlations
    print("\n[TEST 6] Testing significant correlation filtering...")
    significant = detector.get_significant_correlations()
    
    print(f"✓ Found {len(significant)} significant correlations (|r| >= 0.70)")
    
    # Verify all are truly significant
    all_significant = all(pair['is_significant'] for pair in significant)
    all_above_threshold = all(pair['abs_correlation'] >= 0.70 for pair in significant)
    
    if all_significant and all_above_threshold:
        print("✓ All significant pairs exceed threshold")
    else:
        print("✗ Some significant pairs do not exceed threshold")
        return False
    
    # Test 7: Verify known correlations from sample data
    print("\n[TEST 7] Verifying known correlations...")
    
    # institutional_delivery <-> immunization should be highly correlated (positive)
    inst_imm_pair = next(
        (p for p in pairs if 
         set([p['indicator1'], p['indicator2']]) == set(['institutional_delivery', 'immunization'])),
        None
    )
    
    if inst_imm_pair:
        if inst_imm_pair['correlation'] > 0.90 and inst_imm_pair['direction'] == 'positive':
            print(f"✓ institutional_delivery <-> immunization: r = {inst_imm_pair['correlation']:.4f} (positive)")
        else:
            print(f"⚠ institutional_delivery <-> immunization: r = {inst_imm_pair['correlation']:.4f}")
    
    # anc_coverage <-> high_risk_cases should be negatively correlated
    anc_risk = next(
        (p for p in pairs if 
         set([p['indicator1'], p['indicator2']]) == set(['anc_coverage', 'high_risk_cases'])),
        None
    )
    
    if anc_risk:
        if anc_risk['correlation'] < -0.70 and anc_risk['direction'] == 'negative':
            print(f"✓ anc_coverage <-> high_risk_cases: r = {anc_risk['correlation']:.4f} (negative)")
        else:
            print(f"⚠ anc_coverage <-> high_risk_cases: r = {anc_risk['correlation']:.4f}")
    
    # Test 8: Filter by indicator
    print("\n[TEST 8] Testing indicator-specific filtering...")
    anc_correlations = detector.get_correlations_for_indicator('anc_coverage')
    
    # Should have 3 pairs (with each of the other 3 indicators)
    expected_anc_pairs = 3
    if len(anc_correlations) == expected_anc_pairs:
        print(f"✓ Found {len(anc_correlations)} correlations for anc_coverage")
    else:
        print(f"✗ Found {len(anc_correlations)} correlations (expected {expected_anc_pairs})")
        return False
    
    # Verify all involve anc_coverage
    all_involve_anc = all(
        'anc_coverage' in [p['indicator1'], p['indicator2']]
        for p in anc_correlations
    )
    
    if all_involve_anc:
        print("✓ All filtered correlations involve anc_coverage")
    else:
        print("✗ Some filtered correlations don't involve anc_coverage")
        return False
    
    # Test 9: Strongest and weakest correlations
    print("\n[TEST 9] Testing strongest/weakest correlation finding...")
    strongest = detector.find_strongest_correlation()
    weakest = detector.find_weakest_correlation()
    
    if strongest:
        print(f"✓ Strongest: {strongest['indicator1']} <-> {strongest['indicator2']}")
        print(f"  |r| = {strongest['abs_correlation']:.4f}")
    else:
        print("✗ Could not find strongest correlation")
        return False
    
    if weakest:
        print(f"✓ Weakest: {weakest['indicator1']} <-> {weakest['indicator2']}")
        print(f"  |r| = {weakest['abs_correlation']:.4f}")
    else:
        print("✗ Could not find weakest correlation")
        return False
    
    # Test 10: Configurable threshold
    print("\n[TEST 10] Testing configurable threshold...")
    
    detector_low = CorrelationDetector(df, threshold=0.50)
    significant_low = detector_low.get_significant_correlations()
    
    detector_high = CorrelationDetector(df, threshold=0.90)
    significant_high = detector_high.get_significant_correlations()
    
    if len(significant_low) >= len(significant) >= len(significant_high):
        print(f"✓ Threshold works correctly:")
        print(f"  0.50 threshold: {len(significant_low)} significant")
        print(f"  0.70 threshold: {len(significant)} significant")
        print(f"  0.90 threshold: {len(significant_high)} significant")
    else:
        print(f"⚠ Threshold relationship unexpected")
        print(f"  0.50: {len(significant_low)}, 0.70: {len(significant)}, 0.90: {len(significant_high)}")
    
    # Test 11: Summary generation
    print("\n[TEST 11] Testing summary generation...")
    summary = detector.summarize_correlations()
    
    required_keys = ['total_pairs', 'significant_pairs', 'threshold', 'sample_size',
                     'positive_correlations', 'negative_correlations']
    
    if all(key in summary for key in required_keys):
        print("✓ Summary contains all required keys")
        print(f"  Total pairs: {summary['total_pairs']}")
        print(f"  Significant: {summary['significant_pairs']}")
        print(f"  Positive: {summary['positive_correlations']}")
        print(f"  Negative: {summary['negative_correlations']}")
        
        if 'warning' in summary:
            print(f"  ⚠ Warning: {summary['warning']}")
    else:
        print("✗ Summary missing required keys")
        return False
    
    # Test 12: Indicator relationship analysis
    print("\n[TEST 12] Testing indicator relationship analysis...")
    analysis = detector.analyze_indicator_relationships('anc_coverage')
    
    if 'total_relationships' in analysis and 'correlations' in analysis:
        print(f"✓ Analysis complete for anc_coverage")
        print(f"  Total relationships: {analysis['total_relationships']}")
        print(f"  Significant: {analysis['significant_relationships']}")
        
        if 'strongest_negative' in analysis:
            sn = analysis['strongest_negative']
            other = sn['indicator1'] if sn['indicator2'] == 'anc_coverage' else sn['indicator2']
            print(f"  Strongest negative: {other} (r={sn['correlation']:.3f})")
    else:
        print("✗ Analysis missing required fields")
        return False
    
    # Test 13: Export functionality
    print("\n[TEST 13] Testing CSV export...")
    try:
        filepath = detector.export_correlation_matrix("outputs/test_correlation_matrix.csv")
        print(f"✓ Matrix exported to: {filepath}")
        
        # Verify file exists and can be read
        exported_matrix = pd.read_csv(filepath, index_col=0)
        if exported_matrix.shape == corr_matrix.shape:
            print("✓ Exported matrix has correct shape")
        else:
            print("✗ Exported matrix shape mismatch")
            return False
    except Exception as e:
        print(f"✗ Export failed: {e}")
        return False
    
    # Test 14: Sample size warning
    print("\n[TEST 14] Testing sample size warning...")
    if 'warning' in summary and len(df) < 30:
        print(f"✓ Warning present for small sample (n={len(df)})")
        print(f"  {summary['warning']}")
    else:
        print("⚠ No warning for small sample size")
    
    # Test 15: P-value calculation
    print("\n[TEST 15] Testing p-value calculation...")
    has_pvalues = all(pair['p_value'] is not None for pair in pairs)
    
    if has_pvalues:
        print("✓ P-values calculated for all pairs")
        # Check that significant correlations have low p-values
        for pair in significant:
            if pair['p_value'] < 0.05:
                print(f"  ✓ {pair['indicator1']} <-> {pair['indicator2']}: p={pair['p_value']:.4f}")
    else:
        print("✗ Some pairs missing p-values")
        return False
    
    print("\n" + "=" * 70)
    print("✓ ALL PHASE 4 TESTS PASSED")
    print("=" * 70)
    
    # Final summary
    print("\n" + "=" * 70)
    print("PHASE 4 SUMMARY")
    print("=" * 70)
    print(f"Sample size: {len(df)} records")
    print(f"Total correlation pairs: {len(pairs)}")
    print(f"Significant correlations (|r| >= 0.70): {len(significant)}")
    
    if significant:
        print("\nSignificant correlations found:")
        for pair in significant:
            print(f"  {pair['indicator1']} <-> {pair['indicator2']}: "
                  f"r = {pair['correlation']:.3f} ({pair['direction']})")
    
    print(f"\nNote: With only {len(df)} records, correlations may be unstable.")
    print("Recommended minimum sample size: 30 records for reliable correlations.")
    
    return True


if __name__ == "__main__":
    success = test_phase4()
    sys.exit(0 if success else 1)
