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
    Track Availability, Performance, and Quality across production lines and parts.
    """)

    # Sidebar
    with st.sidebar:
        st.header("📱 Controls")

        # Help section
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            #### Data Format Requirements:
            Your CSV file should contain the following columns with specified formats:

            1. **startOfOrder** (Date & Time)
               - Format: MM/DD/YYYY HH:MM
               - Example: 1/12/2025 14:12

            2. **productionLine** (Text)
               - Unique identifier for production line
               - Example: Line01, Line02

            3. **partNumber** (Text)
               - Unique identifier for parts
               - Example: PN001, PN002

            4. **plannedProductionTime** (Number)
               - Theoretical time needed in minutes
               - Example: 375.5

            5. **actualProductionTime** (Number)
               - Actual production time in minutes
               - Example: 471.0

            6. **idealCycleTime** (Number)
               - Standard time to produce one piece in minutes
               - Example: 0.5

            7. **totalPieces** (Whole Number)
               - Total pieces produced
               - Example: 751

            8. **goodPieces** (Whole Number)
               - Pieces passing quality check
               - Example: 698

            9. **plannedDowntime** (Number)
               - Scheduled stops in minutes
               - Example: 35.0

            10. **unplannedDowntime** (Number)
                - Unexpected stops in minutes
                - Example: 60.5

            #### Steps to Use:
            1. Download the template CSV file
            2. Fill in your production data following the format
            3. Upload your completed CSV file
            4. Use the filters to analyze specific lines and parts
            """)

        # Template download
        st.subheader("📥 Download Template")
        st.markdown("""
        Download our CSV template with sample data and format instructions.
        The template includes comments explaining each column's required format.
        """)

        template_data = pd.DataFrame(columns=[
            'startOfOrder', 'productionLine', 'partNumber',
            'plannedProductionTime', 'actualProductionTime',
            'idealCycleTime', 'totalPieces', 'goodPieces',
            'plannedDowntime', 'unplannedDowntime'
        ])

        # Read the template file with comments
        with open('templates/sample_template.csv', 'r') as f:
            template_content = f.read()

        st.download_button(
            label="Download CSV Template",
            data=template_content,
            file_name="oee_template.csv",
            mime="text/csv",
            help="Download a template CSV file with format instructions and sample data"
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
                # Filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    selected_lines = st.multiselect(
                        "🏭 Production Lines",
                        options=sorted(df['productionLine'].unique()),
                        default=sorted(df['productionLine'].unique()),
                        help="Select production lines to analyze"
                    )

                with col2:
                    selected_parts = st.multiselect(
                        "📦 Part Numbers",
                        options=sorted(df['partNumber'].unique()),
                        default=sorted(df['partNumber'].unique()),
                        help="Select part numbers to analyze"
                    )

                with col3:
                    time_filter = st.selectbox(
                        "🕒 Time Period",
                        ["Daily", "Weekly", "Monthly", "Yearly"],
                        help="Choose how to group the data for analysis"
                    )

                # Filter data
                filtered_df = df[
                    df['productionLine'].isin(selected_lines) &
                    df['partNumber'].isin(selected_parts)
                ]

                if len(filtered_df) == 0:
                    st.warning("No data available for the selected filters")
                    return

                # Calculate metrics
                df_with_metrics = calculate_oee_metrics(filtered_df)

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
                    display_cols = [
                        'startOfOrder', 'productionLine', 'partNumber',
                        'OEE', 'Availability', 'Performance', 'Quality',
                        'plannedProductionTime', 'actualProductionTime',
                        'totalPieces', 'goodPieces'
                    ]

                    st.dataframe(
                        df_with_metrics[display_cols].style.format({
                            'OEE': '{:.1%}',
                            'Availability': '{:.1%}',
                            'Performance': '{:.1%}',
                            'Quality': '{:.1%}',
                            'plannedProductionTime': '{:.1f}',
                            'actualProductionTime': '{:.1f}',
                            'totalPieces': '{:,.0f}',
                            'goodPieces': '{:,.0f}'
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