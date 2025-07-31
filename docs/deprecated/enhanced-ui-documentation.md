# Enhanced UI Documentation

## PsychoPy-Inspired Interface Enhancements

This document describes the enhanced user interface improvements made to the Multi-Sensor Recording System Controller, inspired by PsychoPy's clean and professional design principles.

### Overview

The enhanced UI provides a modern, intuitive interface that improves upon the original design with:

- **Clean, modern design** inspired by PsychoPy's professional appearance
- **Better visual hierarchy** with improved spacing and organization
- **Professional color scheme** using Microsoft Fluent Design principles
- **Enhanced control organization** with logical grouping of related functions
- **Visual feedback and status indicators** for better user awareness
- **Improved navigation structure** for easier use

### Key Components

#### 1. Enhanced Main Window (`enhanced_ui_main_window.py`)

The main enhanced window provides three primary panels:

##### Left Panel - Device Management
- **Device Status Display**: Real-time connection status with color-coded indicators
- **Connection Controls**: One-click connect/disconnect for individual or all devices
- **Calibration Interface**: Streamlined calibration workflow

##### Center Panel - Stimulus Presentation & Preview
- **Video Preview Area**: Large, clean preview area for stimulus content
- **Stimulus Controls**: Intuitive playback controls with modern button styling
- **Progress Tracking**: Visual progress bar and timing information

##### Right Panel - Recording Controls & Monitoring
- **Recording Session Management**: Clear recording controls with status display
- **System Monitoring**: Real-time CPU and memory usage indicators
- **System Logs**: Live log display with improved formatting

#### 2. Modern UI Components

##### ModernButton Class
- Custom-styled buttons with hover and pressed states
- Primary and secondary button variants
- Consistent sizing and spacing

##### StatusIndicator Class
- Color-coded circular indicators for device status
- Smooth visual transitions
- Standard status colors (green=connected, red=disconnected, orange=warning)

##### ModernGroupBox Class
- Clean grouping containers with subtle borders
- Improved typography and spacing
- Professional appearance

### Visual Design Principles

#### Color Scheme
- **Primary Blue**: #0078d4 (Microsoft Blue)
- **Success Green**: #107c10
- **Warning Orange**: #ff8c00
- **Error Red**: #d13438
- **Text Dark**: #323130
- **Background Light**: #faf9f8
- **Border Neutral**: #d1d1d1

#### Typography
- **Primary Font**: Segoe UI (system font)
- **Monospace Font**: Consolas/Monaco (for logs and timing)
- **Consistent Font Weights**: Regular (400) and Semi-bold (600)

#### Spacing and Layout
- **Consistent Margins**: 12px standard spacing
- **Logical Grouping**: Related controls grouped in frames
- **Responsive Layout**: Resizable splitter panels

### Usage

#### Running the Enhanced UI

1. **Direct Launch** (Enhanced UI is now the default):
   ```bash
   cd PythonApp/src
   python main.py
   ```

2. **Demo Mode**:
   ```bash
   cd PythonApp/src
   python demo_enhanced_ui.py
   ```

#### Key Features

1. **Device Management**:
   - Connect/disconnect individual devices
   - Bulk connect/disconnect operations
   - Real-time status monitoring

2. **Stimulus Control**:
   - Load video files via file dialog
   - Playback controls (play, pause, stop)
   - Progress tracking and timing display

3. **Recording Sessions**:
   - Start/stop recording with one click
   - Real-time duration and size tracking
   - Session management and status display

4. **System Monitoring**:
   - Live CPU and memory usage
   - System log display
   - Performance indicators

### Technical Implementation

#### Dependencies
- **PyQt5**: Core GUI framework
- **Standard Library**: datetime, time, os, sys
- **Optional**: Existing system components (with graceful fallbacks)

#### Architecture
- **Modular Design**: Separate components for different UI areas
- **Signal-Slot Communication**: Proper PyQt5 event handling
- **Graceful Degradation**: Works even if some system components are unavailable
- **Responsive Layout**: Adaptable to different screen sizes

#### Error Handling
- Graceful import fallbacks for missing dependencies
- Comprehensive logging integration
- User-friendly error messages

### Screenshots

The enhanced UI provides:
1. **Clean Layout**: Organized three-panel design
2. **Professional Appearance**: Modern styling throughout
3. **Intuitive Controls**: Easy-to-understand interface elements
4. **Status Visibility**: Clear feedback on system state

### Comparison with Original UI

| Aspect | Original UI | Enhanced UI |
|--------|-------------|-------------|
| **Design Language** | Basic PyQt5 default | PsychoPy-inspired modern |
| **Color Scheme** | System default | Professional Microsoft Fluent |
| **Button Styling** | Standard buttons | Custom modern buttons |
| **Status Indicators** | Text-based | Visual color indicators |
| **Layout** | Basic grid/box | Responsive splitter panels |
| **Typography** | Mixed fonts | Consistent Segoe UI |
| **Spacing** | Inconsistent | Professional 12px grid |
| **Visual Hierarchy** | Flat | Clear information hierarchy |

### Future Enhancements

Potential future improvements:
1. **Animation Support**: Smooth transitions and micro-interactions
2. **Theming System**: Light/dark theme toggle
3. **Accessibility**: Enhanced keyboard navigation and screen reader support
4. **Customization**: User-configurable layouts and preferences
5. **Advanced Visualizations**: Real-time data plots and graphs

### Integration Notes

The enhanced UI is designed to be:
- **Drop-in Compatible**: Can replace the original main window
- **Backward Compatible**: Works with existing system components
- **Modular**: Individual components can be used separately
- **Extensible**: Easy to add new features and panels

This enhanced interface provides a significant improvement in user experience while maintaining all core functionality of the Multi-Sensor Recording System.