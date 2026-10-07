"""
Data Loading and Validation Module
Handles CSV loading, schema validation, and data quality checks
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class DataLoader:
    """Loads and validates healthcare performance data"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.required_columns = [
            'month', 'district', 'anc_coverage', 
            'institutional_delivery', 'immunization', 'high_risk_cases'
        ]
        
    def load_data(self) -> pd.DataFrame:
        """Load CSV file into DataFrame"""
        try:
            self.df = pd.read_csv(self.file_path)
            self.df['month'] = pd.to_datetime(self.df['month'])
            return self.df
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {self.file_path}")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def validate_schema(self) -> Tuple[bool, List[str]]:
        """Check if all required columns are present"""
        if self.df is None:
            return False, ["Data not loaded yet"]
        
        missing_cols = [col for col in self.required_columns if col not in self.df.columns]
        
        if missing_cols:
            return False, [f"Missing columns: {', '.join(missing_cols)}"]
        
        return True, []
    
    def get_missing_values_report(self) -> Dict[str, int]:
        """Return count of missing values per column"""
        if self.df is None:
            return {}
        return self.df.isnull().sum().to_dict()
    
    def print_data_summary(self):
        """Print comprehensive data summary"""
        if self.df is None:
            print("No data loaded")
            return
        
        print("=" * 60)
        print("DATA SUMMARY")
        print("=" * 60)
        
        print("\n1. FIRST 5 ROWS:")
        print("-" * 60)
        print(self.df.head())
        
        print("\n2. DATA INFO:")
        print("-" * 60)
        print(self.df.info())
        
        print("\n3. MISSING VALUES:")
        print("-" * 60)
        missing_report = self.get_missing_values_report()
        for col, count in missing_report.items():
            print(f"{col}: {count} missing values")
        
        total_missing = sum(missing_report.values())
        print(f"\nTotal missing values: {total_missing}")
        
        print("\n4. BASIC STATISTICS:")
        print("-" * 60)
        print(self.df.describe())
        
        print("\n5. UNIQUE VALUES:")
        print("-" * 60)
        print(f"Districts: {self.df['district'].nunique()}")
        print(f"Months: {self.df['month'].nunique()}")
        print(f"Total records: {len(self.df)}")
        
        print("=" * 60)
    
    def get_filtered_data(self, district: str = None, month: str = None, 
                         indicator: str = None) -> pd.DataFrame:
        """
        Filter data by district, month, or indicator
        
        Args:
            district: District name to filter
            month: Month to filter (YYYY-MM-DD format)
            indicator: Column name to filter on
        
        Returns:
            Filtered DataFrame
        """
        if self.df is None:
            return pd.DataFrame()
        
        filtered_df = self.df.copy()
        
        if district:
            filtered_df = filtered_df[filtered_df['district'] == district]
        
        if month:
            month_dt = pd.to_datetime(month)
            filtered_df = filtered_df[filtered_df['month'] == month_dt]
        
        if indicator and indicator in self.df.columns:
            filtered_df = filtered_df[['month', 'district', indicator]]
        
        return filtered_df
    
    def get_available_districts(self) -> List[str]:
        """Return list of unique districts"""
        if self.df is None:
            return []
        return sorted(self.df['district'].unique().tolist())
    
    def get_available_months(self) -> List[str]:
        """Return list of unique months"""
        if self.df is None:
            return []
        return sorted(self.df['month'].dt.strftime('%Y-%m-%d').unique().tolist())
    
    def get_indicators(self) -> List[str]:
        """Return list of indicator columns"""
        if self.df is None:
            return []
        return [col for col in self.required_columns if col not in ['month', 'district']]


if __name__ == "__main__":
    # Test the data loader
    loader = DataLoader("data/healthcare_data.csv")
    
    print("Loading data...")
    df = loader.load_data()
    
    print("\nValidating schema...")
    is_valid, errors = loader.validate_schema()
    if is_valid:
        print("Schema validation: PASSED")
    else:
        print(f"Schema validation: FAILED - {errors}")
    
    print("\nGenerating data summary...")
    loader.print_data_summary()
    
    print("\n\nAvailable districts:", loader.get_available_districts())
    print("Available months:", loader.get_available_months())
    print("Available indicators:", loader.get_indicators())
