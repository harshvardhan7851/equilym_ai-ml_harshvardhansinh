"""
Automated Insight Generation Module
Combines trend, outlier, and correlation detections into human-readable insights
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime

from src.trend_detector import TrendDetector
from src.outlier_detector import OutlierDetector
from src.correlation_detector import CorrelationDetector


class InsightGenerator:
    """Generates automated insights from healthcare data"""
    
    def __init__(self, df: pd.DataFrame, 
                 trend_threshold: float = 10.0,
                 outlier_method: str = 'IQR',
                 outlier_threshold: float = 1.5,
                 correlation_threshold: float = 0.70):
        """
        Initialize insight generator
        
        Args:
            df: DataFrame with healthcare data
            trend_threshold: Threshold for significant trends (default 10%)
            outlier_method: Method for outlier detection ('IQR' or 'zscore')
            outlier_threshold: Threshold for outlier detection
            correlation_threshold: Threshold for significant correlations
        """
        self.df = df.copy()
        
        # Initialize detectors
        self.trend_detector = TrendDetector(df, threshold=trend_threshold)
        self.outlier_detector = OutlierDetector(df, method=outlier_method, threshold=outlier_threshold)
        self.correlation_detector = CorrelationDetector(df, threshold=correlation_threshold)
        
        self.insight_counter = 0
    
    def _generate_insight_id(self) -> str:
        """Generate unique insight ID"""
        self.insight_counter += 1
        return f"INS-{self.insight_counter:04d}"
    
    def _calculate_severity(self, insight_type: str, metric_value: float, 
                           threshold: float) -> str:
        """
        Calculate severity level based on data-driven rules
        
        Args:
            insight_type: Type of insight ('trend', 'outlier', 'correlation')
            metric_value: The metric value (e.g., percentage change, z-score)
            threshold: The threshold used for detection
            
        Returns:
            'Low', 'Medium', or 'High'
        """
        if insight_type == 'trend':
            # Based on multiples of threshold
            abs_value = abs(metric_value)
            if abs_value >= threshold * 3:
                return 'High'
            elif abs_value >= threshold * 2:
                return 'Medium'
            else:
                return 'Low'
        
        elif insight_type == 'outlier':
            # Based on distance from bounds (for IQR) or z-score magnitude
            abs_value = abs(metric_value)
            if abs_value >= threshold * 3:
                return 'High'
            elif abs_value >= threshold * 2:
                return 'Medium'
            else:
                return 'Low'
        
        elif insight_type == 'correlation':
            # Based on absolute correlation strength
            abs_value = abs(metric_value)
            if abs_value >= 0.90:
                return 'High'
            elif abs_value >= 0.80:
                return 'Medium'
            else:
                return 'Low'
        
        else:
            return 'Medium'
    
    def generate_trend_insights(self) -> List[Dict]:
        """Generate insights from trend detection"""
        insights = []
        
        significant_trends = self.trend_detector.get_significant_trends()
        
        for _, trend in significant_trends.iterrows():
            insight_id = self._generate_insight_id()
            
            # Calculate severity
            severity = self._calculate_severity('trend', trend['change_pct'], 
                                               self.trend_detector.threshold)
            
            # Format indicator name for display
            indicator_display = trend['indicator'].replace('_', ' ').title()
            
            # Generate explanation
            direction = "increased" if trend['change_pct'] > 0 else "dropped"
            explanation = (
                f"{indicator_display} in {trend['district']} {direction} by "
                f"{abs(trend['change_pct']):.1f}% compared to the previous month, "
                f"exceeding the {self.trend_detector.threshold}% significant-change threshold."
            )
            
            insights.append({
                'insight_id': insight_id,
                'type': 'trend',
                'indicator': trend['indicator'],
                'entity': trend['district'],
                'period': trend['period'].strftime('%Y-%m-%d'),
                'value': trend['current_value'],
                'prev_value': trend['previous_value'],
                'change_pct': round(trend['change_pct'], 2),
                'metric': f"{trend['change_pct']:.1f}%",
                'severity': severity,
                'explanation': explanation
            })
        
        return insights
    
    def generate_outlier_insights(self) -> List[Dict]:
        """Generate insights from outlier detection"""
        insights = []
        
        outliers = self.outlier_detector.detect_outliers()
        
        for _, outlier in outliers.iterrows():
            insight_id = self._generate_insight_id()
            
            # Format indicator name
            indicator_display = outlier['indicator'].replace('_', ' ').title()
            
            # Calculate metric and severity based on method
            if outlier['method'] == 'IQR':
                # Calculate distance from bounds
                if outlier['value'] < outlier['lower_bound']:
                    distance = outlier['lower_bound'] - outlier['value']
                    bound_desc = "below the lower bound"
                else:
                    distance = outlier['value'] - outlier['upper_bound']
                    bound_desc = "above the upper bound"
                
                metric_value = distance / outlier['IQR'] if outlier['IQR'] > 0 else 0
                severity = self._calculate_severity('outlier', metric_value, 
                                                   self.outlier_detector.threshold)
                
                # Calculate state mean for context
                state_mean = self.df[outlier['indicator']].mean()
                deviation = ((outlier['value'] - state_mean) / state_mean * 100) if state_mean != 0 else 0
                
                explanation = (
                    f"{outlier['district']}'s {indicator_display} of {outlier['value']} "
                    f"is {abs(deviation):.1f}% {'below' if deviation < 0 else 'above'} "
                    f"the state mean ({state_mean:.1f}), flagged as an outlier "
                    f"({bound_desc} by {distance:.1f} units)."
                )
                
                metric = f"{deviation:.1f}% from mean"
                
            else:  # Z-score
                z_score = outlier['z_score']
                severity = self._calculate_severity('outlier', z_score, 
                                                   self.outlier_detector.threshold)
                
                explanation = (
                    f"{outlier['district']}'s {indicator_display} of {outlier['value']} "
                    f"is {abs(z_score):.2f} standard deviations "
                    f"{'below' if outlier['value'] < outlier['mean'] else 'above'} "
                    f"the state mean ({outlier['mean']:.1f}), flagged as a statistical outlier."
                )
                
                metric = f"Z-score: {z_score:.2f}"
            
            insights.append({
                'insight_id': insight_id,
                'type': 'outlier',
                'indicator': outlier['indicator'],
                'entity': outlier['district'],
                'period': outlier['month'].strftime('%Y-%m-%d'),
                'value': outlier['value'],
                'prev_value': None,
                'change_pct': None,
                'metric': metric,
                'severity': severity,
                'explanation': explanation
            })
        
        return insights
    
    def generate_correlation_insights(self) -> List[Dict]:
        """Generate insights from correlation detection"""
        insights = []
        
        significant_correlations = self.correlation_detector.get_significant_correlations()
        
        for corr in significant_correlations:
            insight_id = self._generate_insight_id()
            
            # Calculate severity
            severity = self._calculate_severity('correlation', corr['correlation'], 
                                               self.correlation_detector.threshold)
            
            # Format indicator names
            ind1_display = corr['indicator1'].replace('_', ' ').title()
            ind2_display = corr['indicator2'].replace('_', ' ').title()
            
            # Generate explanation
            direction_word = "positive" if corr['direction'] == 'positive' else "negative"
            strength_word = corr['strength'].replace('_', ' ')
            
            if corr['direction'] == 'positive':
                relationship = f"when {ind1_display} increases, {ind2_display} also tends to increase"
            else:
                relationship = f"when {ind1_display} increases, {ind2_display} tends to decrease"
            
            explanation = (
                f"A {strength_word} {direction_word} correlation (r={corr['correlation']:.3f}) "
                f"detected between {ind1_display} and {ind2_display}: {relationship}. "
                f"This relationship is statistically significant (p={corr['p_value']:.4f})."
            )
            
            # Use first occurrence from data for period
            period = self.df['month'].max().strftime('%Y-%m-%d')
            
            insights.append({
                'insight_id': insight_id,
                'type': 'correlation',
                'indicator': f"{corr['indicator1']}:{corr['indicator2']}",
                'entity': 'State-wide',
                'period': period,
                'value': corr['correlation'],
                'prev_value': None,
                'change_pct': None,
                'metric': f"r={corr['correlation']:.3f}",
                'severity': severity,
                'explanation': explanation
            })
        
        return insights
    
    def generate_all_insights(self) -> pd.DataFrame:
        """
        Generate all insights (trends, outliers, correlations)
        
        Returns:
            DataFrame with all insights
        """
        all_insights = []
        
        # Generate insights from each detector
        trend_insights = self.generate_trend_insights()
        outlier_insights = self.generate_outlier_insights()
        correlation_insights = self.generate_correlation_insights()
        
        # Combine all insights
        all_insights.extend(trend_insights)
        all_insights.extend(outlier_insights)
        all_insights.extend(correlation_insights)
        
        # Convert to DataFrame
        insights_df = pd.DataFrame(all_insights)
        
        # Ensure consistent column order
        if len(insights_df) > 0:
            column_order = ['insight_id', 'type', 'indicator', 'entity', 'period', 
                          'value', 'prev_value', 'change_pct', 'metric', 'severity', 
                          'explanation']
            insights_df = insights_df[column_order]
        
        return insights_df
    
    def export_insights(self, filepath: str) -> str:
        """
        Export insights to CSV
        
        Args:
            filepath: Path to save CSV file
            
        Returns:
            Path to saved file
        """
        insights = self.generate_all_insights()
        insights.to_csv(filepath, index=False)
        return filepath
    
    def get_insights_by_severity(self, severity: str) -> pd.DataFrame:
        """Get insights filtered by severity level"""
        insights = self.generate_all_insights()
        if len(insights) == 0:
            return insights
        return insights[insights['severity'] == severity]
    
    def get_insights_by_type(self, insight_type: str) -> pd.DataFrame:
        """Get insights filtered by type"""
        insights = self.generate_all_insights()
        if len(insights) == 0:
            return insights
        return insights[insights['type'] == insight_type]
    
    def get_insights_by_entity(self, entity: str) -> pd.DataFrame:
        """Get insights for a specific district"""
        insights = self.generate_all_insights()
        if len(insights) == 0:
            return insights
        return insights[insights['entity'] == entity]
    
    def summarize_insights(self) -> Dict:
        """Generate summary of all insights"""
        insights = self.generate_all_insights()
        
        if len(insights) == 0:
            return {
                'total_insights': 0,
                'message': 'No insights generated'
            }
        
        summary = {
            'total_insights': len(insights),
            'by_type': insights['type'].value_counts().to_dict(),
            'by_severity': insights['severity'].value_counts().to_dict(),
            'unique_entities': insights['entity'].nunique(),
            'unique_indicators': insights['indicator'].nunique(),
        }
        
        # High severity insights
        high_severity = insights[insights['severity'] == 'High']
        if len(high_severity) > 0:
            summary['high_severity_count'] = len(high_severity)
            summary['high_severity_insights'] = high_severity[['insight_id', 'type', 'entity', 'explanation']].to_dict('records')
        
        return summary


if __name__ == "__main__":
    # Test the insight generator
    import sys
    sys.path.append('.')
    from src.data_loader import DataLoader
    
    print("=" * 80)
    print("INSIGHT GENERATOR TEST")
    print("=" * 80)
    
    # Load data
    loader = DataLoader("data/healthcare_data.csv")
    df = loader.load_data()
    
    print(f"\nLoaded {len(df)} records")
    
    # Create insight generator
    print("\n" + "-" * 80)
    print("GENERATING INSIGHTS")
    print("-" * 80)
    
    generator = InsightGenerator(
        df,
        trend_threshold=10.0,
        outlier_method='IQR',
        outlier_threshold=1.5,
        correlation_threshold=0.70
    )
    
    # Generate all insights
    insights = generator.generate_all_insights()
    
    print(f"\nTotal insights generated: {len(insights)}")
    
    # Display insights by type
    print("\n" + "-" * 80)
    print("INSIGHTS BY TYPE")
    print("-" * 80)
    
    for insight_type in insights['type'].unique():
        type_insights = insights[insights['type'] == insight_type]
        print(f"\n{insight_type.upper()} ({len(type_insights)} insights):")
        print(type_insights[['insight_id', 'entity', 'metric', 'severity']].to_string(index=False))
    
    # Display insights by severity
    print("\n" + "-" * 80)
    print("INSIGHTS BY SEVERITY")
    print("-" * 80)
    
    for severity in ['High', 'Medium', 'Low']:
        sev_insights = insights[insights['severity'] == severity]
        if len(sev_insights) > 0:
            print(f"\n{severity.upper()} SEVERITY ({len(sev_insights)} insights):")
            for _, insight in sev_insights.iterrows():
                print(f"\n[{insight['insight_id']}] {insight['type'].upper()}")
                print(f"  {insight['explanation']}")
    
    # Export insights
    print("\n" + "-" * 80)
    print("EXPORT INSIGHTS")
    print("-" * 80)
    
    filepath = generator.export_insights("outputs/insights.csv")
    print(f"\n✓ Insights exported to: {filepath}")
    
    # Summary
    print("\n" + "-" * 80)
    print("INSIGHT SUMMARY")
    print("-" * 80)
    
    summary = generator.summarize_insights()
    print(f"\nTotal insights: {summary['total_insights']}")
    print(f"\nBy type:")
    for itype, count in summary['by_type'].items():
        print(f"  {itype}: {count}")
    print(f"\nBy severity:")
    for sev, count in summary['by_severity'].items():
        print(f"  {sev}: {count}")
    
    if 'high_severity_count' in summary:
        print(f"\n⚠ {summary['high_severity_count']} HIGH SEVERITY insights require immediate attention!")
