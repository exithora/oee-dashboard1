import streamlit as st
import pandas as pd
from datetime import datetime
import io
from utils.calculations import calculate_oee_metrics
from utils.data_processing import process_uploaded_file, validate_dataframe
from utils.visualizations import (
    plot_oee_trend,
    plot_metrics_breakdown,
    plot_time_based_analysis,
    plot_downtime_analysis
)
import streamlit as st

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

@st.cache_data(persist="disk", show_spinner=False)
def get_filtered_data(df, lines=None, parts=None, start_date=None, end_date=None):
    df_filtered = df.copy()
    if lines:
        df_filtered = df_filtered[df_filtered['productionLine'].isin(lines)]
    if parts:
        df_filtered = df_filtered[df_filtered['partNumber'].isin(parts)]
    if start_date and end_date:
        df_filtered = df_filtered[
            (df_filtered['startOfOrder'] >= start_date) &
            (df_filtered['startOfOrder'] <= end_date)
        ]
    return df_filtered

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
               - Format: MM/DD/YYYY HH:MM or YYYY-MM-DD HH:MM:SS
               - Examples: 1/12/2025 14:12 or 2025-01-12 14:12:00

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

                #Apply filters using cached function

                try:
                    # Placeholder - replace with actual date selection logic from the original code
                    selected_start_date = "2024-01-01" #replace with actual date selection
                    selected_end_date = "2024-12-31" #replace with actual date selection

                    start_datetime = pd.to_datetime(selected_start_date)
                    end_datetime = pd.to_datetime(selected_end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

                    # Use cached filtering function
                    df_filtered = get_filtered_data(
                        df, 
                        lines=selected_lines, 
                        parts=selected_parts,
                        start_date=start_datetime,
                        end_date=end_datetime
                    )
                except Exception as e:
                    st.error(f"Filtering error: {str(e)}")
                    df_filtered = get_filtered_data(df, lines=selected_lines, parts=selected_parts)

                # Show data count for context
                st.caption(f"Displaying data for {len(df_filtered):,} records from {df_filtered['startOfOrder'].min().strftime('%m/%d/%Y')} to {df_filtered['startOfOrder'].max().strftime('%m/%d/%Y')}")

                # Calculate metrics
                df_with_metrics = calculate_oee_metrics(df_filtered)

                # Display overall metrics
                st.markdown("### 📈 Key Performance Indicators")
                metrics_container = st.container()

                # Set period label based on time filter
                if time_filter == "Daily":
                    period_label = "Daily"
                elif time_filter == "Weekly":
                    period_label = "Weekly"
                elif time_filter == "Monthly":
                    period_label = "Monthly"
                else:  # Yearly
                    period_label = "Yearly"

                # Make sure we're using numeric type before calculating mean
                # Convert each column to numeric type explicitly
                metrics_cols = ['OEE', 'Availability', 'Performance', 'Quality']
                for col in metrics_cols:
                    # Ensure numeric type
                    df_with_metrics[col] = pd.to_numeric(df_with_metrics[col], errors='coerce')
                
                # Calculate averages with proper numeric handling
                avg_metrics = {}
                for col in metrics_cols:
                    # Get mean and handle potential NaN values
                    mean_val = df_with_metrics[col].mean()
                    # Convert to float but handle NaN
                    avg_metrics[col] = 0.0 if pd.isna(mean_val) else float(mean_val)

                # Option to switch between latest and average metrics
                metric_type = st.radio(
                    "KPI Display Type:",
                    ["Latest Values", f"Average ({period_label})"],
                    horizontal=True,
                    help=f"Choose to display the most recent values or {period_label.lower()} averages"
                )

                col1, col2, col3, col4 = metrics_container.columns(4)

                if metric_type == "Latest Values":
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
                else:
                    col1.metric(
                        f"{period_label} Avg OEE",
                        f"{avg_metrics['OEE']:.1%}",
                        help=f"{period_label} average Overall Equipment Effectiveness (OEE) = Availability × Performance × Quality"
                    )
                    col2.metric(
                        f"{period_label} Avg Availability",
                        f"{avg_metrics['Availability']:.1%}",
                        help=f"{period_label} average Availability = (Planned Production Time + Planned Downtime) / Actual Production Time"
                    )
                    col3.metric(
                        f"{period_label} Avg Performance",
                        f"{avg_metrics['Performance']:.1%}",
                        help=f"{period_label} average Performance = (Ideal Cycle Time × Total Pieces) / Actual Production Time"
                    )
                    col4.metric(
                        f"{period_label} Avg Quality",
                        f"{avg_metrics['Quality']:.1%}",
                        help=f"{period_label} average Quality = Good Pieces / Total Pieces"
                    )

                # Visualizations
                st.markdown("### 📊 Trend Analysis")
                with st.container():
                    st.plotly_chart(plot_oee_trend(df_with_metrics), use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📈 Monthly Metrics Trend")

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
                    st.markdown(f"### 📊 {time_filter} OEE by Production Line")

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
                        # If only one date is selected, use it for both start and end
                        start_date = end_date = date_range

                    # Convert to datetime for filtering - handle both tuple and single date cases
                    try:
                        start_datetime = pd.Timestamp(start_date)
                        end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                    except Exception as e:
                        st.error(f"Date conversion error: {str(e)}")
                        # Fallback to using the entire date range
                        start_datetime = df_with_metrics['startOfOrder'].min()
                        end_datetime = df_with_metrics['startOfOrder'].max()

                    # Filter time-based analysis data
                    time_analysis_df = df_with_metrics[
                        (df_with_metrics['startOfOrder'] >= start_datetime) &
                        (df_with_metrics['startOfOrder'] <= end_datetime)
                    ]

                    if len(time_analysis_df) > 0:
                        st.plotly_chart(plot_time_based_analysis(time_analysis_df, time_filter), use_container_width=True)
                    else:
                        st.warning("No data available for the selected time range")

                # Downtime Analysis
                st.markdown("### ⏱️ Downtime Analysis")

                # Add date range filter for downtime analysis
                st.markdown("#### Date Range Filter for Downtime")
                downtime_min_date = df_with_metrics['startOfOrder'].min().date()
                downtime_max_date = df_with_metrics['startOfOrder'].max().date()

                downtime_date_col1, downtime_date_col2 = st.columns([1, 3])

                with downtime_date_col1:
                    use_date_filter = st.checkbox("Filter by date range", value=False, help="Enable to view downtime data for a specific date range")

                with downtime_date_col2:
                    if use_date_filter:
                        downtime_date_range = st.date_input(
                            "Select date range",
                            value=(downtime_min_date, downtime_max_date),
                            min_value=downtime_min_date,
                            max_value=downtime_max_date,
                            help="Choose date range for downtime analysis"
                        )

                        # Handle single date and date range selections
                        if isinstance(downtime_date_range, tuple) and len(downtime_date_range) == 2:
                            downtime_start_date, downtime_end_date = downtime_date_range
                        else:
                            # If only one date is selected, use it for both start and end
                            downtime_start_date = downtime_end_date = downtime_date_range
                    else:
                        downtime_start_date = downtime_end_date = None

                # Apply date range filter to downtime analysis
                st.plotly_chart(
                    plot_downtime_analysis(
                        df_with_metrics,
                        start_date=downtime_start_date if use_date_filter else None,
                        end_date=downtime_end_date if use_date_filter else None
                    ),
                    use_container_width=True
                )

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