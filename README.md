# OEE Dashboard

A comprehensive Streamlit-based Overall Equipment Effectiveness (OEE) dashboard for manufacturing analytics, featuring interactive visualizations and advanced data processing capabilities.

## Features

- Interactive OEE metric calculations
- Production line and part number tracking
- Real-time data visualization
- Customizable time period analysis
- CSV data handling and processing
- Responsive design with modern UI

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/oee-dashboard.git
cd oee-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run main.py
```

## Data Format

The dashboard accepts CSV files with the following columns:

1. **startOfOrder**: Date and time (Format: MM/DD/YYYY HH:MM)
2. **productionLine**: Production line identifier
3. **partNumber**: Part number being produced
4. **plannedProductionTime**: Theoretical time needed (minutes)
5. **actualProductionTime**: Actual production time (minutes)
6. **idealCycleTime**: Standard time per piece (minutes)
7. **totalPieces**: Total pieces produced
8. **goodPieces**: Quality-passing pieces
9. **plannedDowntime**: Scheduled stops (minutes)
10. **unplannedDowntime**: Unexpected stops (minutes)

## Usage

1. Download the template CSV from the dashboard
2. Fill in your production data following the format
3. Upload your completed CSV file
4. Use the filters to analyze specific lines and parts
5. View insights through interactive visualizations

## License

This project is licensed under the MIT License - see the LICENSE file for details.
