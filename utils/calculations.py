import pandas as pd
import numpy as np

def calculate_oee_metrics(df):
    """Calculate OEE metrics from raw data."""
    # Create a copy of the dataframe to avoid warnings
    df = df.copy()

    # Convert date string to datetime
    df.loc[:, 'startOfOrder'] = pd.to_datetime(df['startOfOrder'])

    # Calculate Planned Production Time (theoretical time needed)
    df.loc[:, 'plannedProductionTime'] = df['totalPieces'] * df['idealCycleTime']

    # Calculate Availability
    df.loc[:, 'Availability'] = (df['plannedProductionTime'] + df['plannedDowntime']) / df['actualProductionTime']

    # Calculate Performance
    df.loc[:, 'Performance'] = (df['idealCycleTime'] * df['totalPieces']) / df['actualProductionTime']

    # Calculate Quality
    df.loc[:, 'Quality'] = df['goodPieces'] / df['totalPieces']

    # Calculate OEE
    df.loc[:, 'OEE'] = df['Availability'] * df['Performance'] * df['Quality']

    # Clean up results
    df.loc[:, 'Availability'] = df['Availability'].clip(0, 1)
    df.loc[:, 'Performance'] = df['Performance'].clip(0, 1)
    df.loc[:, 'Quality'] = df['Quality'].clip(0, 1)
    df.loc[:, 'OEE'] = df['OEE'].clip(0, 1)

    return df