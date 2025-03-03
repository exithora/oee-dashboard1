
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import timedelta

def plot_oee_trend(df):
    """Create OEE trend line plot with components, optimized for large datasets."""
    # Sample data to reduce points for large datasets 
    if len(df) > 1000:
        # Resample data to reduce points
        df = df.sort_values('startOfOrder')
        df = df.set_index('startOfOrder')
        # Resample by day and take mean
        df_resampled = df.resample('D').mean().reset_index()
        df_resampled['productionLine'] = df['productionLine'].iloc[0]
        df_resampled['partNumber'] = df['partNumber'].iloc[0]
        df = df_resampled
    else:
        df = df.copy()
    
    fig = go.Figure()

    # Add traces for each metric
    metrics = ['OEE', 'Availability', 'Performance', 'Quality']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for metric, color in zip(metrics, colors):
        fig.add_trace(go.Scatter(
            x=df['startOfOrder'],
            y=df[metric],
            name=metric,
            line=dict(width=2, color=color),
            hovertemplate=(
                f"{metric}: %{{y:.1%}}<br>"
                "Date: %{x}<br>"
                f"Line: {df['productionLine'].iloc[0]}<br>"
                f"Part: {df['partNumber'].iloc[0]}"
                "<extra></extra>"
            )
        ))

    fig.update_layout(
        title={
            'text': 'OEE and Components Trend Over Time',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Date',
        yaxis_title='Value',
        yaxis_tickformat='.1%',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')

    return fig

def plot_metrics_breakdown(df):
    """Create metrics trend chart by month, optimized."""
    if len(df) == 0:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig
    
    # Get production line and part info for title
    line = df['productionLine'].iloc[0]
    part = df['partNumber'].iloc[0]
    
    # Add month column for grouping
    df = df.copy()
    df['month'] = df['startOfOrder'].dt.strftime('%Y-%m')  # Use YYYY-MM format for better sorting
    
    # Make sure we have numeric columns before aggregating
    metrics_list = ['OEE', 'Availability', 'Performance', 'Quality']
    for metric in metrics_list:
        # Convert to numeric explicitly
        df[metric] = pd.to_numeric(df[metric], errors='coerce')
    
    # Create aggregation dictionary
    agg_dict = {metric: 'mean' for metric in metrics_list}
    agg_dict['startOfOrder'] = 'min'  # Get first date of each month for sorting
    
    # Group by month with explicit numeric columns
    monthly_data = df.groupby('month').agg(agg_dict).reset_index()
    
    # Sort months chronologically
    monthly_data = monthly_data.sort_values('startOfOrder')
    
    # Format month display
    monthly_data['month_display'] = pd.to_datetime(monthly_data['startOfOrder']).dt.strftime('%b %Y')
    
    # Create trend chart for all metrics
    fig = go.Figure()
    
    metrics = ['OEE', 'Availability', 'Performance', 'Quality']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for metric, color in zip(metrics, colors):
        fig.add_trace(go.Scatter(
            x=monthly_data['month_display'],
            y=monthly_data[metric],
            mode='lines+markers',
            name=metric,
            line=dict(color=color, width=2),
            hovertemplate=(
                "Month: %{x}<br>"
                f"{metric}: %{{y:.1%}}<br>"
                f"Line: {line}<br>"
                f"Part: {part}"
                "<extra></extra>"
            )
        ))
    
    current_month = df['startOfOrder'].max().strftime('%B %Y')
    
    fig.update_layout(
        title={
            'text': f'Monthly Metrics Trend<br><sup>Current Month: {current_month}</sup>',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Month',
        yaxis_title='Value',
        yaxis_tickformat='.1%',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    
    return fig

def plot_time_based_analysis(df, time_filter):
    """Create time-based analysis chart, optimized for clarity."""
    if len(df) == 0:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(title="No data available for selected time range")
        return fig
        
    df = df.copy()

    # Format period based on time filter
    if time_filter == "Daily":
        df['period'] = df['startOfOrder'].dt.date
        period_format = "Date: %{x}<br>"
    elif time_filter == "Weekly":
        df['period'] = df['startOfOrder'].dt.strftime('%Y-W%W')  # Year-Week format
        period_format = "Week: %{x}<br>"
    elif time_filter == "Monthly":
        df['period'] = df['startOfOrder'].dt.strftime('%Y-%m')  # Year-Month format
        period_format = "Month: %{x}<br>"
    else:  # Yearly
        df['period'] = df['startOfOrder'].dt.year
        period_format = "Year: %{x}<br>"

    # Get date range for title
    start_date = df['startOfOrder'].min().strftime('%m/%d/%Y')
    end_date = df['startOfOrder'].max().strftime('%m/%d/%Y')
    date_range = f"{start_date} to {end_date}"

    # Group by period and production line
    grouped_data = df.groupby(['period', 'productionLine']).agg({
        'OEE': 'mean',
        'startOfOrder': 'min',  # For sorting
        'partNumber': lambda x: ', '.join(sorted(set(x)))[:30]  # Limit part numbers display
    }).reset_index()

    # Sort by date
    grouped_data = grouped_data.sort_values('startOfOrder')
    
    # Limit number of periods shown to prevent overcrowding
    if len(grouped_data['period'].unique()) > 20:
        # Get reduced set of periods by taking evenly spaced samples
        all_periods = sorted(grouped_data['period'].unique())
        
        # For yearly/monthly, take last 12
        if time_filter in ["Yearly", "Monthly"]:
            selected_periods = all_periods[-12:]
        # For weekly, take last 8 weeks
        elif time_filter == "Weekly":
            selected_periods = all_periods[-8:]
        # For daily, take 1 day per week for the last 4 weeks
        else:
            step = max(len(all_periods) // 8, 1)
            selected_periods = all_periods[-8*step::step]
            
        grouped_data = grouped_data[grouped_data['period'].isin(selected_periods)]
    
    # Handle display formatting
    if time_filter == "Daily":
        grouped_data['period_display'] = pd.to_datetime(grouped_data['period']).dt.strftime('%m/%d')
    elif time_filter == "Weekly":
        grouped_data['period_display'] = pd.to_datetime(grouped_data['startOfOrder']).dt.strftime('W%W %b')
    elif time_filter == "Monthly":
        grouped_data['period_display'] = pd.to_datetime(grouped_data['startOfOrder']).dt.strftime('%b %Y')
    else:
        grouped_data['period_display'] = grouped_data['period'].astype(str)

    # Create figure
    fig = go.Figure()

    # Get at most 6 most common production lines to avoid too many bars
    top_lines = df['productionLine'].value_counts().nlargest(6).index.tolist()
    
    # Create separate bars per production line
    for line in top_lines:
        line_data = grouped_data[grouped_data['productionLine'] == line]
        if len(line_data) > 0:
            fig.add_trace(go.Bar(
                x=line_data['period_display'],
                y=line_data['OEE'],
                name=line,
                hovertemplate=(
                    f"Line: {line}<br>" +
                    period_format.replace("%{x}", "%{customdata[0]}") +
                    "OEE: %{y:.1%}<br>" +
                    "Parts: %{customdata[1]}"
                    "<extra></extra>"
                ),
                customdata=np.column_stack((line_data['period_display'], line_data['partNumber']))
            ))

    fig.update_layout(
        title={
            'text': f'{time_filter} OEE Analysis by Production Line<br><sup>{date_range}</sup>',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Period',
        yaxis_title='OEE Value',
        yaxis_tickformat='.1%',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        barmode='group',  # Group bars by date
        bargap=0.15,      # Gap between bars
        bargroupgap=0.1   # Gap between bar groups
    )

    fig.update_xaxes(showgrid=False, tickangle=45)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')

    return fig


def plot_downtime_analysis(df, start_date=None, end_date=None):
    """Create downtime analysis visualization, optimized for clarity."""
    if len(df) == 0:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig
    
    # Create a copy to avoid modifying the original dataframe
    df = df.copy()
    
    # Filter by date range if provided
    if start_date is not None and end_date is not None:
        # Convert end_date to end of day for inclusive filtering
        end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df = df[(df['startOfOrder'] >= pd.Timestamp(start_date)) & 
                (df['startOfOrder'] <= end_datetime)]
        
        if len(df) == 0:
            # Return empty figure if no data for the selected date range
            fig = go.Figure()
            fig.update_layout(title=f"No downtime data available for {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}")
            return fig
    
    # Get date range for title
    start_date_str = df['startOfOrder'].min().strftime('%m/%d/%Y')
    end_date_str = df['startOfOrder'].max().strftime('%m/%d/%Y')
    date_range = f"{start_date_str}" if start_date_str == end_date_str else f"{start_date_str} to {end_date_str}"
    
    # Group by production line only to simplify the chart
    grouped_data = df.groupby(['productionLine']).agg({
        'plannedDowntime': 'sum',
        'unplannedDowntime': 'sum',
        'startOfOrder': 'count'  # Count records for reference
    }).reset_index()
    
    # Sort by total downtime for better visualization
    grouped_data['totalDowntime'] = grouped_data['plannedDowntime'] + grouped_data['unplannedDowntime']
    grouped_data = grouped_data.sort_values('totalDowntime', ascending=False)
    
    # Limit to top 10 lines for clarity
    if len(grouped_data) > 10:
        grouped_data = grouped_data.head(10)
    
    # Create figure with two bar traces
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=grouped_data['productionLine'],
        y=grouped_data['plannedDowntime'],
        name='Planned Downtime',
        marker_color='#2ca02c',
        hovertemplate=(
            "Line: %{x}<br>" +
            "Planned Downtime: %{y:.1f} min<br>" +
            "Records: %{customdata:,}<br>" +
            "<extra></extra>"
        ),
        customdata=grouped_data['startOfOrder']
    ))
    
    fig.add_trace(go.Bar(
        x=grouped_data['productionLine'],
        y=grouped_data['unplannedDowntime'],
        name='Unplanned Downtime',
        marker_color='#d62728',
        hovertemplate=(
            "Line: %{x}<br>" +
            "Unplanned Downtime: %{y:.1f} min<br>" +
            "Records: %{customdata:,}<br>" +
            "<extra></extra>"
        ),
        customdata=grouped_data['startOfOrder']
    ))
    
    # Create title based on filter status
    title_text = 'Downtime Analysis by Production Line'
    title_text += f'<br><sup>{date_range}</sup>'
    
    fig.update_layout(
        title={
            'text': title_text,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Production Line',
        yaxis_title='Downtime (minutes)',
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500
    )
    
    fig.update_xaxes(showgrid=False, tickangle=45 if len(grouped_data) > 5 else 0)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    
    return fig
