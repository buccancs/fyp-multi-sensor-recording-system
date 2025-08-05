# Bucika GSR Python Package

Main Python package implementing the PC master-controller for the multi-sensor recording system. This package provides core functionality for device synchronization, sensor data collection, and real-time processing.

## Package Structure

- **calibration/** - Calibration algorithms and quality assessment
- **config/** - Configuration management and settings
- **error_handling/** - Error management and logging systems
- **gui/** - PyQt5-based graphical user interface components
- **hand_segmentation/** - Computer vision and ML processing
- **network/** - Socket communication and protocol handling
- **production/** - Production-ready deployment utilities
- **protocol/** - Communication protocol implementations
- **session/** - Session management and data recording
- **utils/** - Shared utility functions and helpers
- **web_ui/** - Web-based interface components
- **webcam/** - Camera handling and video processing

## Core Components

- **main.py** - Primary application entry point
- **application.py** - Main application controller
- **shimmer_manager.py** - GSR sensor management
- **master_clock_synchronizer.py** - Device synchronization
- **demo_enhanced_ui.py** - Enhanced demo interface

## CLI Commands

The package provides installable CLI commands:
- `bucika-gsr` - Main application
- `bucika-gsr-demo` - Demo interface

## Architecture

Implements offline-first local recording with PC master-controller architecture using JSON socket protocol for device communication.