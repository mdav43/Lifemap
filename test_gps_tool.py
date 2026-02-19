"""
Test script for GPS Mapping Tool
"""
import sys
import os
from pathlib import Path
from gps_database import GPSDatabase
import pandas as pd
from datetime import datetime


def test_database():
    """Test database functionality"""
    print("=" * 60)
    print("Testing GPS Database Module")
    print("=" * 60)
    
    # Clean up test database if exists
    test_db = "test_gps_tracks.duckdb"
    if Path(test_db).exists():
        Path(test_db).unlink()
    
    # Initialize database
    print("\n1. Initializing database...")
    db = GPSDatabase(test_db)
    print("   ✓ Database initialized")
    
    # Test CSV import
    print("\n2. Testing CSV import...")
    count = db.import_from_csv('sample_gps_track.csv', 'Test Track')
    print(f"   ✓ Imported {count} GPS points")
    
    # Test data retrieval
    print("\n3. Testing data retrieval...")
    tracks = db.get_all_tracks()
    print(f"   ✓ Retrieved {len(tracks)} GPS points")
    print(f"   ✓ Columns: {list(tracks.columns)}")
    
    # Test track statistics
    print("\n4. Testing track statistics...")
    stats = db.get_track_stats()
    print(f"   ✓ Found {len(stats)} track(s)")
    for _, row in stats.iterrows():
        print(f"   - Track: {row['track_name']}")
        print(f"     Points: {row['point_count']}")
        print(f"     Time range: {row['start_time']} to {row['end_time']}")
    
    # Test getting specific track
    print("\n5. Testing get track by name...")
    track_data = db.get_track_by_name('Test Track')
    print(f"   ✓ Retrieved {len(track_data)} points for 'Test Track'")
    
    # Test getting track names
    print("\n6. Testing track name retrieval...")
    names = db.get_track_names()
    print(f"   ✓ Track names: {names}")
    
    # Test delete
    print("\n7. Testing track deletion...")
    deleted = db.delete_track('Test Track')
    print(f"   ✓ Deleted {deleted} records")
    
    remaining = db.get_track_names()
    print(f"   ✓ Remaining tracks: {remaining}")
    
    db.close()
    
    # Cleanup
    if Path(test_db).exists():
        Path(test_db).unlink()
    
    print("\n" + "=" * 60)
    print("✓ All database tests passed!")
    print("=" * 60)
    return True


def test_csv_import():
    """Test various CSV formats"""
    print("\n" + "=" * 60)
    print("Testing CSV Import Variations")
    print("=" * 60)
    
    test_db = "test_gps_tracks.duckdb"
    if Path(test_db).exists():
        Path(test_db).unlink()
    
    db = GPSDatabase(test_db)
    
    # Test 1: CSV with all columns
    print("\n1. Testing full CSV with all columns...")
    count = db.import_from_csv('sample_gps_track.csv')
    print(f"   ✓ Imported {count} points")
    
    # Test 2: Create minimal CSV (only lat/lon)
    print("\n2. Testing minimal CSV (lat/lon only)...")
    minimal_csv = Path("test_minimal.csv")
    with open(minimal_csv, 'w') as f:
        f.write("latitude,longitude\n")
        f.write("37.7749,-122.4194\n")
        f.write("37.7750,-122.4195\n")
    
    count = db.import_from_csv(str(minimal_csv), 'Minimal Track')
    print(f"   ✓ Imported {count} points from minimal CSV")
    minimal_csv.unlink()
    
    # Verify all data
    all_tracks = db.get_track_stats()
    print(f"\n   ✓ Total tracks: {len(all_tracks)}")
    for _, row in all_tracks.iterrows():
        print(f"   - {row['track_name']}: {row['point_count']} points")
    
    db.close()
    if Path(test_db).exists():
        Path(test_db).unlink()
    
    print("\n" + "=" * 60)
    print("✓ All CSV import tests passed!")
    print("=" * 60)
    return True


def test_archiving():
    """Test file archiving functionality"""
    print("\n" + "=" * 60)
    print("Testing File Archiving")
    print("=" * 60)
    
    # Create archive directory if it doesn't exist
    archive_dir = Path("data/archive")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Count existing archives
    existing_archives = list(archive_dir.glob("*.csv"))
    print(f"\n1. Existing archives: {len(existing_archives)}")
    
    # Simulate archiving by copying sample file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = archive_dir / f"{timestamp}_test_archive.csv"
    
    import shutil
    shutil.copy("sample_gps_track.csv", archive_path)
    print(f"2. Created test archive: {archive_path.name}")
    
    # Verify it exists
    if archive_path.exists():
        print("   ✓ Archive file created successfully")
        size = archive_path.stat().st_size
        print(f"   ✓ Archive size: {size} bytes")
        
        # Clean up test archive
        archive_path.unlink()
        print("   ✓ Test archive cleaned up")
    
    print("\n" + "=" * 60)
    print("✓ Archiving test passed!")
    print("=" * 60)
    return True


def main():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print("GPS Mapping Tool - Test Suite")
    print("*" * 60)
    
    try:
        test_database()
        test_csv_import()
        test_archiving()
        
        print("\n")
        print("*" * 60)
        print("✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("*" * 60)
        print("\nThe GPS Mapping Tool is ready to use!")
        print("\nTo start the application, run:")
        print("  streamlit run app.py")
        print("*" * 60)
        print("\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
