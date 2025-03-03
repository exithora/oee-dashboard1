import pandas as pd
from datetime import datetime

def process_uploaded_file(uploaded_file):
    """Process and validate uploaded CSV file."""
    try:
        # Print the first few lines for debugging
        uploaded_file.seek(0)
        print("First few lines of uploaded file:")
        for i, line in enumerate(uploaded_file):
            if i < 5:
                print(f"Line {i}: {line.decode('utf-8').strip()}")
            else:
                break
        uploaded_file.seek(0)
        
        # Read CSV file, skipping comment lines that start with # and blank lines
        df = pd.read_csv(uploaded_file, comment='#', skip_blank_lines=True)
        
        # Check if headers are in data - this happens when there's a blank line at the start
        if any("Unnamed" in col for col in df.columns):
            print("Detected header row in data, attempting to fix...")
            # First row might contain the actual headers
            if "startOfOrder" in df.iloc[0, 0]:
                # Use the first row as headers and skip it in the data
                new_headers = df.iloc[0].tolist()
                df = pd.DataFrame(df.values[1:], columns=new_headers)
            
        print("DataFrame after processing:")
        print(df.head())
        print("Columns:", df.columns.tolist())
        
        # Try to convert startOfOrder with multiple format options
        try:
            if 'startOfOrder' not in df.columns:
                raise Exception(f"'startOfOrder' column not found. Available columns: {df.columns.tolist()}")
                
            # First try with explicit format MM/DD/YYYY HH:MM
            df['startOfOrder'] = pd.to_datetime(df['startOfOrder'], format='%m/%d/%Y %H:%M', errors='coerce')
            
            # If that fails, try with more flexible parsing
            if df['startOfOrder'].isna().any():
                df['startOfOrder'] = pd.to_datetime(df['startOfOrder'], errors='coerce')
        
            # Check if any dates still failed to parse
            if df['startOfOrder'].isna().any():
                raise Exception("Some dates could not be parsed. Please ensure dates are in format: MM/DD/YYYY HH:MM")
        except Exception as e:
            print(f"Date parsing error: {str(e)}")
            print("Sample data from file:", df.head())
            raise Exception(f"Error parsing dates: {str(e)}. Please ensure dates are in format: MM/DD/YYYY HH:MM")

        return df
    except Exception as e:
        print(f"Exception in process_uploaded_file: {str(e)}")
        raise Exception(f"Error reading CSV file: {str(e)}")

def validate_dataframe(df):
    """Validate the dataframe structure and data types."""
    required_columns = [
        'startOfOrder', 'productionLine', 'partNumber',
        'plannedProductionTime', 'actualProductionTime',
        'idealCycleTime', 'totalPieces', 'goodPieces',
        'plannedDowntime', 'unplannedDowntime'
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

    # Validate string columns are not empty
    string_columns = ['productionLine', 'partNumber']
    for col in string_columns:
        if df[col].isna().any() or (df[col] == '').any():
            raise Exception(f"Empty values found in column: {col}")

    return True