
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def plot_oee_trend(df):
    """Create OEE trend line plot with components."""
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
    """Create metrics trend chart by month."""
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
    df['month'] = df['startOfOrder'].dt.strftime('%B %Y')
    
    # Group by month
    monthly_data = df.groupby('month').agg({
        'OEE': 'mean',
        'Availability': 'mean',
        'Performance': 'mean',
        'Quality': 'mean'
    }).reset_index()
    
    # Sort months chronologically
    monthly_data['month_sort'] = pd.to_datetime(monthly_data['month'], format='%B %Y')
    monthly_data = monthly_data.sort_values('month_sort')
    
    # Create trend chart for all metrics
    fig = go.Figure()
    
    metrics = ['OEE', 'Availability', 'Performance', 'Quality']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for metric, color in zip(metrics, colors):
        fig.add_trace(go.Scatter(
            x=monthly_data['month'],
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
            'text': f'Monthly Metrics Trend - Line: {line}, Part: {part}<br><sub>Current Month: {current_month}</sub>',
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
    """Create time-based analysis chart by production line and part."""
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
        df['period'] = df['startOfOrder'].dt.strftime('Week %W, %Y')
        period_format = "Week: %{x}<br>"
    elif time_filter == "Monthly":
        df['period'] = df['startOfOrder'].dt.strftime('%B %Y')
        period_format = "Month: %{x}<br>"
    else:  # Yearly
        df['period'] = df['startOfOrder'].dt.year
        period_format = "Year: %{x}<br>"

    # Get date range for title
    start_date = df['startOfOrder'].min().strftime('%m/%d/%Y')
    end_date = df['startOfOrder'].max().strftime('%m/%d/%Y')
    date_range = f"{start_date} to {end_date}"

    # Group by period and production line for bar chart
    grouped_data = df.groupby(['period', 'productionLine']).agg({
        'OEE': 'mean',
        'Availability': 'mean',
        'Performance': 'mean',
        'Quality': 'mean',
        'partNumber': lambda x: ', '.join(sorted(set(x)))  # Keep track of part numbers
    }).reset_index()

    fig = go.Figure()

    # For Daily analysis, display just date on x-axis
    if time_filter == "Daily":
        # Convert to string format for dates to simplify x-axis
        grouped_data['period_display'] = grouped_data['period'].astype(str)
    else:
        grouped_data['period_display'] = grouped_data['period']

    # Create separate bars per production line
    for line in sorted(grouped_data['productionLine'].unique()):
        line_data = grouped_data[grouped_data['productionLine'] == line]
        
        fig.add_trace(go.Bar(
            x=line_data['period_display'],
            y=line_data['OEE'],  # Just show OEE for simplicity
            name=f"{line}",
            hovertemplate=(
                period_format +
                "OEE: %{y:.1%}<br>"
                f"Line: {line}<br>"
                "Parts: %{customdata}"
                "<extra></extra>"
            ),
            customdata=line_data['partNumber']
        ))

    fig.update_layout(
        title={
            'text': f'{time_filter} OEE Analysis by Production Line<br><sub>{date_range}</sub>',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Date' if time_filter == "Daily" else 'Period',
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
        barmode='group'  # Group bars by date
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')

    return fig
