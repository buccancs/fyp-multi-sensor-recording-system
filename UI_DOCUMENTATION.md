# Multi-Sensor Recording System UI Documentation

## Overview

The Multi-Sensor Recording System features a comprehensive graphical user interface implemented in PyQt6/PyQt5, providing researchers with an intuitive platform for managing multi-device physiological data collection sessions.

## Interface Structure

The main application window consists of a tabbed interface with seven specialized tabs, each focused on specific aspects of the recording system:

### 1. Recording Tab (`ui_tab_00_recording.png`)
- **Session Configuration**: Set session name, duration, and auto-start options
- **Recording Controls**: Create, start, and stop recording sessions
- **Session Status**: Real-time display of current session state
- **Session Log**: Live activity logging during recording sessions

### 2. Devices Tab (`ui_tab_01_devices.png`)
- **Server Status**: Monitor network server operation status
- **Server Controls**: Start/stop the device communication server
- **Connected Devices**: Live view of Android devices connected to the system
- **Device Management**: Real-time status monitoring of all connected devices

### 3. Sensors Tab (`ui_tab_02_sensors.png`)
- **GSR Sensors**: Management of Shimmer GSR+ sensors and simulated devices
- **Sensor Controls**: Add/remove sensors and configure sensor parameters
- **Time Synchronization**: Monitor NTP-like time server for device clock alignment
- **Sync Controls**: Start/stop time synchronization services

### 4. Sync Tab (`ui_tab_03_sync.png`)
- **Device Synchronization**: Coordinate recording across multiple devices
- **Signal Broadcasting**: Flash, audio, and marker signal generation
- **Sync Status**: Real-time synchronization status monitoring
- **Coordination Controls**: Manage multi-device recording coordination

### 5. Calibration Tab (`ui_tab_04_calibration.png`)
- **Camera Calibration**: OpenCV-based camera calibration utilities
- **Calibration Controls**: Initiate and manage calibration procedures
- **Pattern Detection**: Chessboard and other calibration pattern support
- **Calibration Results**: Display calibration parameters and quality metrics

### 6. Security Tab (`ui_tab_05_security.png`)
- **TLS Configuration**: Manage encryption certificates and security settings
- **Authentication**: Token-based device authentication management
- **Security Status**: Monitor security state and certificate validity
- **Access Control**: Device permission and access management

### 7. Settings Tab (`ui_tab_06_settings.png`)
- **System Configuration**: General application settings and preferences
- **Network Settings**: Server ports, protocols, and connection parameters
- **Logging Configuration**: Debug levels and log file management
- **Advanced Options**: Developer and research-specific configuration options

## Key Features

### Real-Time Monitoring
- Live status updates across all tabs
- Real-time device connection monitoring
- Session progress tracking with live logging

### Multi-Device Coordination
- Support for up to 10 concurrent Android devices
- Synchronized recording start/stop across all connected devices
- Device-specific status monitoring and fault detection

### Security Framework
- TLS encryption for all network communications
- Token-based authentication with configurable security levels
- Certificate management and validation

### Research-Ready Interface
- Session-based data organization
- Comprehensive logging and debugging capabilities
- Calibration utilities for experimental setup
- Time synchronization with sub-millisecond accuracy

## Technical Implementation

The UI is built using PyQt6 with PyQt5 fallback compatibility, ensuring broad system support. The interface is designed with modularity in mind, with each tab implementing specific functionality while maintaining integration with the overall system architecture.

### Key UI Components:
- **Tabbed Interface**: Organized workflow for different system aspects
- **Real-Time Updates**: Timer-based status refresh across all components
- **Event-Driven Controls**: Responsive button and control interactions
- **Status Monitoring**: Live feedback on system state and operations
- **Error Handling**: User-friendly error reporting and status messages

The interface serves as the central control point for the entire multi-sensor recording ecosystem, providing researchers with comprehensive tools for managing complex physiological data collection experiments.