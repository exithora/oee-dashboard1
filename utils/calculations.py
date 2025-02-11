import pandas as pd
import numpy as np

def calculate_oee_metrics(df):
    """Calculate OEE metrics from raw data."""
    # Convert date string to datetime
    df['startOfOrder'] = pd.to_datetime(df['startOfOrder'])
    
    # Calculate Availability
    df['Availability'] = (df['actualProductionTime'] - df['unplannedDowntime']) / \
                        (df['plannedProductionTime'] - df['plannedDowntime'])
    
    # Calculate Performance
    df['theoreticalOutput'] = df['actualProductionTime'] / df['idealCycleTime']
    df['Performance'] = df['totalPieces'] / df['theoreticalOutput']
    
    # Calculate Quality
    df['Quality'] = df['goodPieces'] / df['totalPieces']
    
    # Calculate OEE
    df['OEE'] = df['Availability'] * df['Performance'] * df['Quality']
    
    # Clean up results
    df['Availability'] = df['Availability'].clip(0, 1)
    df['Performance'] = df['Performance'].clip(0, 1)
    df['Quality'] = df['Quality'].clip(0, 1)
    df['OEE'] = df['OEE'].clip(0, 1)
    
    return df
