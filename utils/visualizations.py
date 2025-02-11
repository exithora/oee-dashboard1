import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def plot_oee_trend(df):
    """Create OEE trend line plot."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['startOfOrder'],
        y=df['OEE'],
        name='OEE',
        line=dict(color='#0066cc', width=2)
    ))
    
    fig.update_layout(
        title='OEE Trend Over Time',
        xaxis_title='Date',
        yaxis_title='OEE',
        yaxis_tickformat='.1%',
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def plot_metrics_breakdown(df):
    """Create metrics breakdown chart."""
    latest_data = df.iloc[-1]
    metrics = ['Availability', 'Performance', 'Quality']
    values = [latest_data[metric] for metric in metrics]
    
    fig = go.Figure(data=[
        go.Bar(
            x=metrics,
            y=values,
            text=[f'{v:.1%}' for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title='Current Metrics Breakdown',
        yaxis_title='Value',
        yaxis_tickformat='.1%',
        showlegend=False
    )
    
    return fig

def plot_time_based_analysis(df, time_filter):
    """Create time-based analysis chart."""
    df = df.copy()
    
    if time_filter == "Daily":
        df['period'] = df['startOfOrder'].dt.date
    elif time_filter == "Weekly":
        df['period'] = df['startOfOrder'].dt.isocalendar().week
    elif time_filter == "Monthly":
        df['period'] = df['startOfOrder'].dt.to_period('M')
    else:  # Yearly
        df['period'] = df['startOfOrder'].dt.year
    
    grouped_data = df.groupby('period')['OEE'].mean().reset_index()
    
    fig = go.Figure(data=[
        go.Scatter(
            x=grouped_data['period'],
            y=grouped_data['OEE'],
            mode='lines+markers',
            name='Average OEE'
        )
    ])
    
    fig.update_layout(
        title=f'{time_filter} OEE Analysis',
        xaxis_title='Period',
        yaxis_title='Average OEE',
        yaxis_tickformat='.1%',
        showlegend=True
    )
    
    return fig
