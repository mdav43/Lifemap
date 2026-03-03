"""
GPS Mapping Tool - Upload and visualize GPS tracks
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static
from gps_database import GPSDatabase


# Page configuration
st.set_page_config(
    page_title="Lifemap - GPS Track Visualizer",
    page_icon="🗺️",
    layout="wide"
)

# Initialize database
@st.cache_resource
def get_database():
    """Get database connection."""
    return GPSDatabase("data/gps_tracks.duckdb")


def archive_file(uploaded_file):
    """Archive uploaded CSV file."""
    archive_dir = Path("data/archive")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = archive_dir / f"{timestamp}_{uploaded_file.name}"
    
    with open(archive_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return archive_path


def create_kepler_map(df):
    """Create Kepler.gl map from GPS data."""
    if df.empty:
        return None
    
    # Prepare data for Kepler.gl
    map_data = df[['latitude', 'longitude', 'track_name']].copy()
    
    # Add optional columns if they exist
    optional_cols = ['altitude', 'speed', 'timestamp']
    for col in optional_cols:
        if col in df.columns and df[col].notna().any():
            map_data[col] = df[col]
    
    # Create Kepler map
    config = {
        'version': 'v1',
        'config': {
            'mapState': {
                'latitude': df['latitude'].mean(),
                'longitude': df['longitude'].mean(),
                'zoom': 12
            }
        }
    }
    
    map_1 = KeplerGl(height=600, config=config)
    map_1.add_data(data=map_data, name='GPS Tracks')
    
    return map_1


def main():
    """Main application."""
    st.title("🗺️ Lifemap - GPS Track Visualizer")
    st.markdown("Upload GPS tracks in CSV format and visualize them on an interactive map")
    
    # Sidebar
    st.sidebar.header("📁 Track Management")
    
    db = get_database()
    
    # File upload section
    st.sidebar.subheader("Upload GPS Track")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="CSV file should contain 'latitude' and 'longitude' columns. Optional: 'altitude', 'timestamp', 'speed'"
    )
    
    track_name = st.sidebar.text_input(
        "Track Name (optional)",
        help="Leave empty to use filename as track name"
    )
    
    if uploaded_file is not None:
        if st.sidebar.button("📤 Upload and Import"):
            try:
                # Save uploaded file temporarily
                temp_path = Path("data/uploads") / uploaded_file.name
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Archive the file
                archive_path = archive_file(uploaded_file)
                st.sidebar.success(f"✅ Archived to: {archive_path.name}")
                
                # Import to database
                name = track_name if track_name else None
                count = db.import_from_csv(str(temp_path), name)
                
                st.sidebar.success(f"✅ Imported {count} GPS points!")
                
                # Clean up temp file
                temp_path.unlink()
                
                # Clear cache to refresh data
                st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")
    
    # Display CSV format example
    with st.sidebar.expander("📋 CSV Format Example"):
        st.code("""latitude,longitude,altitude,timestamp,speed
37.7749,-122.4194,100,2024-01-01 12:00:00,5.5
37.7750,-122.4195,105,2024-01-01 12:01:00,6.0
37.7751,-122.4196,110,2024-01-01 12:02:00,5.8""")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("📊 Track Statistics")
        
        # Get track statistics
        stats_df = db.get_track_stats()
        
        if not stats_df.empty:
            st.metric("Total Tracks", len(stats_df))
            st.metric("Total Points", stats_df['point_count'].sum())
            
            st.markdown("---")
            st.subheader("Tracks")
            
            # Display track list with selection
            track_names = db.get_track_names()
            selected_tracks = st.multiselect(
                "Select tracks to display",
                options=track_names,
                default=track_names,
                help="Select one or more tracks to visualize"
            )
            
            # Display track details
            for _, row in stats_df.iterrows():
                with st.expander(f"📍 {row['track_name']}"):
                    st.write(f"**Points:** {row['point_count']}")
                    if pd.notna(row['start_time']):
                        st.write(f"**Start:** {row['start_time']}")
                        st.write(f"**End:** {row['end_time']}")
                    st.write(f"**Source:** {row['source_file']}")
                    st.write(f"**Uploaded:** {row['uploaded_at']}")
                    
                    if st.button(f"🗑️ Delete", key=f"del_{row['track_name']}"):
                        db.delete_track(row['track_name'])
                        st.success(f"Deleted {row['track_name']}")
                        st.rerun()
        else:
            st.info("No tracks uploaded yet. Upload a CSV file to get started!")
            selected_tracks = []
    
    with col1:
        st.subheader("🗺️ Map Visualization")
        
        # Load and display selected tracks
        if selected_tracks:
            # Get data for selected tracks
            all_data = []
            for track in selected_tracks:
                track_data = db.get_track_by_name(track)
                all_data.append(track_data)
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                
                # Display data preview
                with st.expander("📄 View Data", expanded=False):
                    st.dataframe(combined_df, use_container_width=True)
                
                # Create and display Kepler map
                try:
                    kepler_map = create_kepler_map(combined_df)
                    if kepler_map:
                        keplergl_static(kepler_map, height=600)
                except Exception as e:
                    st.error(f"Error creating map: {str(e)}")
                    st.info("Displaying data table instead")
                    st.dataframe(combined_df, use_container_width=True)
        else:
            st.info("Select tracks from the sidebar to visualize them on the map")
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit, DuckDB, and Kepler.gl")


if __name__ == "__main__":
    main()
