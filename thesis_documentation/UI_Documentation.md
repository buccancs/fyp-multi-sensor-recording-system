# Multi-Sensor Recording System - Enhanced User Interface Documentation

## Overview

This document provides a comprehensive overview of the Multi-Sensor Recording System's enhanced user interfaces, featuring modern, visually appealing designs suitable for professional psychophysiology research environments. The interface improvements include contemporary visual styling, enhanced user experience elements, and realistic multi-sensor recording configurations.

## Visual Enhancement Summary

The user interfaces have been significantly enhanced with:
- **Modern Color Schemes**: Professional purple-to-blue gradients and contemporary color palettes
- **Glassmorphism Effects**: Semi-transparent backgrounds with backdrop blur for web interfaces
- **Enhanced Animations**: Smooth transitions, hover effects, and micro-interactions
- **Improved Typography**: Better font hierarchy using Inter and Segoe UI font families
- **Professional Visual Design**: Research-grade software aesthetics with attention to detail

## System Architecture

The Multi-Sensor Recording System implements a dual-interface approach with enhanced visual design:

1. **PyQt5 Desktop Application**: A native desktop interface with modern styling, gradients, and professional appearance
2. **Web Dashboard**: A browser-based interface featuring glassmorphism design, enhanced cards, and contemporary visual effects

Both interfaces maintain consistent enhanced styling while sharing the same backend components for data handling and device management.

## PyQt5 Desktop Application

### Enhanced Main Window Interface

The desktop application features a sophisticated PyQt5-based interface with modern visual enhancements, displaying realistic research-grade sensor configurations with contemporary design elements.

![PyQt5 Enhanced Main Window](images/ui_screenshots/pyqt_enhanced_main_window.png)

**Visual Enhancements:**
- **Modern Gradient Design**: Beautiful purple-to-blue gradients throughout the interface
- **Enhanced Buttons**: Smooth hover animations with transform effects and gradient styling
- **Improved Status Indicators**: Larger, more vibrant status dots with glow effects
- **Professional Typography**: Enhanced font weights and improved visual hierarchy
- **Subtle Animations**: Smooth transitions and micro-interactions for better user experience
- **Enhanced Form Controls**: Modern rounded inputs, sliders, and progress bars with gradient fills

**Key Features:**
- **Research-Grade Interface**: Clean, professional appearance optimized for laboratory environments
- **Real-time Device Monitoring**: Enhanced visual feedback for connected sensors and devices
- **Android Device Integration**: Improved device cards with modern styling and clear status indicators
- **Advanced Webcam Management**: Professional camera feed management with enhanced visual feedback
- **Session Control**: Modern recording interface with enhanced visual progress indicators
- **Enhanced Status Monitoring**: Beautiful, easy-to-read system health indicators

**Visible Realistic Devices:**
- **Shimmer3 GSR Unit #1**: 85% battery, excellent signal quality, 128Hz sampling, 12,450 samples recorded
- **Shimmer3 ECG Unit #2**: 92% battery, good signal quality, 512Hz sampling, 98,600 samples recorded  
- **Shimmer3 GSR Unit #3**: 67% battery, fair signal quality, standby mode
- **Samsung Galaxy S23**: Participant 1 device, 78% battery, actively recording
- **iPad Pro 12.9**: Experimenter device, 95% battery, monitoring mode
- **Logitech C920 HD Pro**: Facial recording webcam, excellent signal quality
- **Microsoft LifeCam HD-3000**: Overview camera, good signal quality

### Standard Main Application Window

![PyQt5 Main Application](images/ui_screenshots/pyqt_main_app.png)

**Components:**
- **Menu Bar**: Access to all application functions and settings
- **Toolbar**: Quick access to frequently used recording controls
- **Device Status Panel**: Real-time display of connected sensors with detailed specifications
- **Data Visualization Area**: Configurable plots for sensor data streams
- **Control Panel**: Recording start/stop, calibration, and session management
- **Current Session**: "PSYC_2025_P001_S003" with 15.3 minutes duration and excellent data quality

## Web Dashboard Interface

### Enhanced Main Dashboard Overview

The web interface provides a responsive, browser-based monitoring solution with modern glassmorphism design, accessible from any device on the network while displaying enhanced visual styling and realistic device configurations.

![Web UI Main Dashboard](images/ui_screenshots/web_ui_main_dashboard.png)

**Visual Design Features:**
- **Glassmorphism Background**: Beautiful purple gradient backdrop with semi-transparent cards
- **Enhanced Card Design**: Modern rounded cards (20px radius) with subtle gradients and depth effects
- **Animated Status Indicators**: Glowing status dots with pulse, glow, and ping animations
- **Modern Typography**: Inter font family with improved weight hierarchy and spacing
- **Smooth Animations**: Transform effects on hover with enhanced shadows and micro-interactions
- **Professional Color Palette**: Contemporary color scheme optimized for research environments

**Dashboard Features:**
- **Enhanced System Status Cards**: Modern card design showing PC controller, Android devices, and Shimmer sensors
- **Real-time Metrics**: Visually enhanced display of CPU usage (12.5%), memory consumption (34.7%), and system health
- **Device Connection Status**: Beautiful glowing indicators for all connected research-grade devices
- **Session Information**: Modern session cards displaying current recording with participant P001, session 3
- **Data Quality Monitoring**: Enhanced visual tracking of 146,470 total samples across all devices
- **Responsive Design**: Improved mobile-first design with glassmorphism effects maintained across all screen sizes

### Enhanced Device Management Interface

![Web UI Device Management](images/ui_screenshots/web_ui_devices.png)

**Visual Enhancements:**
- **Modern Device Cards**: Enhanced card design with gradient headers and improved visual hierarchy
- **Enhanced Status Indicators**: Larger, more vibrant status indicators with glow effects and animations
- **Improved Typography**: Better font weights and spacing for enhanced readability across all device information
- **Smooth Hover Effects**: Transform animations with enhanced shadows, scale effects, and smooth transitions
- **Professional Color Coding**: Modern color palette for different device states, types, and signal qualities
- **Enhanced Button Design**: Modern buttons with gradient styling, shimmer hover effects, and improved feedback

**Device Management Capabilities:**
- **Shimmer Sensor Details**: Enhanced visual display of battery levels, signal quality, and sampling rates for each unit
- **Android Device Status**: Modern cards showing connection status, battery levels, and recording capabilities
- **Webcam Configuration**: Enhanced video recording status display and quality settings interface
- **Network Information**: Improved presentation of IP addresses and MAC addresses for networked devices
- **Real-time Updates**: Enhanced visual feedback for live status updates via WebSocket connections
- **Remote Control**: Modern interface for connecting/disconnecting devices and modifying recording parameters

**Displayed Research Equipment:**
- **3 Shimmer3 Units**: GSR and ECG sensors with different battery levels and signal qualities
- **3 Android Devices**: Participant phones and experimenter tablet with recording capabilities
- **3 Camera Systems**: USB webcams and network cameras for comprehensive video capture

### Enhanced Session History and Management

![Web UI Session Management](images/ui_screenshots/web_ui_sessions.png)

**Visual Design Improvements:**
- **Modern Session Cards**: Enhanced card design with glassmorphism effects and improved visual hierarchy
- **Enhanced Progress Indicators**: Beautiful progress bars with gradient fills and smooth animations
- **Improved Data Visualization**: Better charts and metrics display with modern color schemes
- **Professional Typography**: Enhanced font hierarchy with better spacing and readability
- **Smooth Interactions**: Enhanced hover effects and transitions for better user experience
- **Contemporary Color Palette**: Modern colors for different session states and data quality indicators

**Session Management Features:**
- **Enhanced Recording History**: Modern card-based display of participant sessions with realistic IDs and improved visual organization
- **Detailed Session Metadata**: Enhanced presentation of duration, participant ID, data quality, and file sizes
- **Advanced Data Export Tools**: Improved interface for downloading and analyzing recorded sensor data
- **Enhanced Search and Filter**: Modern search interface to find specific sessions by participant, date, or session type
- **Improved Preview Capabilities**: Enhanced quick data preview interface without requiring full download
- **Research Context Display**: Better visualization of calibration sessions and multi-session participant studies

**Example Sessions Shown:**
- **PSYC_2025_P001_S003**: Current active recording (15.3 min, excellent quality)
- **PSYC_2025_P001_S002**: Previous session (22.7 min, 145.2 MB data file)
- **PSYC_2025_P001_S001**: First participant session (18.1 min, excellent quality)
- **PSYC_2025_P000_CALIB**: System calibration session (5.0 min baseline)

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