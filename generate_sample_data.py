
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducibility
np.random.seed(42)

def generate_oee_data(num_rows=500000):
    """Generate realistic OEE data with the specified number of rows."""
    
    # Define constants
    production_lines = ['Line01', 'Line02', 'Line03', 'Line04', 'Line05']
    part_numbers = ['PN001', 'PN002', 'PN003', 'PN004', 'PN005', 'PN006', 'PN007']
    
    # Base parameters for different parts and lines
    # Format: (ideal_cycle_time, quality_base, performance_base, availability_base)
    part_params = {
        'PN001': (0.5, 0.95, 0.85, 0.90),
        'PN002': (0.6, 0.97, 0.82, 0.88),
        'PN003': (0.4, 0.93, 0.87, 0.92),
        'PN004': (0.7, 0.96, 0.83, 0.86),
        'PN005': (0.55, 0.94, 0.89, 0.91),
        'PN006': (0.65, 0.98, 0.84, 0.87),
        'PN007': (0.45, 0.92, 0.86, 0.89)
    }
    
    line_modifiers = {
        'Line01': (1.00, 1.00, 1.00, 1.00),  # Reference line
        'Line02': (0.95, 1.02, 0.98, 0.97),
        'Line03': (1.05, 0.98, 1.03, 0.96),
        'Line04': (0.98, 1.01, 0.97, 1.02),
        'Line05': (1.02, 0.99, 1.01, 0.95)
    }
    
    # Start date for the data (2 years of data)
    start_date = datetime(2023, 1, 1)
    
    # Create empty lists for each column
    data = {
        'startOfOrder': [],
        'productionLine': [],
        'partNumber': [],
        'plannedProductionTime': [],
        'actualProductionTime': [],
        'idealCycleTime': [],
        'totalPieces': [],
        'goodPieces': [],
        'plannedDowntime': [],
        'unplannedDowntime': []
    }
    
    # Generate data with daily trends, weekly patterns, and monthly seasonality
    current_date = start_date
    
    # Create a dictionary to track the last values for each line-part combination
    # This helps create more realistic trends
    last_values = {}
    
    print(f"Generating {num_rows} rows of data...")
    
    for i in range(num_rows):
        if i % 50000 == 0:
            print(f"Generated {i} rows...")
            
        # Select production line and part number
        production_line = random.choice(production_lines)
        part_number = random.choice(part_numbers)
        
        # Get base parameters for the part and line
        ideal_cycle_time_base, quality_base, performance_base, availability_base = part_params[part_number]
        cycle_mod, quality_mod, perf_mod, avail_mod = line_modifiers[production_line]
        
        # Apply modifiers
        ideal_cycle_time = ideal_cycle_time_base * cycle_mod
        
        # Get last values or initialize
        key = f"{production_line}_{part_number}"
        if key not in last_values:
            last_values[key] = {
                'quality': quality_base * quality_mod,
                'performance': performance_base * perf_mod,
                'availability': availability_base * avail_mod
            }
        
        # Add some randomness and trends
        # Daily variations
        hour_of_day = current_date.hour
        day_factor = 1.0 - 0.05 * np.sin(hour_of_day * np.pi / 12)  # Lower at night
        
        # Weekly variations
        day_of_week = current_date.weekday()
        week_factor = 1.0 - 0.03 * (day_of_week >= 5)  # Lower on weekends
        
        # Monthly variations
        day_of_month = current_date.day
        month_factor = 1.0 + 0.04 * np.sin(day_of_month * 2 * np.pi / 30)  # Cyclical
        
        # Seasonal variations
        month = current_date.month
        season_factor = 1.0 + 0.06 * np.sin((month - 1) * 2 * np.pi / 12)  # Annual cycle
        
        # Combine factors
        combined_factor = day_factor * week_factor * month_factor * season_factor
        
        # Add random trends (some consistent drift)
        trend = np.random.normal(0, 0.01)
        
        # Update values with previous + randomness + trend
        quality = min(max(last_values[key]['quality'] + np.random.normal(0, 0.015) + trend, 0.75), 0.995)
        performance = min(max(last_values[key]['performance'] + np.random.normal(0, 0.025) + trend, 0.65), 0.98)
        availability = min(max(last_values[key]['availability'] + np.random.normal(0, 0.02) + trend, 0.70), 0.97)
        
        # Apply combined factor for overall effects
        quality *= combined_factor
        performance *= combined_factor
        availability *= combined_factor
        
        # Clamp values to realistic ranges
        quality = min(max(quality, 0.75), 0.995)
        performance = min(max(performance, 0.65), 0.98)
        availability = min(max(availability, 0.70), 0.97)
        
        # Store updated values
        last_values[key]['quality'] = quality
        last_values[key]['performance'] = performance
        last_values[key]['availability'] = availability
        
        # Calculate planned variables based on the metrics
        total_pieces = int(np.random.normal(500, 100) * combined_factor)
        total_pieces = max(50, total_pieces)  # Ensure minimum pieces
        
        # Calculate good pieces based on quality
        good_pieces = int(total_pieces * quality)
        
        # Calculate planned production time (ideal)
        planned_production_time = total_pieces * ideal_cycle_time
        
        # Calculate actual production time based on availability and performance
        actual_production_time = planned_production_time / (availability * performance)
        
        # Calculate downtimes
        planned_downtime = np.random.exponential(30) * (1 - availability) * 0.3
        unplanned_downtime = np.random.exponential(45) * (1 - availability) * 0.7
        
        # Round values for realism
        planned_production_time = round(planned_production_time, 1)
        actual_production_time = round(actual_production_time, 1)
        ideal_cycle_time = round(ideal_cycle_time, 2)
        planned_downtime = round(planned_downtime, 1)
        unplanned_downtime = round(unplanned_downtime, 1)
        
        # Append data
        data['startOfOrder'].append(current_date)
        data['productionLine'].append(production_line)
        data['partNumber'].append(part_number)
        data['plannedProductionTime'].append(planned_production_time)
        data['actualProductionTime'].append(actual_production_time)
        data['idealCycleTime'].append(ideal_cycle_time)
        data['totalPieces'].append(total_pieces)
        data['goodPieces'].append(good_pieces)
        data['plannedDowntime'].append(planned_downtime)
        data['unplannedDowntime'].append(unplanned_downtime)
        
        # Increment date (more records for weekdays, fewer for weekends)
        increment = timedelta(hours=1) if day_of_week < 5 else timedelta(hours=3)
        current_date += increment
    
    # Create dataframe
    df = pd.DataFrame(data)
    
    # Sort by date
    df = df.sort_values('startOfOrder')
    
    return df

def main():
    # Generate data
    df = generate_oee_data(500000)
    
    # Save to CSV
    output_file = 'large_sample_oee_data.csv'
    print(f"Saving data to {output_file}...")
    df.to_csv(output_file, index=False)
    
    # Print basic stats
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"File generated successfully: {output_file}")
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"Number of rows: {len(df)}")
    print(f"Date range: {df['startOfOrder'].min()} to {df['startOfOrder'].max()}")
    
    # Print a few sample rows
    print("\nSample data:")
    print(df.head())

if __name__ == "__main__":
    main()
