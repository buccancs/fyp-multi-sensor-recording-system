#!/usr/bin/env python3
"""
Data Management Example Script

This script demonstrates how to use the data management system including:
- Creating properly named sessions
- Validating data against schemas  
- Using standardized file naming
- Accessing session information

Usage:
    python examples/data_management_example.py
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add the source directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'PythonApp', 'src'))

def demonstrate_session_creation():
    """Demonstrate creating sessions with proper naming."""
    print("=== Session Creation Example ===")
    
    from session.session_manager import SessionManager
    
    # Create session manager
    manager = SessionManager("example_recordings")
    
    # Test session name validation
    print("\n1. Testing session name validation:")
    test_names = [
        "experiment_A",           # Valid
        "pilot study 2025",       # Valid (spaces allowed)
        "test-run-1",            # Valid (hyphens allowed)  
        "invalid/name",          # Invalid (slash not allowed)
        "way_too_long_session_name_that_exceeds_reasonable_limits_for_filesystem_compatibility",  # Too long
        "",                      # Empty
        "valid_name_123"         # Valid
    ]
    
    for name in test_names:
        is_valid = SessionManager.validate_session_name(name)
        print(f"  '{name}' -> {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    # Create example sessions
    print("\n2. Creating example sessions:")
    
    # Default session
    session1 = manager.create_session()
    print(f"  Default session: {session1['session_id']}")
    
    # Named session
    session2 = manager.create_session("data_collection_pilot")
    print(f"  Named session: {session2['session_id']}")
    
    # Session with spaces (will be sanitized)
    session3 = manager.create_session("User Study Phase 1")
    print(f"  Sanitized session: {session3['session_id']}")
    
    # Clean up example sessions
    manager.end_session()
    
    return [session1, session2, session3]


def demonstrate_file_naming():
    """Demonstrate standardized file naming."""
    print("\n=== File Naming Example ===")
    
    from session.session_manager import SessionManager
    
    timestamp = datetime(2025, 7, 31, 14, 30, 22)
    
    print("1. Device file naming examples:")
    examples = [
        ("phone_1", "rgb", "mp4"),
        ("phone_1", "thermal", "mp4"), 
        ("phone_2", "gsr", "csv"),
        ("webcam_1", "video", "mp4"),
        ("shimmer_01", "motion", "csv")
    ]
    
    for device_id, file_type, extension in examples:
        filename = SessionManager.generate_device_filename(
            device_id, file_type, extension, timestamp
        )
        print(f"  {device_id} {file_type} -> {filename}")


def demonstrate_data_validation():
    """Demonstrate data validation using schemas."""
    print("\n=== Data Validation Example ===")
    
    # Import validation tools
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
    
    try:
        from validate_data_schemas import DataSchemaValidator
        
        print("1. Loading schemas:")
        validator = DataSchemaValidator("docs/schemas")
        
        print("\n2. Finding existing sessions:")
        sessions = validator.find_all_sessions("PythonApp/recordings")
        calib_sessions = validator.find_all_calibration_sessions("calibration_data")
        
        print(f"  Found {len(sessions)} recording sessions")
        print(f"  Found {len(calib_sessions)} calibration sessions")
        
        # Validate a session if available
        if calib_sessions:
            print(f"\n3. Validating calibration session: {calib_sessions[0].name}")
            result = validator.validate_calibration_session(str(calib_sessions[0]))
            print(f"  Valid: {'✓' if result['valid'] else '✗'}")
            print(f"  Files checked: {result['files_checked']}")
            if result['errors']:
                for error in result['errors']:
                    print(f"  Error: {error}")
        
    except ImportError as e:
        print(f"  Could not import validation tools: {e}")
        print("  Run from project root directory")


def demonstrate_session_access():
    """Demonstrate accessing session information."""
    print("\n=== Session Information Access Example ===")
    
    # Find example session data
    recordings_dir = Path("PythonApp/recordings")
    if recordings_dir.exists():
        session_folders = [f for f in recordings_dir.iterdir() if f.is_dir()]
        if session_folders:
            example_session = session_folders[0]
            print(f"1. Examining session: {example_session.name}")
            
            # Check for metadata file
            metadata_file = example_session / "session_metadata.json"
            if metadata_file.exists():
                import json
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    print("2. Session information:")
                    print(f"  Session ID: {metadata.get('session_id', 'Unknown')}")
                    print(f"  Start time: {metadata.get('start_time', 'Unknown')}")
                    print(f"  Duration: {metadata.get('duration', 'Unknown')} seconds")
                    print(f"  Status: {metadata.get('status', 'Unknown')}")
                    
                    devices = metadata.get('devices', {})
                    print(f"  Devices: {len(devices)}")
                    for device_id, device_info in devices.items():
                        device_type = device_info.get('device_type', 'unknown')
                        print(f"    {device_id}: {device_type}")
                    
                    files = metadata.get('files', {})
                    total_files = sum(len(device_files) for device_files in files.values())
                    print(f"  Total files: {total_files}")
                    
                except Exception as e:
                    print(f"  Error reading metadata: {e}")
            else:
                print("  No metadata file found")
        else:
            print("  No session folders found in PythonApp/recordings")
    else:
        print("  PythonApp/recordings directory not found")


def demonstrate_directory_structure():
    """Show the expected directory structure."""
    print("\n=== Directory Structure Example ===")
    
    structure = """
Expected session folder structure:

session_20250731_143022/
├── session_metadata.json              # Session overview
├── session_20250731_143022_log.json   # Event timeline
├── devices/                           # Device data
│   ├── phone_1/
│   │   ├── rgb_videos/
│   │   │   └── phone_1_rgb_20250731_143022.mp4
│   │   ├── thermal_videos/
│   │   │   └── phone_1_thermal_20250731_143022.mp4
│   │   └── sensor_data/
│   │       └── phone_1_gsr_20250731_143022.csv
│   └── phone_2/
├── webcam/
│   └── webcam_1_20250731_143022.mp4
├── processing/
│   └── hand_segmentation/
│       └── processing_metadata.json
└── exports/
    ├── csv/
    └── matlab/
    """
    
    print(structure)


def main():
    """Main demonstration function."""
    print("Multi-Sensor Recording System - Data Management Examples")
    print("=" * 60)
    
    try:
        demonstrate_session_creation()
        demonstrate_file_naming()
        demonstrate_data_validation()
        demonstrate_session_access()
        demonstrate_directory_structure()
        
        print("\n" + "=" * 60)
        print("Examples completed successfully!")
        print("\nFor more information, see:")
        print("  - docs/DATA_STORAGE_QUICK_REFERENCE.md")
        print("  - docs/DATA_STRUCTURE_DOCUMENTATION.md")
        print("  - docs/FILE_NAMING_STANDARDS.md")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you're running from the project root directory")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)