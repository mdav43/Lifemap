# Lifemap 🗺️

A GPS mapping tool for uploading, archiving, and visualizing GPS tracks using DuckDB geospatial database and Kepler.gl visualization.

## Quick Start

**Option 1: Use the quick start script**
```bash
./quickstart.sh
```

**Option 2: Manual setup**
```bash
pip install -r requirements.txt
python test_gps_tool.py  # Run tests
streamlit run app.py     # Start the app
```

Then open your browser at `http://localhost:8501` and upload `sample_gps_track.csv` to see it in action!

## Features

- 📤 **CSV Upload**: Upload GPS tracks from CSV files
- 🗄️ **DuckDB Storage**: Store tracks in DuckDB with geospatial extensions
- 📁 **Automatic Archiving**: Uploaded files are automatically archived with timestamps
- 🗺️ **Interactive Visualization**: View tracks on an interactive Kepler.gl map
- 📊 **Track Management**: View track statistics, select tracks to display, and delete tracks
- 🌐 **Geospatial Support**: Full geospatial indexing and querying capabilities

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mdav43/Lifemap.git
cd Lifemap
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser at `http://localhost:8501`

3. Upload a CSV file with GPS tracks:
   - Use the file uploader in the sidebar
   - Optionally provide a custom track name
   - Click "Upload and Import"

4. View and manage your tracks:
   - See track statistics in the right panel
   - Select which tracks to display on the map
   - Delete tracks you no longer need

## CSV Format

Your CSV file should contain at minimum the following columns:
- `latitude` (required): Latitude coordinate
- `longitude` (required): Longitude coordinate

Optional columns:
- `altitude`: Elevation in meters
- `timestamp`: Date and time of the GPS point (ISO format)
- `speed`: Speed in meters per second

### Example CSV:

```csv
latitude,longitude,altitude,timestamp,speed
37.7749,-122.4194,100,2024-01-01 12:00:00,5.5
37.7750,-122.4195,105,2024-01-01 12:01:00,6.0
37.7751,-122.4196,110,2024-01-01 12:02:00,5.8
```

A sample GPS track file is included: `sample_gps_track.csv`

## Architecture

### Components

1. **gps_database.py**: DuckDB database module with geospatial support
   - Manages GPS track storage
   - Provides import/export functionality
   - Handles geospatial indexing

2. **app.py**: Streamlit web application
   - User interface for upload and visualization
   - Integration with Kepler.gl for mapping
   - Track management interface

3. **Data Storage**:
   - `data/gps_tracks.duckdb`: DuckDB database file
   - `data/archive/`: Archived CSV files with timestamps
   - `data/uploads/`: Temporary upload directory

## Technology Stack

- **Streamlit**: Web application framework
- **DuckDB**: Embedded analytical database with spatial extension
- **Pandas**: Data manipulation and analysis
- **Kepler.gl**: Geospatial visualization platform
- **streamlit-keplergl**: Streamlit component for Kepler.gl

## Development

### Project Structure

```
Lifemap/
├── app.py                  # Main Streamlit application
├── gps_database.py         # DuckDB database module
├── requirements.txt        # Python dependencies
├── sample_gps_track.csv   # Sample GPS data
├── data/
│   ├── uploads/           # Temporary upload directory
│   ├── archive/           # Archived CSV files
│   └── gps_tracks.duckdb  # DuckDB database (created on first run)
└── README.md              # This file
```

### Database Schema

The `gps_tracks` table has the following structure:

```sql
CREATE TABLE gps_tracks (
    id INTEGER PRIMARY KEY,
    track_name VARCHAR,
    latitude DOUBLE,
    longitude DOUBLE,
    altitude DOUBLE,
    timestamp TIMESTAMP,
    speed DOUBLE,
    uploaded_at TIMESTAMP,
    source_file VARCHAR,
    geom GEOMETRY  -- PostGIS-style geometry column
);
```

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.