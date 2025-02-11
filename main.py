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
    layout="wide"
)

# Custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.title("OEE Dashboard")
    st.markdown("### Overall Equipment Effectiveness Analysis")

    # Sidebar
    st.sidebar.header("Controls")
    
    # Template download
    template_data = pd.DataFrame(columns=[
        'startOfOrder', 'plannedProductionTime', 'actualProductionTime',
        'idealCycleTime', 'totalPieces', 'goodPieces', 'plannedDowntime',
        'unplannedDowntime'
    ])
    
    template_buffer = io.BytesIO()
    template_data.to_csv(template_buffer, index=False)
    template_bytes = template_buffer.getvalue()
    
    st.sidebar.download_button(
        label="📥 Download Template",
        data=template_bytes,
        file_name="oee_template.csv",
        mime="text/csv"
    )

    # File upload
    uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=['csv'])

    if uploaded_file is not None:
        try:
            df = process_uploaded_file(uploaded_file)
            if validate_dataframe(df):
                # Time filter
                time_filter = st.sidebar.selectbox(
                    "Time Grouping",
                    ["Daily", "Weekly", "Monthly", "Yearly"]
                )

                # Calculate metrics
                df_with_metrics = calculate_oee_metrics(df)

                # Display overall metrics
                col1, col2, col3, col4 = st.columns(4)
                latest_metrics = df_with_metrics.iloc[-1]
                
                col1.metric("Overall OEE", f"{latest_metrics['OEE']:.1%}")
                col2.metric("Availability", f"{latest_metrics['Availability']:.1%}")
                col3.metric("Performance", f"{latest_metrics['Performance']:.1%}")
                col4.metric("Quality", f"{latest_metrics['Quality']:.1%}")

                # Visualizations
                st.markdown("### OEE Trend Analysis")
                st.plotly_chart(plot_oee_trend(df_with_metrics), use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Metrics Breakdown")
                    st.plotly_chart(plot_metrics_breakdown(df_with_metrics), use_container_width=True)
                
                with col2:
                    st.markdown("### Time-based Analysis")
                    st.plotly_chart(plot_time_based_analysis(df_with_metrics, time_filter), use_container_width=True)

                # Data table
                st.markdown("### Detailed Data")
                st.dataframe(df_with_metrics)

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    else:
        st.info("Please upload a CSV file to begin analysis")

if __name__ == "__main__":
    main()
