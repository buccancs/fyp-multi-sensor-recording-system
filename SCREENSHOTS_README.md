# Multi-Sensor Recording System - Application Screenshots

This document provides a comprehensive overview of the application screenshots generated from the Multi-Sensor Recording System, showcasing both the Python desktop application and web-based dashboard interfaces.

## Generated Screenshots

### 1. Main Desktop Application (PyQt5)
**File:** `screenshots_main_app.png`
- **Description:** Main application window with enhanced PsychoPy-inspired UI
- **Features:** Complete desktop interface for multi-sensor recording system control
- **Components:** Device management, session control, real-time monitoring

### 2. Enhanced UI Demo (Inactive State)
**File:** `screenshots_enhanced_ui.png`  
- **Description:** Enhanced UI demonstration showing the PsychoPy-inspired interface design
- **Features:** Modern, professional interface with improved usability
- **State:** Initial/inactive state showing available features

### 3. Enhanced UI Demo (Active State)
**File:** `screenshots_enhanced_ui_active.png`
- **Description:** Enhanced UI in active recording state
- **Features:** Active device connections, calibration status, recording indicators
- **State:** Simulated recording session with connected devices

### 4. Web Dashboard - Main Page
**File:** `screenshots_web_dashboard.png`
- **Description:** Web-based dashboard main interface
- **Features:** Real-time system monitoring, device status, session overview
- **Access:** Available at `http://localhost:5000/`

### 5. Web Dashboard - Device Management
**File:** `screenshots_web_devices.png`
- **Description:** Device management page of the web dashboard
- **Features:** Device configuration, status monitoring, connection management
- **Access:** Available at `http://localhost:5000/devices`

### 6. Web Dashboard - Session History
**File:** `screenshots_web_sessions.png`
- **Description:** Session history and management page
- **Features:** Recording session history, data management, export options
- **Access:** Available at `http://localhost:5000/sessions`

## Application Components Demonstrated

### Desktop Application (PyQt5)
- **Enhanced Main Window:** Modern PsychoPy-inspired interface design
- **Multi-sensor Integration:** Support for webcams, thermal cameras, Shimmer sensors
- **Real-time Monitoring:** Live data visualization and device status
- **Session Management:** Recording control and data organization

### Web Dashboard (Flask + SocketIO)
- **Responsive Design:** Mobile and tablet-friendly interface
- **Real-time Updates:** WebSocket-based live data streaming
- **Device Control:** Remote device management and configuration
- **Data Visualization:** Interactive charts and monitoring displays

## Technical Implementation

### Desktop Application
- **Framework:** PyQt5 with enhanced UI components
- **Graphics:** Custom styling inspired by PsychoPy design principles
- **Integration:** Direct hardware interface and sensor management
- **Features:** Offline-first recording with local data storage

### Web Interface
- **Backend:** Flask with SocketIO for real-time communication
- **Frontend:** Modern HTML5/CSS3/JavaScript with responsive design
- **Integration:** RESTful API with WebSocket real-time updates
- **Compatibility:** Cross-platform browser support

## System Requirements Met

✅ **Multi-sensor Synchronization:** Both interfaces support synchronized recording  
✅ **Real-time Monitoring:** Live data display and device status updates  
✅ **Professional UI:** Clean, modern interface design  
✅ **Web Accessibility:** Browser-based remote monitoring capability  
✅ **Mobile Support:** Responsive design for tablet/phone access  
✅ **Data Management:** Session recording and export functionality  

## Usage Context

These screenshots demonstrate the Multi-Sensor Recording System's comprehensive capabilities for research applications, particularly in synchronized data collection from multiple sensor modalities including smartphone cameras, thermal imaging, USB webcams, and physiological sensors.

The system provides researchers with both desktop and web-based interfaces for maximum flexibility in data collection scenarios, whether conducting lab-based studies or remote monitoring applications.

## Generated: August 4, 2025
**Environment:** Ubuntu 24.04, Python 3.12, PyQt5 5.15, Flask 3.1  
**Display:** 1920x1080 resolution screenshots  
**Browser:** Firefox headless mode for web interface capture