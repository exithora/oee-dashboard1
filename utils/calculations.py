import pandas as pd
import numpy as np

def calculate_oee_metrics(df):
    """Calculate OEE metrics from raw data."""
    import pandas as pd
    import numpy as np
    
    # Create a copy of the dataframe to avoid warnings
    df = df.copy()
    
    # Ensure numeric columns are properly typed
    numeric_cols = ['plannedProductionTime', 'actualProductionTime', 'idealCycleTime', 
                    'totalPieces', 'goodPieces', 'plannedDowntime', 'unplannedDowntime']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate Planned Production Time (theoretical time needed)
    df.loc[:, 'plannedProductionTime'] = df['totalPieces'] * df['idealCycleTime']

    # Calculate Availability with error handling
    df.loc[:, 'Availability'] = np.where(
        df['actualProductionTime'] > 0,
        (df['plannedProductionTime'] + df['plannedDowntime']) / df['actualProductionTime'],
        0  # Handle division by zero
    )

    # Calculate Performance with error handling
    df.loc[:, 'Performance'] = np.where(
        df['actualProductionTime'] > 0,
        (df['idealCycleTime'] * df['totalPieces']) / df['actualProductionTime'],
        0  # Handle division by zero
    )

    # Calculate Quality with error handling
    df.loc[:, 'Quality'] = np.where(
        df['totalPieces'] > 0,
        df['goodPieces'] / df['totalPieces'],
        0  # Handle division by zero
    )

    # Calculate OEE
    df.loc[:, 'OEE'] = df['Availability'] * df['Performance'] * df['Quality']
    
    # Ensure all metrics are float type to prevent object dtype issues
    metric_cols = ['Availability', 'Performance', 'Quality', 'OEE']
    for col in metric_cols:
        df[col] = df[col].astype(float)

    # Clean up results
    df.loc[:, 'Availability'] = df['Availability'].clip(0, 1)
    df.loc[:, 'Performance'] = df['Performance'].clip(0, 1)
    df.loc[:, 'Quality'] = df['Quality'].clip(0, 1)
    df.loc[:, 'OEE'] = df['OEE'].clip(0, 1)

    return df

    # Ensure all metrics are float type to prevent object dtype issues
    metric_cols = ['Availability', 'Performance', 'Quality', 'OEE']
    for col in metric_cols:
        df[col] = df[col].astype(float)

    # Clean up results
    df.loc[:, 'Availability'] = df['Availability'].clip(0, 1)
    df.loc[:, 'Performance'] = df['Performance'].clip(0, 1)
    df.loc[:, 'Quality'] = df['Quality'].clip(0, 1)
    df.loc[:, 'OEE'] = df['OEE'].clip(0, 1)

    return df