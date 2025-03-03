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
    """Create metrics breakdown chart."""
    if len(df) == 0:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig
        
    # Use the latest data for selected line and part
    latest_data = df.iloc[-1]
    
    # Get production line and part info for title
    line = latest_data['productionLine']
    part = latest_data['partNumber']
    date_str = latest_data['startOfOrder'].strftime('%m/%d/%Y %H:%M')
    
    metrics = ['Availability', 'Performance', 'Quality']
    values = [latest_data[metric] for metric in metrics]
    colors = ['#ff7f0e', '#2ca02c', '#d62728']

    fig = go.Figure(data=[
        go.Bar(
            x=metrics,
            y=values,
            text=[f'{v:.1%}' for v in values],
            textposition='auto',
            marker_color=colors,
            hovertemplate=(
                "Metric: %{x}<br>"
                "Value: %{y:.1%}<br>"
                f"Line: {line}<br>"
                f"Part: {part}<br>"
                f"Date: {date_str}"
                "<extra></extra>"
            )
        )
    ])

    # Add OEE value as annotation
    fig.add_annotation(
        text=f"OEE: {latest_data['OEE']:.1%}",
        x=0.5,
        y=1.05,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=14, color="black"),
        bgcolor="#f0f0f0",
        bordercolor="#cccccc",
        borderwidth=1,
        borderpad=4
    )

    fig.update_layout(
        title={
            'text': f'Metrics Breakdown - Line: {line}, Part: {part}',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title='Value',
        yaxis_tickformat='.1%',
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        bargap=0.4
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

    grouped_data = df.groupby(['period', 'productionLine', 'partNumber']).agg({
        'OEE': 'mean',
        'Availability': 'mean',
        'Performance': 'mean',
        'Quality': 'mean'
    }).reset_index()

    fig = go.Figure()

    metrics = ['OEE', 'Availability', 'Performance', 'Quality']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for metric, color in zip(metrics, colors):
        fig.add_trace(go.Scatter(
            x=grouped_data['period'],
            y=grouped_data[metric],
            mode='lines+markers',
            name=metric,
            line=dict(color=color),
            hovertemplate=(
                period_format +
                f"{metric}: %{{y:.1%}}<br>"
                "Line: %{customdata[0]}<br>"
                "Part: %{customdata[1]}"
                "<extra></extra>"
            ),
            customdata=grouped_data[['productionLine', 'partNumber']]
        ))

    fig.update_layout(
        title={
            'text': f'{time_filter} Average Metrics Analysis<br><sub>{date_range}</sub>',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Period',
        yaxis_title='Average Value',
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
        height=500
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')

    return fig