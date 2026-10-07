"""
Phase 1 Test Script
Tests data loading and validation functionality
"""

import sys
sys.path.append('.')
from src.data_loader import DataLoader


def test_phase1():
    """Run all Phase 1 tests"""
    print("\n" + "=" * 70)
    print("PHASE 1 TEST: DATA LOADING & VALIDATION")
    print("=" * 70)
    
    # Test 1: Load data
    print("\n[TEST 1] Loading data from CSV...")
    try:
        loader = DataLoader("data/healthcare_data.csv")
        df = loader.load_data()
        print(f"✓ Data loaded successfully: {len(df)} rows")
    except Exception as e:
        print(f"✗ Failed to load data: {e}")
        return False
    
    # Test 2: Schema validation
    print("\n[TEST 2] Validating schema...")
    is_valid, errors = loader.validate_schema()
    if is_valid:
        print("✓ Schema validation passed")
    else:
        print(f"✗ Schema validation failed: {errors}")
        return False
    
    # Test 3: Check required columns
    print("\n[TEST 3] Checking required columns...")
    required = ['month', 'district', 'anc_coverage', 'institutional_delivery', 
                'immunization', 'high_risk_cases']
    missing = [col for col in required if col not in df.columns]
    if not missing:
        print(f"✓ All required columns present: {required}")
    else:
        print(f"✗ Missing columns: {missing}")
        return False
    
    # Test 4: Missing values check
    print("\n[TEST 4] Checking for missing values...")
    missing_report = loader.get_missing_values_report()
    total_missing = sum(missing_report.values())
    if total_missing == 0:
        print("✓ No missing values found")
    else:
        print(f"⚠ Found {total_missing} missing values:")
        for col, count in missing_report.items():
            if count > 0:
                print(f"  - {col}: {count}")
    
    # Test 5: Data summary
    print("\n[TEST 5] Generating data summary...")
    loader.print_data_summary()
    
    # Test 6: Filter functionality
    print("\n[TEST 6] Testing filter functions...")
    districts = loader.get_available_districts()
    months = loader.get_available_months()
    indicators = loader.get_indicators()
    
    print(f"✓ Districts found: {len(districts)} - {districts}")
    print(f"✓ Months found: {len(months)} - {months}")
    print(f"✓ Indicators found: {len(indicators)} - {indicators}")
    
    # Test 7: Filter by district
    print("\n[TEST 7] Testing district filter...")
    ahmedabad_data = loader.get_filtered_data(district="Ahmedabad")
    print(f"✓ Ahmedabad data: {len(ahmedabad_data)} rows")
    print(ahmedabad_data)
    
    # Test 8: Filter by month
    print("\n[TEST 8] Testing month filter...")
    july_data = loader.get_filtered_data(month="2026-07-01")
    print(f"✓ July 2026 data: {len(july_data)} rows")
    
    # Test 9: Filter by indicator
    print("\n[TEST 9] Testing indicator filter...")
    anc_data = loader.get_filtered_data(indicator="anc_coverage")
    print(f"✓ ANC coverage data: {anc_data.shape}")
    print(anc_data.head())
    
    # Test 10: Data types
    print("\n[TEST 10] Checking data types...")
    print(df.dtypes)
    if df['month'].dtype == 'datetime64[ns]':
        print("✓ Month column is datetime type")
    else:
        print("✗ Month column is not datetime type")
        return False
    
    print("\n" + "=" * 70)
    print("✓ ALL PHASE 1 TESTS PASSED")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_phase1()
    sys.exit(0 if success else 1)
