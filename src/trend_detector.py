"""
Trend Detection Module
Detects significant changes in indicators over time for each district
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


class TrendDetector:
    """Detects trends by comparing current vs previous period values"""
    
    def __init__(self, df: pd.DataFrame, threshold: float = 10.0):
        """
        Initialize trend detector
        
        Args:
            df: DataFrame with columns [month, district, indicators...]
            threshold: Minimum percentage change to flag as significant (default 10%)
        """
        self.df = df.copy()
        self.threshold = threshold
        self.indicators = ['anc_coverage', 'institutional_delivery', 'immunization', 'high_risk_cases']
        
    def calculate_percentage_change(self, current: float, previous: float) -> float:
        """
        Calculate percentage change between two values
        
        Formula: ((current - previous) / previous) * 100
        
        Args:
            current: Current period value
            previous: Previous period value
            
        Returns:
            Percentage change (positive for increase, negative for decrease)
            Returns None if calculation not possible
        """
        # Handle edge cases
        if pd.isna(current) or pd.isna(previous):
            return None
        
        if previous == 0:
            # If previous is 0 and current is not, it's infinite growth
            # Return None to indicate undefined
            if current != 0:
                return None
            else:
                return 0.0
        
        pct_change = ((current - previous) / previous) * 100
        return round(pct_change, 2)
    
    def detect_trends(self) -> pd.DataFrame:
        """
        Detect trends for all districts and indicators
        
        Returns:
            DataFrame with columns:
            - district
            - indicator
            - period (current month)
            - current_value
            - previous_value
            - change_pct
            - is_significant (True if |change_pct| >= threshold)
        """
        trends = []
        
        # Sort by district and month to ensure correct ordering
        df_sorted = self.df.sort_values(['district', 'month'])
        
        # Group by district
        for district in df_sorted['district'].unique():
            district_data = df_sorted[df_sorted['district'] == district]
            
            # Need at least 2 records to compare
            if len(district_data) < 2:
                continue
            
            # For each indicator
            for indicator in self.indicators:
                if indicator not in district_data.columns:
                    continue
                
                # Get values as list ordered by time
                values = district_data[indicator].tolist()
                months = district_data['month'].tolist()
                
                # Compare each month with the previous one
                for i in range(1, len(values)):
                    current_value = values[i]
                    previous_value = values[i-1]
                    current_month = months[i]
                    
                    # Calculate percentage change
                    pct_change = self.calculate_percentage_change(current_value, previous_value)
                    
                    # Skip if calculation failed
                    if pct_change is None:
                        continue
                    
                    # Check if change is significant
                    is_significant = abs(pct_change) >= self.threshold
                    
                    # Add to results
                    trends.append({
                        'district': district,
                        'indicator': indicator,
                        'period': current_month,
                        'current_value': current_value,
                        'previous_value': previous_value,
                        'change_pct': pct_change,
                        'is_significant': is_significant
                    })
        
        return pd.DataFrame(trends)
    
    def get_significant_trends(self) -> pd.DataFrame:
        """
        Get only the significant trends (|change| >= threshold)
        
        Returns:
            DataFrame containing only trends flagged as significant
        """
        all_trends = self.detect_trends()
        return all_trends[all_trends['is_significant'] == True]
    
    def get_trends_by_district(self, district: str) -> pd.DataFrame:
        """
        Get trends for a specific district
        
        Args:
            district: District name
            
        Returns:
            DataFrame with trends for the specified district
        """
        all_trends = self.detect_trends()
        return all_trends[all_trends['district'] == district]
    
    def get_trends_by_indicator(self, indicator: str) -> pd.DataFrame:
        """
        Get trends for a specific indicator across all districts
        
        Args:
            indicator: Indicator name
            
        Returns:
            DataFrame with trends for the specified indicator
        """
        all_trends = self.detect_trends()
        return all_trends[all_trends['indicator'] == indicator]
    
    def summarize_trends(self) -> Dict:
        """
        Generate summary statistics about detected trends
        
        Returns:
            Dictionary with trend summary statistics
        """
        all_trends = self.detect_trends()
        significant_trends = self.get_significant_trends()
        
        summary = {
            'total_trends_detected': len(all_trends),
            'significant_trends': len(significant_trends),
            'threshold_used': self.threshold,
            'districts_analyzed': all_trends['district'].nunique() if len(all_trends) > 0 else 0,
            'indicators_analyzed': all_trends['indicator'].nunique() if len(all_trends) > 0 else 0,
        }
        
        if len(significant_trends) > 0:
            summary['largest_increase'] = {
                'district': significant_trends.loc[significant_trends['change_pct'].idxmax(), 'district'],
                'indicator': significant_trends.loc[significant_trends['change_pct'].idxmax(), 'indicator'],
                'change_pct': significant_trends['change_pct'].max()
            }
            summary['largest_decrease'] = {
                'district': significant_trends.loc[significant_trends['change_pct'].idxmin(), 'district'],
                'indicator': significant_trends.loc[significant_trends['change_pct'].idxmin(), 'indicator'],
                'change_pct': significant_trends['change_pct'].min()
            }
        
        return summary


if __name__ == "__main__":
    # Test the trend detector
    from data_loader import DataLoader
    
    print("=" * 70)
    print("TREND DETECTOR TEST")
    print("=" * 70)
    
    # Load data
    loader = DataLoader("data/healthcare_data.csv")
    df = loader.load_data()
    
    print(f"\nLoaded {len(df)} records")
    print(f"Districts: {df['district'].unique().tolist()}")
    print(f"Months: {df['month'].unique()}")
    
    # Create trend detector with default threshold (10%)
    print("\n" + "-" * 70)
    print("DETECTING TRENDS (threshold = 10%)")
    print("-" * 70)
    
    detector = TrendDetector(df, threshold=10.0)
    all_trends = detector.detect_trends()
    
    print(f"\nTotal trends detected: {len(all_trends)}")
    print("\nAll trends:")
    print(all_trends.to_string(index=False))
    
    # Get significant trends only
    print("\n" + "-" * 70)
    print("SIGNIFICANT TRENDS ONLY")
    print("-" * 70)
    
    significant = detector.get_significant_trends()
    print(f"\nSignificant trends (|change| >= 10%): {len(significant)}")
    print("\n" + significant.to_string(index=False))
    
    # Summary
    print("\n" + "-" * 70)
    print("TREND SUMMARY")
    print("-" * 70)
    
    summary = detector.summarize_trends()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Test with different threshold
    print("\n" + "=" * 70)
    print("TESTING WITH DIFFERENT THRESHOLD (5%)")
    print("=" * 70)
    
    detector_low = TrendDetector(df, threshold=5.0)
    significant_low = detector_low.get_significant_trends()
    print(f"\nSignificant trends with 5% threshold: {len(significant_low)}")
    
    # Test specific district
    print("\n" + "-" * 70)
    print("TRENDS FOR AHMEDABAD ONLY")
    print("-" * 70)
    
    ahmedabad_trends = detector.get_trends_by_district("Ahmedabad")
    print(ahmedabad_trends.to_string(index=False))
    
    # Test specific indicator
    print("\n" + "-" * 70)
    print("TRENDS FOR ANC COVERAGE ACROSS ALL DISTRICTS")
    print("-" * 70)
    
    anc_trends = detector.get_trends_by_indicator("anc_coverage")
    print(anc_trends.to_string(index=False))
