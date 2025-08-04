# Multi-Sensor Recording System - User Interface Documentation

## Overview

This document provides a comprehensive overview of the Multi-Sensor Recording System's user interfaces, capturing both the PyQt5 desktop application and the web-based dashboard. These screenshots were generated as part of the thesis documentation for the "Multi-Sensor Recording System" project.

## System Architecture

The Multi-Sensor Recording System implements a dual-interface approach:

1. **PyQt5 Desktop Application**: A native desktop interface providing full system control and real-time sensor management
2. **Web Dashboard**: A browser-based interface offering remote monitoring and basic control capabilities

## PyQt5 Desktop Application

### Enhanced Main Window Interface

The desktop application features a sophisticated PyQt5-based interface designed with inspiration from psychophysiology software standards.

![PyQt5 Enhanced Main Window](images/ui_screenshots/pyqt_enhanced_main_window.png)

**Key Features:**
- **Modern GUI Design**: Clean, professional interface optimized for research environments
- **Real-time Data Visualization**: Live sensor data streams with customizable plotting options
- **Device Management Panel**: Direct control over Shimmer3+ sensors and Android devices
- **Session Control**: Complete recording session management with timeline controls
- **Status Monitoring**: Real-time system health and device connectivity indicators

### Standard Main Application Window

![PyQt5 Main Application](images/ui_screenshots/pyqt_main_app.png)

**Components:**
- **Menu Bar**: Access to all application functions and settings
- **Toolbar**: Quick access to frequently used recording controls
- **Device Status Panel**: Real-time display of connected sensors and their status
- **Data Visualization Area**: Configurable plots for sensor data streams
- **Control Panel**: Recording start/stop, calibration, and session management

## Web Dashboard Interface

### Main Dashboard Overview

The web interface provides a responsive, browser-based monitoring solution accessible from any device on the network.

![Web UI Main Dashboard](images/ui_screenshots/web_ui_main_dashboard.png)

**Dashboard Features:**
- **System Status Cards**: Overview of PC controller, Android devices, and Shimmer sensors
- **Real-time Metrics**: CPU usage, memory consumption, and system health indicators
- **Device Connection Status**: Visual indicators for all connected devices
- **Session Information**: Current recording status and session metadata
- **Responsive Design**: Optimized for desktop, tablet, and mobile viewing

### Device Management Interface

![Web UI Device Management](images/ui_screenshots/web_ui_devices.png)

**Device Management Capabilities:**
- **Device Discovery**: Automatic detection and listing of available sensors
- **Connection Management**: Connect/disconnect devices remotely
- **Status Monitoring**: Real-time device health and battery levels
- **Configuration Access**: Remote device configuration and calibration
- **Network Topology**: Visual representation of device connections

### Session History and Management

![Web UI Session Management](images/ui_screenshots/web_ui_sessions.png)

**Session Management Features:**
- **Recording History**: Complete list of all recording sessions
- **Session Metadata**: Detailed information for each recording session
- **Data Export Tools**: Options for downloading and analyzing recorded data
- **Search and Filter**: Find specific sessions by date, duration, or participants
- **Preview Capabilities**: Quick data preview without full download

## Technical Implementation

### Desktop Application (PyQt5)

- **Framework**: PyQt5 with modern Fusion style
- **Architecture**: MVC pattern with signal-slot communication
- **Real-time Updates**: Qt timers for data refresh and UI updates
- **Threading**: Background threads for sensor communication
- **Cross-platform**: Supports Windows, macOS, and Linux

### Web Dashboard (Flask + SocketIO)

- **Backend**: Flask with SocketIO for real-time communication
- **Frontend**: Bootstrap 5 with responsive design
- **Real-time Data**: WebSocket connections for live updates
- **API Integration**: RESTful endpoints for device communication
- **Mobile Responsive**: Optimized for various screen sizes

## Use Cases

### Research Laboratory Environment

1. **Primary Interface**: PyQt5 desktop application for researchers conducting experiments
2. **Secondary Monitoring**: Web dashboard for supervisors and remote monitoring
3. **Mobile Access**: Web interface accessible on tablets for field work

### Remote Monitoring Scenarios

1. **Multi-room Studies**: Web dashboard accessible from control rooms
2. **Collaborative Research**: Multiple researchers monitoring from different locations
3. **Quality Assurance**: Real-time monitoring of data quality and system health

## Integration and Workflow

Both interfaces operate on the same underlying system:

- **Shared Data Sources**: Both UIs access identical sensor data and system status
- **Synchronized State**: Changes made in one interface are reflected in the other
- **Complementary Features**: Desktop app for detailed control, web interface for monitoring
- **Network Communication**: JSON-based protocol for Android device integration

## Conclusion

The dual-interface approach provides flexibility for different use cases while maintaining a consistent user experience. The PyQt5 desktop application serves as the primary control interface for researchers, while the web dashboard enables remote monitoring and basic control from any networked device.

---

*Generated as part of the Multi-Sensor Recording System thesis documentation*
*Date: August 2025*
*System Version: 3.1.1 Enhanced*