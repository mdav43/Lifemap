"""
Database module for GPS track storage using DuckDB with geospatial extensions.
"""
import duckdb
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional


class GPSDatabase:
    """Manages GPS track data in DuckDB with geospatial support."""
    
    def __init__(self, db_path: str = "gps_tracks.duckdb"):
        """
        Initialize the GPS database.
        
        Args:
            db_path: Path to the DuckDB database file
        """
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables if needed."""
        self.conn = duckdb.connect(self.db_path)
        
        # Try to install and load spatial extension
        try:
            self.conn.execute("INSTALL spatial;")
        except Exception as e:
            # Spatial extension may already be installed or network error
            print(f"Note: Spatial extension install attempted: {e}")
        
        try:
            self.conn.execute("LOAD spatial;")
        except Exception as e:
            print(f"Warning: Could not load spatial extension: {e}")
            print("Continuing without spatial indexing...")
        
        # Create GPS tracks table with geospatial support
        # Use simpler schema if spatial extension is not available
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS gps_tracks (
                    id INTEGER PRIMARY KEY,
                    track_name VARCHAR,
                    latitude DOUBLE,
                    longitude DOUBLE,
                    altitude DOUBLE,
                    timestamp TIMESTAMP,
                    speed DOUBLE,
                    uploaded_at TIMESTAMP,
                    source_file VARCHAR,
                    geom GEOMETRY
                );
            """)
            self.has_spatial = True
        except Exception:
            # Fallback without geometry column
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS gps_tracks (
                    id INTEGER PRIMARY KEY,
                    track_name VARCHAR,
                    latitude DOUBLE,
                    longitude DOUBLE,
                    altitude DOUBLE,
                    timestamp TIMESTAMP,
                    speed DOUBLE,
                    uploaded_at TIMESTAMP,
                    source_file VARCHAR
                );
            """)
            self.has_spatial = False
        
        # Create sequence for auto-incrementing IDs
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS gps_tracks_id_seq START 1;
        """)
        
        # Create index on geospatial column for faster queries if spatial is available
        if self.has_spatial:
            try:
                self.conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_gps_geom ON gps_tracks USING RTREE (geom);
                """)
            except Exception:
                # RTREE index may not be available in all DuckDB versions
                pass
    
    def import_from_csv(self, csv_path: str, track_name: Optional[str] = None) -> int:
        """
        Import GPS tracks from CSV file to DuckDB.
        
        Args:
            csv_path: Path to the CSV file
            track_name: Optional name for the track (defaults to filename)
            
        Returns:
            Number of records imported
        """
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Validate required columns
        required_cols = ['latitude', 'longitude']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV must contain columns: {required_cols}")
        
        # Set track name
        if track_name is None:
            track_name = Path(csv_path).stem
        
        # Add metadata columns
        df['track_name'] = track_name
        df['uploaded_at'] = datetime.now()
        df['source_file'] = Path(csv_path).name
        
        # Handle optional columns
        if 'altitude' not in df.columns:
            df['altitude'] = None
        if 'timestamp' not in df.columns:
            df['timestamp'] = None
        else:
            # Convert timestamp to datetime if it's a string
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        if 'speed' not in df.columns:
            df['speed'] = None
        
        # Select and order columns
        columns = ['track_name', 'latitude', 'longitude', 'altitude', 
                   'timestamp', 'speed', 'uploaded_at', 'source_file']
        df = df[columns]
        
        # Insert data into DuckDB with or without geom column
        if self.has_spatial:
            self.conn.execute("""
                INSERT INTO gps_tracks 
                SELECT 
                    nextval('gps_tracks_id_seq') as id,
                    track_name,
                    latitude,
                    longitude,
                    altitude,
                    timestamp,
                    speed,
                    uploaded_at,
                    source_file,
                    ST_Point(longitude, latitude) as geom
                FROM df
            """)
        else:
            self.conn.execute("""
                INSERT INTO gps_tracks 
                SELECT 
                    nextval('gps_tracks_id_seq') as id,
                    track_name,
                    latitude,
                    longitude,
                    altitude,
                    timestamp,
                    speed,
                    uploaded_at,
                    source_file
                FROM df
            """)
        
        return len(df)
    
    def get_all_tracks(self) -> pd.DataFrame:
        """
        Get all GPS tracks from the database.
        
        Returns:
            DataFrame with all tracks
        """
        return self.conn.execute("""
            SELECT 
                id,
                track_name,
                latitude,
                longitude,
                altitude,
                timestamp,
                speed,
                uploaded_at,
                source_file
            FROM gps_tracks
            ORDER BY uploaded_at DESC, timestamp ASC
        """).df()
    
    def get_track_by_name(self, track_name: str) -> pd.DataFrame:
        """
        Get a specific GPS track by name.
        
        Args:
            track_name: Name of the track
            
        Returns:
            DataFrame with the track data
        """
        return self.conn.execute("""
            SELECT 
                id,
                track_name,
                latitude,
                longitude,
                altitude,
                timestamp,
                speed,
                uploaded_at,
                source_file
            FROM gps_tracks
            WHERE track_name = ?
            ORDER BY timestamp ASC
        """, [track_name]).df()
    
    def get_track_names(self) -> list:
        """
        Get list of all track names.
        
        Returns:
            List of track names
        """
        result = self.conn.execute("""
            SELECT DISTINCT track_name
            FROM gps_tracks
            ORDER BY track_name
        """).df()
        return result['track_name'].tolist()
    
    def get_track_stats(self) -> pd.DataFrame:
        """
        Get statistics for all tracks.
        
        Returns:
            DataFrame with track statistics
        """
        return self.conn.execute("""
            SELECT 
                track_name,
                COUNT(*) as point_count,
                MIN(timestamp) as start_time,
                MAX(timestamp) as end_time,
                MIN(latitude) as min_lat,
                MAX(latitude) as max_lat,
                MIN(longitude) as min_lon,
                MAX(longitude) as max_lon,
                source_file,
                MAX(uploaded_at) as uploaded_at
            FROM gps_tracks
            GROUP BY track_name, source_file
            ORDER BY uploaded_at DESC
        """).df()
    
    def delete_track(self, track_name: str) -> int:
        """
        Delete a track by name.
        
        Args:
            track_name: Name of the track to delete
            
        Returns:
            Number of records deleted
        """
        result = self.conn.execute("""
            DELETE FROM gps_tracks
            WHERE track_name = ?
        """, [track_name])
        return result.fetchall()[0][0] if result else 0
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
