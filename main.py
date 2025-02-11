import streamlit as st
import pandas as pd
from datetime import datetime
import io
from utils.calculations import calculate_oee_metrics
from utils.data_processing import process_uploaded_file, validate_dataframe
from utils.visualizations import (
    plot_oee_trend,
    plot_metrics_breakdown,
    plot_time_based_analysis
)

# Page configuration
st.set_page_config(
    page_title="OEE Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    # Header
    st.title("📊 OEE Dashboard")
    st.markdown("""
    ### Overall Equipment Effectiveness Analysis
    Monitor and analyze your equipment's effectiveness with real-time metrics and visualizations.
    Track Availability, Performance, and Quality to optimize your production process.
    """)

    # Sidebar
    with st.sidebar:
        st.header("📱 Controls")

        # Help section
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            1. Download the template CSV file
            2. Fill in your production data
            3. Upload your completed CSV file
            4. Use the time filter to analyze trends
            """)

        # Template download
        st.subheader("📥 Download Template")
        template_data = pd.DataFrame(columns=[
            'startOfOrder', 'plannedProductionTime', 'actualProductionTime',
            'idealCycleTime', 'totalPieces', 'goodPieces', 'plannedDowntime',
            'unplannedDowntime'
        ])

        template_buffer = io.BytesIO()
        template_data.to_csv(template_buffer, index=False)
        template_bytes = template_buffer.getvalue()

        st.download_button(
            label="Download CSV Template",
            data=template_bytes,
            file_name="oee_template.csv",
            mime="text/csv",
            help="Download a template CSV file with the required columns"
        )

        # File upload
        st.subheader("📤 Upload Data")
        uploaded_file = st.file_uploader(
            "Upload your CSV file",
            type=['csv'],
            help="Upload a CSV file with your production data"
        )

    if uploaded_file is not None:
        try:
            df = process_uploaded_file(uploaded_file)
            if validate_dataframe(df):
                # Time filter
                time_filter = st.selectbox(
                    "🕒 Select Time Period",
                    ["Daily", "Weekly", "Monthly", "Yearly"],
                    help="Choose how to group the data for analysis"
                )

                # Calculate metrics
                df_with_metrics = calculate_oee_metrics(df)

                # Display overall metrics
                st.markdown("### 📈 Key Performance Indicators")
                metrics_container = st.container()
                col1, col2, col3, col4 = metrics_container.columns(4)

                latest_metrics = df_with_metrics.iloc[-1]

                col1.metric(
                    "Overall OEE",
                    f"{latest_metrics['OEE']:.1%}",
                    help="Overall Equipment Effectiveness (OEE) = Availability × Performance × Quality"
                )
                col2.metric(
                    "Availability",
                    f"{latest_metrics['Availability']:.1%}",
                    help="Availability = (Planned Production Time + Planned Downtime) / Actual Production Time"
                )
                col3.metric(
                    "Performance",
                    f"{latest_metrics['Performance']:.1%}",
                    help="Performance = (Ideal Cycle Time × Total Pieces) / Actual Production Time"
                )
                col4.metric(
                    "Quality",
                    f"{latest_metrics['Quality']:.1%}",
                    help="Quality = Good Pieces / Total Pieces"
                )

                # Visualizations
                st.markdown("### 📊 Trend Analysis")
                with st.container():
                    st.plotly_chart(plot_oee_trend(df_with_metrics), use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📉 Current Metrics")
                    st.plotly_chart(plot_metrics_breakdown(df_with_metrics), use_container_width=True)

                with col2:
                    st.markdown(f"### 📈 {time_filter} Analysis")
                    st.plotly_chart(plot_time_based_analysis(df_with_metrics, time_filter), use_container_width=True)

                # Data table
                with st.expander("🔍 View Detailed Data"):
                    st.dataframe(
                        df_with_metrics.style.format({
                            'OEE': '{:.1%}',
                            'Availability': '{:.1%}',
                            'Performance': '{:.1%}',
                            'Quality': '{:.1%}'
                        }),
                        use_container_width=True
                    )

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    else:
        # Welcome message
        st.info("""
        👋 Welcome to the OEE Dashboard!

        To get started:
        1. Download the template CSV from the sidebar
        2. Fill it with your production data
        3. Upload your completed CSV file

        The dashboard will automatically generate visualizations and insights from your data.
        """)

if __name__ == "__main__":
    main()