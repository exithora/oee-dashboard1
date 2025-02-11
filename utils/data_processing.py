import pandas as pd
from datetime import datetime

def process_uploaded_file(uploaded_file):
    """Process and validate uploaded CSV file."""
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")

def validate_dataframe(df):
    """Validate the dataframe structure and data types."""
    required_columns = [
        'startOfOrder', 'plannedProductionTime', 'actualProductionTime',
        'idealCycleTime', 'totalPieces', 'goodPieces', 'plannedDowntime',
        'unplannedDowntime'
    ]
    
    # Check for required columns
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise Exception(f"Missing required columns: {missing_columns}")
    
    # Check for numeric columns
    numeric_columns = [
        'plannedProductionTime', 'actualProductionTime', 'idealCycleTime',
        'totalPieces', 'goodPieces', 'plannedDowntime', 'unplannedDowntime'
    ]
    
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        if df[col].isna().any():
            raise Exception(f"Invalid numeric values in column: {col}")
    
    return True
