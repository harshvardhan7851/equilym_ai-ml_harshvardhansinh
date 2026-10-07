"""
Outlier Detection Module
Detects statistical outliers using IQR and Z-score methods
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


class OutlierDetector:
    """Detects outliers in indicator values across districts"""
    
    def __init__(self, df: pd.DataFrame, method: str = 'IQR', threshold: float = None):
        """
        Initialize outlier detector
        
        Args:
            df: DataFrame with columns [month, district, indicators...]
            method: Detection method - 'IQR' or 'zscore' (default 'IQR')
            threshold: 
                - For IQR: multiplier for IQR (default 1.5)
                - For zscore: Z-score threshold (default 3.0)
        """
        self.df = df.copy()
        self.method = method.upper()
        self.indicators = ['anc_coverage', 'institutional_delivery', 'immunization', 'high_risk_cases']
        
        # Set default thresholds based on method
        if threshold is None:
            self.threshold = 1.5 if self.method == 'IQR' else 3.0
        else:
            self.threshold = threshold
        
        # Validate method
        if self.method not in ['IQR', 'ZSCORE']:
            raise ValueError(f"Method must be 'IQR' or 'zscore', got '{method}'")
    
    def detect_outliers_iqr(self, indicator: str) -> pd.DataFrame:
        """
        Detect outliers using Interquartile Range (IQR) method
        
        Method: outlier if value > Q3 + threshold*IQR OR value < Q1 - threshold*IQR
        
        Args:
            indicator: Column name to analyze
            
        Returns:
            DataFrame with outlier records
        """
        if indicator not in self.df.columns:
            return pd.DataFrame()
        
        values = self.df[indicator]
        
        # Calculate quartiles
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        
        # Calculate bounds
        lower_bound = Q1 - self.threshold * IQR
        upper_bound = Q3 + self.threshold * IQR
        
        # Find outliers
        outlier_mask = (values < lower_bound) | (values > upper_bound)
        outliers = self.df[outlier_mask].copy()
        
        # Add outlier metadata
        outliers['indicator'] = indicator
        outliers['value'] = outliers[indicator]
        outliers['Q1'] = Q1
        outliers['Q3'] = Q3
        outliers['IQR'] = IQR
        outliers['lower_bound'] = lower_bound
        outliers['upper_bound'] = upper_bound
        outliers['method'] = 'IQR'
        
        return outliers
    
    def detect_outliers_zscore(self, indicator: str) -> pd.DataFrame:
        """
        Detect outliers using Z-score method
        
        Method: outlier if |Z| > threshold, where Z = (value - mean) / std
        
        Args:
            indicator: Column name to analyze
            
        Returns:
            DataFrame with outlier records
        """
        if indicator not in self.df.columns:
            return pd.DataFrame()
        
        values = self.df[indicator]
        
        # Calculate mean and standard deviation
        mean = values.mean()
        std = values.std()
        
        # Handle case where std is 0 (all values identical)
        if std == 0:
            return pd.DataFrame()
        
        # Calculate Z-scores
        z_scores = np.abs((values - mean) / std)
        
        # Find outliers
        outlier_mask = z_scores > self.threshold
        outliers = self.df[outlier_mask].copy()
        
        # Add outlier metadata
        outliers['indicator'] = indicator
        outliers['value'] = outliers[indicator]
        outliers['mean'] = mean
        outliers['std'] = std
        outliers['z_score'] = z_scores[outlier_mask]
        outliers['method'] = 'Z-score'
        
        return outliers
    
    def detect_outliers(self) -> pd.DataFrame:
        """
        Detect outliers for all indicators using configured method
        
        Returns:
            DataFrame with all detected outliers
        """
        all_outliers = []
        
        for indicator in self.indicators:
            if indicator not in self.df.columns:
                continue
            
            if self.method == 'IQR':
                outliers = self.detect_outliers_iqr(indicator)
            else:  # Z-score
                outliers = self.detect_outliers_zscore(indicator)
            
            if len(outliers) > 0:
                all_outliers.append(outliers)
        
        if len(all_outliers) == 0:
            return pd.DataFrame()
        
        return pd.concat(all_outliers, ignore_index=True)
    
    def get_outliers_by_district(self, district: str) -> pd.DataFrame:
        """
        Get outliers for a specific district
        
        Args:
            district: District name
            
        Returns:
            DataFrame with outliers for the specified district
        """
        all_outliers = self.detect_outliers()
        if len(all_outliers) == 0:
            return pd.DataFrame()
        return all_outliers[all_outliers['district'] == district]
    
    def get_outliers_by_indicator(self, indicator: str) -> pd.DataFrame:
        """
        Get outliers for a specific indicator
        
        Args:
            indicator: Indicator name
            
        Returns:
            DataFrame with outliers for the specified indicator
        """
        all_outliers = self.detect_outliers()
        if len(all_outliers) == 0:
            return pd.DataFrame()
        return all_outliers[all_outliers['indicator'] == indicator]
    
    def compare_methods(self, indicator: str) -> Dict:
        """
        Compare IQR and Z-score methods for a specific indicator
        
        Args:
            indicator: Indicator to analyze
            
        Returns:
            Dictionary with comparison results
        """
        # Save current settings
        original_method = self.method
        original_threshold = self.threshold
        
        # Detect with IQR
        self.method = 'IQR'
        self.threshold = 1.5
        iqr_outliers = self.detect_outliers_iqr(indicator)
        
        # Detect with Z-score
        self.method = 'ZSCORE'
        self.threshold = 3.0
        zscore_outliers = self.detect_outliers_zscore(indicator)
        
        # Restore settings
        self.method = original_method
        self.threshold = original_threshold
        
        comparison = {
            'indicator': indicator,
            'iqr_outliers': len(iqr_outliers),
            'zscore_outliers': len(zscore_outliers),
            'iqr_districts': iqr_outliers['district'].tolist() if len(iqr_outliers) > 0 else [],
            'zscore_districts': zscore_outliers['district'].tolist() if len(zscore_outliers) > 0 else [],
        }
        
        # Find common outliers
        if len(iqr_outliers) > 0 and len(zscore_outliers) > 0:
            common = set(iqr_outliers['district'].tolist()) & set(zscore_outliers['district'].tolist())
            comparison['common_districts'] = list(common)
            comparison['agreement'] = len(common)
        else:
            comparison['common_districts'] = []
            comparison['agreement'] = 0
        
        return comparison
    
    def summarize_outliers(self) -> Dict:
        """
        Generate summary statistics about detected outliers
        
        Returns:
            Dictionary with outlier summary
        """
        outliers = self.detect_outliers()
        
        summary = {
            'method': self.method,
            'threshold': self.threshold,
            'total_outliers': len(outliers),
            'total_records': len(self.df),
            'outlier_percentage': round(len(outliers) / len(self.df) * 100, 2) if len(self.df) > 0 else 0,
        }
        
        if len(outliers) > 0:
            summary['districts_with_outliers'] = outliers['district'].nunique()
            summary['indicators_with_outliers'] = outliers['indicator'].nunique()
            summary['outliers_by_district'] = outliers['district'].value_counts().to_dict()
            summary['outliers_by_indicator'] = outliers['indicator'].value_counts().to_dict()
            
            # Most extreme outlier
            if self.method == 'IQR':
                # Find value furthest from bounds
                outliers['distance_from_bound'] = outliers.apply(
                    lambda row: max(
                        abs(row['value'] - row['lower_bound']),
                        abs(row['value'] - row['upper_bound'])
                    ), axis=1
                )
                most_extreme = outliers.loc[outliers['distance_from_bound'].idxmax()]
            else:  # Z-score
                most_extreme = outliers.loc[outliers['z_score'].idxmax()]
            
            summary['most_extreme_outlier'] = {
                'district': most_extreme['district'],
                'indicator': most_extreme['indicator'],
                'value': most_extreme['value'],
                'month': most_extreme['month']
            }
        
        return summary


if __name__ == "__main__":
    # Test the outlier detector
    from data_loader import DataLoader
    
    print("=" * 70)
    print("OUTLIER DETECTOR TEST")
    print("=" * 70)
    
    # Load data
    loader = DataLoader("data/healthcare_data.csv")
    df = loader.load_data()
    
    print(f"\nLoaded {len(df)} records")
    
    # Test IQR method
    print("\n" + "-" * 70)
    print("IQR METHOD (threshold = 1.5)")
    print("-" * 70)
    
    detector_iqr = OutlierDetector(df, method='IQR', threshold=1.5)
    outliers_iqr = detector_iqr.detect_outliers()
    
    print(f"\nOutliers detected: {len(outliers_iqr)}")
    if len(outliers_iqr) > 0:
        display_cols = ['district', 'indicator', 'month', 'value', 'lower_bound', 'upper_bound']
        print("\n" + outliers_iqr[display_cols].to_string(index=False))
    
    # Test Z-score method
    print("\n" + "-" * 70)
    print("Z-SCORE METHOD (threshold = 3.0)")
    print("-" * 70)
    
    detector_zscore = OutlierDetector(df, method='zscore', threshold=3.0)
    outliers_zscore = detector_zscore.detect_outliers()
    
    print(f"\nOutliers detected: {len(outliers_zscore)}")
    if len(outliers_zscore) > 0:
        display_cols = ['district', 'indicator', 'month', 'value', 'mean', 'z_score']
        print("\n" + outliers_zscore[display_cols].to_string(index=False))
    
    # Summary for IQR
    print("\n" + "-" * 70)
    print("IQR SUMMARY")
    print("-" * 70)
    
    summary_iqr = detector_iqr.summarize_outliers()
    for key, value in summary_iqr.items():
        if key not in ['outliers_by_district', 'outliers_by_indicator']:
            print(f"{key}: {value}")
    
    # Summary for Z-score
    print("\n" + "-" * 70)
    print("Z-SCORE SUMMARY")
    print("-" * 70)
    
    summary_zscore = detector_zscore.summarize_outliers()
    for key, value in summary_zscore.items():
        if key not in ['outliers_by_district', 'outliers_by_indicator']:
            print(f"{key}: {value}")
    
    # Compare methods for ANC coverage
    print("\n" + "-" * 70)
    print("METHOD COMPARISON FOR ANC COVERAGE")
    print("-" * 70)
    
    comparison = detector_iqr.compare_methods('anc_coverage')
    for key, value in comparison.items():
        print(f"{key}: {value}")
    
    # Test with lower Z-score threshold (more sensitive)
    print("\n" + "=" * 70)
    print("Z-SCORE METHOD WITH LOWER THRESHOLD (2.0)")
    print("=" * 70)
    
    detector_sensitive = OutlierDetector(df, method='zscore', threshold=2.0)
    outliers_sensitive = detector_sensitive.detect_outliers()
    
    print(f"\nOutliers detected: {len(outliers_sensitive)}")
    if len(outliers_sensitive) > 0:
        display_cols = ['district', 'indicator', 'value', 'mean', 'z_score']
        print("\n" + outliers_sensitive[display_cols].to_string(index=False))
