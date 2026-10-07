"""
Correlation Detection Module
Detects correlations between indicators using Pearson correlation coefficient
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from scipy import stats


class CorrelationDetector:
    """Detects correlations between healthcare indicators"""
    
    def __init__(self, df: pd.DataFrame, threshold: float = 0.70):
        """
        Initialize correlation detector
        
        Args:
            df: DataFrame with columns [month, district, indicators...]
            threshold: Minimum |correlation| to flag as significant (default 0.70)
        """
        self.df = df.copy()
        self.threshold = threshold
        self.indicators = ['anc_coverage', 'institutional_delivery', 'immunization', 'high_risk_cases']
        
        # Validate threshold
        if not 0 <= threshold <= 1:
            raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")
    
    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """
        Calculate Pearson correlation matrix for all indicators
        
        Returns:
            DataFrame with correlation coefficients between all indicator pairs
        """
        # Select only indicator columns that exist in the dataframe
        available_indicators = [ind for ind in self.indicators if ind in self.df.columns]
        
        if len(available_indicators) < 2:
            return pd.DataFrame()
        
        # Calculate correlation matrix
        correlation_matrix = self.df[available_indicators].corr(method='pearson')
        
        return correlation_matrix
    
    def get_correlation_pairs(self) -> List[Dict]:
        """
        Get all indicator pairs with their correlation coefficients
        
        Returns:
            List of dictionaries with correlation pair information
        """
        corr_matrix = self.calculate_correlation_matrix()
        
        if corr_matrix.empty:
            return []
        
        pairs = []
        indicators = corr_matrix.columns.tolist()
        
        # Iterate through upper triangle of matrix (avoid duplicates)
        for i in range(len(indicators)):
            for j in range(i + 1, len(indicators)):
                indicator1 = indicators[i]
                indicator2 = indicators[j]
                correlation = corr_matrix.loc[indicator1, indicator2]
                
                # Calculate p-value for statistical significance
                n = len(self.df)
                if n > 2:
                    # t-statistic for correlation
                    t_stat = correlation * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
                    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
                else:
                    p_value = None
                
                pairs.append({
                    'indicator1': indicator1,
                    'indicator2': indicator2,
                    'correlation': round(correlation, 4),
                    'abs_correlation': round(abs(correlation), 4),
                    'strength': self._classify_strength(correlation),
                    'direction': 'positive' if correlation > 0 else 'negative',
                    'is_significant': abs(correlation) >= self.threshold,
                    'p_value': round(p_value, 4) if p_value is not None else None,
                    'sample_size': n
                })
        
        return pairs
    
    def _classify_strength(self, correlation: float) -> str:
        """
        Classify correlation strength
        
        Args:
            correlation: Correlation coefficient
            
        Returns:
            String describing correlation strength
        """
        abs_corr = abs(correlation)
        
        if abs_corr >= 0.90:
            return 'very_strong'
        elif abs_corr >= 0.70:
            return 'strong'
        elif abs_corr >= 0.50:
            return 'moderate'
        elif abs_corr >= 0.30:
            return 'weak'
        else:
            return 'very_weak'
    
    def get_significant_correlations(self) -> List[Dict]:
        """
        Get only correlations that exceed the threshold
        
        Returns:
            List of significant correlation pairs
        """
        all_pairs = self.get_correlation_pairs()
        return [pair for pair in all_pairs if pair['is_significant']]
    
    def get_correlations_for_indicator(self, indicator: str) -> List[Dict]:
        """
        Get all correlations involving a specific indicator
        
        Args:
            indicator: Indicator name
            
        Returns:
            List of correlation pairs involving the indicator
        """
        all_pairs = self.get_correlation_pairs()
        return [
            pair for pair in all_pairs 
            if pair['indicator1'] == indicator or pair['indicator2'] == indicator
        ]
    
    def find_strongest_correlation(self) -> Dict:
        """
        Find the strongest correlation (highest |r|)
        
        Returns:
            Dictionary with strongest correlation information
        """
        pairs = self.get_correlation_pairs()
        
        if not pairs:
            return {}
        
        strongest = max(pairs, key=lambda x: x['abs_correlation'])
        return strongest
    
    def find_weakest_correlation(self) -> Dict:
        """
        Find the weakest correlation (lowest |r|)
        
        Returns:
            Dictionary with weakest correlation information
        """
        pairs = self.get_correlation_pairs()
        
        if not pairs:
            return {}
        
        weakest = min(pairs, key=lambda x: x['abs_correlation'])
        return weakest
    
    def export_correlation_matrix(self, filepath: str):
        """
        Export correlation matrix to CSV
        
        Args:
            filepath: Path to save the CSV file
        """
        corr_matrix = self.calculate_correlation_matrix()
        corr_matrix.to_csv(filepath)
        return filepath
    
    def summarize_correlations(self) -> Dict:
        """
        Generate summary statistics about correlations
        
        Returns:
            Dictionary with correlation summary
        """
        pairs = self.get_correlation_pairs()
        significant_pairs = self.get_significant_correlations()
        
        if not pairs:
            return {
                'total_pairs': 0,
                'significant_pairs': 0,
                'threshold': self.threshold,
                'sample_size': len(self.df),
                'warning': 'Not enough indicators to compute correlations'
            }
        
        summary = {
            'total_pairs': len(pairs),
            'significant_pairs': len(significant_pairs),
            'threshold': self.threshold,
            'sample_size': len(self.df),
            'indicators_analyzed': len(self.indicators),
        }
        
        # Count by strength
        strength_counts = {}
        for pair in pairs:
            strength = pair['strength']
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        summary['strength_distribution'] = strength_counts
        
        # Positive vs negative
        positive = sum(1 for p in pairs if p['direction'] == 'positive')
        negative = sum(1 for p in pairs if p['direction'] == 'negative')
        summary['positive_correlations'] = positive
        summary['negative_correlations'] = negative
        
        # Strongest and weakest
        if pairs:
            summary['strongest'] = self.find_strongest_correlation()
            summary['weakest'] = self.find_weakest_correlation()
        
        # Sample size warning
        if len(self.df) < 30:
            summary['warning'] = f'Small sample size (n={len(self.df)}). Correlations may be unstable. Recommended: n≥30'
        
        return summary
    
    def analyze_indicator_relationships(self, indicator: str) -> Dict:
        """
        Analyze all relationships for a specific indicator
        
        Args:
            indicator: Indicator to analyze
            
        Returns:
            Dictionary with relationship analysis
        """
        correlations = self.get_correlations_for_indicator(indicator)
        
        if not correlations:
            return {
                'indicator': indicator,
                'relationships': 0,
                'message': 'No correlations found'
            }
        
        # Sort by absolute correlation
        correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
        
        analysis = {
            'indicator': indicator,
            'total_relationships': len(correlations),
            'significant_relationships': sum(1 for c in correlations if c['is_significant']),
            'correlations': correlations,
        }
        
        # Identify strongest positive and negative
        positive = [c for c in correlations if c['direction'] == 'positive']
        negative = [c for c in correlations if c['direction'] == 'negative']
        
        if positive:
            analysis['strongest_positive'] = positive[0]
        if negative:
            analysis['strongest_negative'] = negative[0]
        
        return analysis


if __name__ == "__main__":
    # Test the correlation detector
    from data_loader import DataLoader
    
    print("=" * 70)
    print("CORRELATION DETECTOR TEST")
    print("=" * 70)
    
    # Load data
    loader = DataLoader("data/healthcare_data.csv")
    df = loader.load_data()
    
    print(f"\nLoaded {len(df)} records")
    print(f"Sample size note: With only {len(df)} records, correlations may be unstable")
    
    # Create correlation detector
    print("\n" + "-" * 70)
    print("CORRELATION MATRIX")
    print("-" * 70)
    
    detector = CorrelationDetector(df, threshold=0.70)
    corr_matrix = detector.calculate_correlation_matrix()
    
    print("\n" + corr_matrix.to_string())
    
    # Get all correlation pairs
    print("\n" + "-" * 70)
    print("ALL CORRELATION PAIRS")
    print("-" * 70)
    
    pairs = detector.get_correlation_pairs()
    print(f"\nTotal pairs: {len(pairs)}\n")
    
    for pair in pairs:
        print(f"{pair['indicator1']:25} <-> {pair['indicator2']:25} | "
              f"r = {pair['correlation']:6.3f} | {pair['strength']:12} | "
              f"{'✓ SIGNIFICANT' if pair['is_significant'] else ''}")
    
    # Significant correlations
    print("\n" + "-" * 70)
    print(f"SIGNIFICANT CORRELATIONS (|r| >= {detector.threshold})")
    print("-" * 70)
    
    significant = detector.get_significant_correlations()
    print(f"\nFound {len(significant)} significant correlations\n")
    
    if significant:
        for pair in significant:
            print(f"{pair['indicator1']} <-> {pair['indicator2']}")
            print(f"  Correlation: {pair['correlation']}")
            print(f"  Strength: {pair['strength']}")
            print(f"  Direction: {pair['direction']}")
            print(f"  P-value: {pair['p_value']}")
            print()
    else:
        print("No correlations exceed the threshold of 0.70")
    
    # Summary
    print("\n" + "-" * 70)
    print("CORRELATION SUMMARY")
    print("-" * 70)
    
    summary = detector.summarize_correlations()
    for key, value in summary.items():
        if key not in ['strength_distribution', 'strongest', 'weakest']:
            print(f"{key}: {value}")
    
    print(f"\nStrength distribution:")
    for strength, count in summary.get('strength_distribution', {}).items():
        print(f"  {strength}: {count}")
    
    if 'strongest' in summary:
        strongest = summary['strongest']
        print(f"\nStrongest correlation:")
        print(f"  {strongest['indicator1']} <-> {strongest['indicator2']}")
        print(f"  r = {strongest['correlation']} ({strongest['strength']})")
    
    # Analyze specific indicator
    print("\n" + "-" * 70)
    print("ANALYSIS FOR ANC_COVERAGE")
    print("-" * 70)
    
    anc_analysis = detector.analyze_indicator_relationships('anc_coverage')
    print(f"\nTotal relationships: {anc_analysis['total_relationships']}")
    print(f"Significant relationships: {anc_analysis['significant_relationships']}")
    
    print("\nAll correlations with anc_coverage:")
    for corr in anc_analysis['correlations']:
        other_indicator = corr['indicator2'] if corr['indicator1'] == 'anc_coverage' else corr['indicator1']
        print(f"  {other_indicator:25}: r = {corr['correlation']:6.3f} ({corr['strength']})")
    
    # Export matrix
    print("\n" + "-" * 70)
    print("EXPORT CORRELATION MATRIX")
    print("-" * 70)
    
    filepath = detector.export_correlation_matrix("outputs/correlation_matrix.csv")
    print(f"\n✓ Correlation matrix exported to: {filepath}")
    
    # Test with different threshold
    print("\n" + "=" * 70)
    print("TESTING WITH LOWER THRESHOLD (0.50)")
    print("=" * 70)
    
    detector_low = CorrelationDetector(df, threshold=0.50)
    significant_low = detector_low.get_significant_correlations()
    
    print(f"\nSignificant correlations with 0.50 threshold: {len(significant_low)}")
    for pair in significant_low:
        print(f"  {pair['indicator1']} <-> {pair['indicator2']}: r = {pair['correlation']}")
