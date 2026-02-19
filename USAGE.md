# Lifemap Usage Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   streamlit run app.py
   ```

3. **Open in Browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to the URL shown in the terminal

## Using the GPS Mapping Tool

### Uploading GPS Tracks

1. **Prepare Your CSV File**
   - Required columns: `latitude`, `longitude`
   - Optional columns: `altitude`, `timestamp`, `speed`
   - See `sample_gps_track.csv` for an example

2. **Upload via Web Interface**
   - Click "Browse files" in the sidebar
   - Select your CSV file
   - (Optional) Enter a custom track name
   - Click "📤 Upload and Import"

3. **Automatic Processing**
   - File is validated
   - Data is imported to DuckDB database
   - Original file is archived with timestamp
   - Map visualization is updated

### Viewing Tracks

- **Map View**: Interactive Kepler.gl map showing all selected tracks
- **Track List**: View all uploaded tracks in the sidebar
- **Track Selection**: Use multiselect to choose which tracks to display
- **Track Details**: Expand track items to see statistics

### Managing Tracks

- **View Statistics**: Point count, time range, source file, upload date
- **Delete Tracks**: Click the 🗑️ button in the track details
- **View Data**: Expand "View Data" to see raw data table

### Data Storage

- **Database**: All tracks stored in `data/gps_tracks.duckdb`
- **Archive**: Original CSV files saved in `data/archive/`
- **Format**: Archive files named with timestamp: `YYYYMMDD_HHMMSS_filename.csv`

## CSV Format Examples

### Minimal Format (Required Fields Only)
```csv
latitude,longitude
37.7749,-122.4194
37.7750,-122.4195
37.7751,-122.4196
```

### Full Format (All Fields)
```csv
latitude,longitude,altitude,timestamp,speed
37.7749,-122.4194,100,2024-01-01 12:00:00,5.5
37.7750,-122.4195,105,2024-01-01 12:01:00,6.0
37.7751,-122.4196,110,2024-01-01 12:02:00,5.8
```

### Supported Timestamp Formats
- ISO 8601: `2024-01-01T12:00:00`
- Common: `2024-01-01 12:00:00`
- Date only: `2024-01-01`

## Testing

Run the test suite to verify installation:
```bash
python test_gps_tool.py
```

This will test:
- Database functionality
- CSV import with various formats
- File archiving
- Data retrieval and management

## Troubleshooting

### Spatial Extension Warning
You may see warnings about DuckDB spatial extension. This is normal and doesn't affect functionality. The tool works with or without the spatial extension.

### File Upload Issues
- Ensure CSV has `latitude` and `longitude` columns
- Check that coordinates are in decimal degrees format
- Verify file is valid CSV format

### Map Not Displaying
- Check browser console for errors
- Ensure tracks are selected in the multiselect
- Try refreshing the page

### Data Not Persisting
- Check that `data/` directory exists
- Ensure write permissions for `data/` directory
- Verify database file `data/gps_tracks.duckdb` is not locked

## Advanced Usage

### Direct Database Access

You can access the database directly using Python:

```python
from gps_database import GPSDatabase

# Open database
db = GPSDatabase('data/gps_tracks.duckdb')

# Get all tracks
tracks = db.get_all_tracks()
print(tracks)

# Get specific track
my_track = db.get_track_by_name('My Track Name')

# Get statistics
stats = db.get_track_stats()

# Close database
db.close()
```

### Batch Import

Import multiple CSV files programmatically:

```python
from gps_database import GPSDatabase
from pathlib import Path

db = GPSDatabase('data/gps_tracks.duckdb')

# Import all CSV files from a directory
for csv_file in Path('my_tracks/').glob('*.csv'):
    count = db.import_from_csv(str(csv_file))
    print(f"Imported {count} points from {csv_file.name}")

db.close()
```

### Export Data

Export tracks to CSV:

```python
from gps_database import GPSDatabase

db = GPSDatabase('data/gps_tracks.duckdb')
tracks = db.get_all_tracks()
tracks.to_csv('exported_tracks.csv', index=False)
db.close()
```

## Support

For issues or questions:
- Check the README.md for general information
- Review this usage guide for common tasks
- Run the test suite to verify installation
- Check GitHub issues for known problems

## Tips

- Upload tracks with descriptive names for easier management
- Use consistent timestamp formats across your CSV files
- Archive important tracks before deleting
- Regularly backup the `data/` directory
- Use the sample file as a template for your own tracks
