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
                
                # Group data based on time filter for KPIs
                if time_filter == "Daily":
                    df_with_metrics['period'] = df_with_metrics['startOfOrder'].dt.date
                    period_label = "Daily"
                elif time_filter == "Weekly":
                    df_with_metrics['period'] = df_with_metrics['startOfOrder'].dt.strftime('Week %W, %Y')
                    period_label = "Weekly"
                elif time_filter == "Monthly":
                    df_with_metrics['period'] = df_with_metrics['startOfOrder'].dt.strftime('%B %Y')
                    period_label = "Monthly"
                else:  # Yearly
                    df_with_metrics['period'] = df_with_metrics['startOfOrder'].dt.year
                    period_label = "Yearly"
                
                # Calculate average metrics grouped by production line and time period
                avg_metrics_by_line = df_with_metrics.groupby(['productionLine', 'period']).agg({
                    'OEE': 'mean',
                    'Availability': 'mean',
                    'Performance': 'mean',
                    'Quality': 'mean'
                }).groupby('productionLine').mean()
                
                # Calculate overall average across all lines
                overall_avg = df_with_metrics.groupby('period').agg({
                    'OEE': 'mean',
                    'Availability': 'mean',
                    'Performance': 'mean',
                    'Quality': 'mean'
                }).mean()
                
                st.markdown(f"### 📈 {period_label} Average KPIs by Production Line")
                
                # Create a dynamic grid based on number of lines plus overall
                num_lines = len(avg_metrics_by_line) + 1  # +1 for overall metrics
                cols_per_row = 4  # 4 metrics per line
                
                # Create grid layout for KPI display
                metric_rows = []
                current_row = []
                
                for i in range(num_lines * cols_per_row):
                    if i % cols_per_row == 0 and i > 0:
                        metric_rows.append(current_row)
                        current_row = []
                    current_row.append(metrics_container.container())
                
                if current_row:
                    metric_rows.append(current_row)
                
                # Display overall metrics in first row
                metric_rows[0][0].metric(
                    f"Overall {period_label} Avg OEE",
                    f"{overall_avg['OEE']:.1%}",
                    help=f"Average Overall Equipment Effectiveness across all lines ({period_label})"
                )
                metric_rows[0][1].metric(
                    f"Overall {period_label} Avg Availability",
                    f"{overall_avg['Availability']:.1%}",
                    help=f"Average Availability across all lines ({period_label})"
                )
                metric_rows[0][2].metric(
                    f"Overall {period_label} Avg Performance",
                    f"{overall_avg['Performance']:.1%}",
                    help=f"Average Performance across all lines ({period_label})"
                )
                metric_rows[0][3].metric(
                    f"Overall {period_label} Avg Quality",
                    f"{overall_avg['Quality']:.1%}",
                    help=f"Average Quality across all lines ({period_label})"
                )
                
                # Display per-line metrics in subsequent rows
                for i, (line, metrics) in enumerate(avg_metrics_by_line.iterrows(), 1):
                    row_idx = i // (cols_per_row // 4) if cols_per_row >= 4 else i
                    
                    if row_idx < len(metric_rows):
                        metric_rows[row_idx][0].metric(
                            f"{line} {period_label} Avg OEE",
                            f"{metrics['OEE']:.1%}",
                            help=f"{period_label} average OEE for {line}"
                        )
                        metric_rows[row_idx][1].metric(
                            f"{line} {period_label} Avg Availability",
                            f"{metrics['Availability']:.1%}",
                            help=f"{period_label} average Availability for {line}"
                        )
                        metric_rows[row_idx][2].metric(
                            f"{line} {period_label} Avg Performance",
                            f"{metrics['Performance']:.1%}",
                            help=f"{period_label} average Performance for {line}"
                        )
                        metric_rows[row_idx][3].metric(
                            f"{line} {period_label} Avg Quality",
                            f"{metrics['Quality']:.1%}",
                            help=f"{period_label} average Quality for {line}"
                        )

                # Visualizations
                st.markdown("### 📊 Trend Analysis")
                with st.container():
                    st.plotly_chart(plot_oee_trend(df_with_metrics), use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📉 Current Metrics")
                    
                    # Add filters for metrics breakdown
                    breakdown_line = st.selectbox(
                        "Production Line (Metrics Breakdown)",
                        options=sorted(df_with_metrics['productionLine'].unique()),
                        key="breakdown_line",
                        help="Select production line for metrics breakdown"
                    )
                    
                    breakdown_part = st.selectbox(
                        "Part Number (Metrics Breakdown)",
                        options=sorted(df_with_metrics[df_with_metrics['productionLine'] == breakdown_line]['partNumber'].unique()),
                        key="breakdown_part",
                        help="Select part number for metrics breakdown"
                    )
                    
                    # Filter metrics breakdown data
                    breakdown_df = df_with_metrics[
                        (df_with_metrics['productionLine'] == breakdown_line) &
                        (df_with_metrics['partNumber'] == breakdown_part)
                    ]
                    
                    if len(breakdown_df) > 0:
                        st.plotly_chart(plot_metrics_breakdown(breakdown_df), use_container_width=True)
                    else:
                        st.warning("No data available for the selected breakdown filters")

                with col2:
                    st.markdown(f"### 📈 {time_filter} Analysis")
                    
                    # Add date range filter for time-based analysis
                    min_date = df_with_metrics['startOfOrder'].min().date()
                    max_date = df_with_metrics['startOfOrder'].max().date()
                    
                    date_range = st.date_input(
                        "Date Range (Time Analysis)",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        help="Select date range for time analysis"
                    )
                    
                    # Handle single date selection
                    if isinstance(date_range, tuple) and len(date_range) == 2:
                        start_date, end_date = date_range
                    else:
                        start_date = end_date = date_range
                    
                    # Convert to datetime for filtering
                    start_datetime = pd.Timestamp(start_date)
                    end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                    
                    # Filter time-based analysis data
                    time_analysis_df = df_with_metrics[
                        (df_with_metrics['startOfOrder'] >= start_datetime) &
                        (df_with_metrics['startOfOrder'] <= end_datetime)
                    ]
                    
                    if len(time_analysis_df) > 0:
                        st.plotly_chart(plot_time_based_analysis(time_analysis_df, time_filter), use_container_width=True)
                    else:
                        st.warning("No data available for the selected time range")

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