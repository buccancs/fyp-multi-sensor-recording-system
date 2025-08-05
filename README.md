# Bucika GSR - Multi-Sensor Synchronized Recording System

Multi-sensor recording system for synchronized data collection from thermal cameras, GSR sensors, and mobile devices. This system serves as a PC master-controller implementing an offline-first local recording approach with JSON socket protocol communication.

## Project Structure

- **AndroidApp/** - Android mobile application for sensor data collection
- **bucika_gsr/** - Main Python package containing the PC controller
- **data/** - Test videos and sample data files
- **scripts/** - Standalone execution and utility scripts
- **tests/** - Consolidated test suite for all components
- **docs/** - Complete project documentation and technical diagrams
- **protocol/** - Communication protocol definitions
- **calibration_data/** - Calibration test data and session files
- **tools/** - Development and validation tools

## Installation

```bash
pip install -e .
```

## Usage

Run the main application:
```bash
bucika-gsr
```

Run the demo interface:
```bash
bucika-gsr-demo
```

## Architecture

The system implements a PC master-controller architecture with offline-first local recording capabilities. Communication between components uses a JSON socket protocol for reliable data exchange.

## Features

- Multi-device synchronization
- Real-time sensor data collection
- Thermal camera recording
- GSR sensor integration
- Hand segmentation and computer vision
- Web-based user interface
- Comprehensive calibration system