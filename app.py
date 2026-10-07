"""
Auto-Analytics Engine - Interactive Dashboard
Streamlit UI for healthcare performance insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_loader import DataLoader
from src.insight_generator import InsightGenerator


# Page config
st.set_page_config(
    page_title="Auto-Analytics Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Light theme styling
st.markdown("""
<style>
    .main {
        background-color: #ffffff;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #e9ecef;
    }
    h1, h2, h3 {
        color: #212529;
    }
    .stAlert {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and cache data"""
    loader = DataLoader("data/healthcare_data.csv")
    df = loader.load_data()
    return df, loader


@st.cache_data
def generate_insights(df, trend_threshold, outlier_method, outlier_threshold, correlation_threshold):
    """Generate and cache insights"""
    generator = InsightGenerator(
        df,
        trend_threshold=trend_threshold,
        outlier_method=outlier_method,
        outlier_threshold=outlier_threshold,
        correlation_threshold=correlation_threshold
    )
    insights = generator.generate_all_insights()
    summary = generator.summarize_insights()
    return insights, summary, generator


def main():
    # Header
    st.title("📊 Auto-Analytics Engine")
    st.markdown("**Healthcare Performance Insights Generator**")
    st.markdown("---")
    
    # Load data
    try:
        df, loader = load_data()
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    st.sidebar.subheader("Detection Thresholds")
    trend_threshold = st.sidebar.slider(
        "Trend Threshold (%)",
        min_value=5.0,
        max_value=30.0,
        value=10.0,
        step=1.0,
        help="Minimum percentage change to flag as significant trend"
    )
    
    outlier_method = st.sidebar.selectbox(
        "Outlier Detection Method",
        options=["IQR", "zscore"],
        index=0,
        help="IQR is more robust for small samples"
    )
    
    if outlier_method == "IQR":
        outlier_threshold = st.sidebar.slider(
            "IQR Multiplier",
            min_value=1.0,
            max_value=3.0,
            value=1.5,
            step=0.1,
            help="Higher values = stricter outlier detection"
        )
    else:
        outlier_threshold = st.sidebar.slider(
            "Z-score Threshold",
            min_value=2.0,
            max_value=4.0,
            value=3.0,
            step=0.1,
            help="Standard deviations from mean"
        )
    
    correlation_threshold = st.sidebar.slider(
        "Correlation Threshold",
        min_value=0.50,
        max_value=0.95,
        value=0.70,
        step=0.05,
        help="Minimum |r| to flag as significant correlation"
    )
    
    st.sidebar.markdown("---")
    
    # Filters
    st.sidebar.subheader("🔍 Filters")
    
    available_districts = ["All"] + loader.get_available_districts()
    selected_district = st.sidebar.selectbox("District", available_districts)
    
    available_months = ["All"] + loader.get_available_months()
    selected_month = st.sidebar.selectbox("Month", available_months)
    
    available_indicators = ["All"] + loader.get_indicators()
    selected_indicator = st.sidebar.selectbox("Indicator", available_indicators)
    
    # Generate insights
    insights, summary, generator = generate_insights(
        df, trend_threshold, outlier_method, outlier_threshold, correlation_threshold
    )
    
    # Apply filters to insights
    filtered_insights = insights.copy()
    
    if selected_district != "All":
        filtered_insights = filtered_insights[filtered_insights['entity'] == selected_district]
    
    if selected_month != "All":
        filtered_insights = filtered_insights[filtered_insights['period'] == selected_month]
    
    if selected_indicator != "All":
        # For correlations, check if indicator is in the pair
        mask = filtered_insights['indicator'].str.contains(selected_indicator, na=False)
        filtered_insights = filtered_insights[mask]
    
    # Main content
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Insights",
            len(filtered_insights),
            delta=None
        )
    
    with col2:
        high_count = len(filtered_insights[filtered_insights['severity'] == 'High'])
        st.metric(
            "High Severity",
            high_count,
            delta=None,
            delta_color="inverse"
        )
    
    with col3:
        districts_analyzed = df['district'].nunique()
        st.metric(
            "Districts Analyzed",
            districts_analyzed
        )
    
    with col4:
        months_analyzed = df['month'].nunique()
        st.metric(
            "Time Periods",
            months_analyzed
        )
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Insights", "📈 Visualizations", "🔗 Correlations", "ℹ️ About"])
    
    with tab1:
        st.header("Generated Insights")
        
        if len(filtered_insights) == 0:
            st.info("No insights match the current filters. Try adjusting the thresholds or filters.")
        else:
            # Severity filter
            severity_filter = st.multiselect(
                "Filter by Severity",
                options=["High", "Medium", "Low"],
                default=["High", "Medium", "Low"]
            )
            
            # Type filter
            type_filter = st.multiselect(
                "Filter by Type",
                options=["trend", "outlier", "correlation"],
                default=["trend", "outlier", "correlation"]
            )
            
            display_insights = filtered_insights[
                (filtered_insights['severity'].isin(severity_filter)) &
                (filtered_insights['type'].isin(type_filter))
            ]
            
            st.markdown(f"**Showing {len(display_insights)} insights**")
            
            # Group by severity and display
            for severity in ["High", "Medium", "Low"]:
                sev_insights = display_insights[display_insights['severity'] == severity]
                
                if len(sev_insights) > 0:
                    if severity == "High":
                        st.error(f"🔴 **{severity} Severity** ({len(sev_insights)} insights)")
                    elif severity == "Medium":
                        st.warning(f"🟡 **{severity} Severity** ({len(sev_insights)} insights)")
                    else:
                        st.success(f"🟢 **{severity} Severity** ({len(sev_insights)} insights)")
                    
                    for _, insight in sev_insights.iterrows():
                        with st.expander(f"[{insight['insight_id']}] {insight['type'].upper()} - {insight['entity']}"):
                            st.markdown(f"**{insight['explanation']}**")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Indicator", insight['indicator'].replace('_', ' ').title())
                            with col2:
                                st.metric("Period", insight['period'])
                            with col3:
                                st.metric("Metric", insight['metric'])
    
    with tab2:
        st.header("Visualizations")
        
        if len(filtered_insights) == 0:
            st.info("No data to visualize with current filters.")
        else:
            # Severity distribution
            st.subheader("Insights by Severity")
            severity_counts = filtered_insights['severity'].value_counts()
            
            fig_severity = px.bar(
                x=severity_counts.index,
                y=severity_counts.values,
                labels={'x': 'Severity', 'y': 'Count'},
                color=severity_counts.index,
                color_discrete_map={'High': '#dc3545', 'Medium': '#ffc107', 'Low': '#28a745'}
            )
            fig_severity.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#212529')
            )
            st.plotly_chart(fig_severity, use_container_width=True)
            
            # Type distribution
            st.subheader("Insights by Type")
            type_counts = filtered_insights['type'].value_counts()
            
            fig_type = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                color_discrete_sequence=['#007bff', '#6c757d', '#17a2b8']
            )
            fig_type.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#212529')
            )
            st.plotly_chart(fig_type, use_container_width=True)
            
            # Trend lines
            st.subheader("Indicator Trends by District")
            
            # Select indicator for trend visualization
            trend_indicators = loader.get_indicators()
            selected_trend_indicator = st.selectbox(
                "Select Indicator",
                trend_indicators,
                key="trend_viz"
            )
            
            # Prepare data for line chart
            trend_data = df.copy()
            if selected_district != "All":
                trend_data = trend_data[trend_data['district'] == selected_district]
            
            fig_trend = px.line(
                trend_data,
                x='month',
                y=selected_trend_indicator,
                color='district',
                markers=True,
                labels={'month': 'Month', selected_trend_indicator: selected_trend_indicator.replace('_', ' ').title()}
            )
            fig_trend.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#212529'),
                xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
                yaxis=dict(showgrid=True, gridcolor='#e9ecef')
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab3:
        st.header("Correlation Analysis")
        
        # Generate correlation matrix
        corr_matrix = generator.correlation_detector.calculate_correlation_matrix()
        
        st.subheader("Correlation Heatmap")
        
        # Create heatmap
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=[col.replace('_', ' ').title() for col in corr_matrix.columns],
            y=[col.replace('_', ' ').title() for col in corr_matrix.columns],
            colorscale='RdBu_r',
            zmid=0,
            text=corr_matrix.values.round(3),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig_corr.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#212529'),
            height=500
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Significant correlations
        st.subheader("Significant Correlations")
        significant_corrs = generator.correlation_detector.get_significant_correlations()
        
        if len(significant_corrs) > 0:
            for corr in significant_corrs:
                direction_emoji = "📈" if corr['direction'] == 'positive' else "📉"
                st.markdown(f"{direction_emoji} **{corr['indicator1'].replace('_', ' ').title()}** ↔ "
                           f"**{corr['indicator2'].replace('_', ' ').title()}**")
                st.markdown(f"Correlation: **r = {corr['correlation']:.3f}** ({corr['strength'].replace('_', ' ')})")
                st.markdown(f"P-value: {corr['p_value']:.4f}")
                st.markdown("---")
        else:
            st.info(f"No correlations exceed the threshold of {correlation_threshold:.2f}")
        
        # Sample size warning
        if len(df) < 30:
            st.warning(f"⚠️ Small sample size (n={len(df)}). Correlations may be unstable. Recommended: n ≥ 30")
    
    with tab4:
        st.header("About This Application")
        
        st.markdown("""
        ### Auto-Analytics Engine
        
        This application automatically analyzes healthcare performance data and generates insights 
        without hardcoded logic. It combines three detection methods:
        
        **1. Trend Detection**
        - Identifies significant changes between time periods
        - Uses percentage change calculation
        - Configurable threshold for significance
        
        **2. Outlier Detection**
        - Finds unusual values compared to the group
        - Two methods: IQR (robust) and Z-score (sensitive)
        - Helps identify districts needing attention
        
        **3. Correlation Analysis**
        - Discovers relationships between indicators
        - Uses Pearson correlation coefficient
        - Identifies positive and negative associations
        
        ### How to Use
        
        1. **Adjust thresholds** in the sidebar to control sensitivity
        2. **Apply filters** to focus on specific districts, months, or indicators
        3. **Review insights** in the Insights tab, grouped by severity
        4. **Explore visualizations** to see patterns and trends
        5. **Examine correlations** to understand indicator relationships
        
        ### Severity Classification
        
        - **High**: Requires immediate attention (change > 3× threshold)
        - **Medium**: Noteworthy (change > 2× threshold)
        - **Low**: Minor but flagged (change > 1× threshold)
        
        ### Data Source
        
        The application analyzes district-level healthcare performance data including:
        - ANC Coverage
        - Institutional Delivery
        - Immunization
        - High Risk Cases
        """)
        
        st.markdown("---")
        st.info("💡 **Tip**: Lower thresholds will detect more insights but may include less significant changes.")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Auto-Analytics Engine v1.0**")
    st.sidebar.markdown("Built with Streamlit")


if __name__ == "__main__":
    main()
