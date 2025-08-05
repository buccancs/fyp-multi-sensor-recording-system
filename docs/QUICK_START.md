# Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Samsung Galaxy S22 (or compatible Android device)
- TopDon TC001 thermal camera
- Windows/macOS/Linux computer with Python 3.8+
- WiFi network for device communication

### Step-by-Step Setup

#### 1. Hardware Connection
1. **Connect Thermal Camera**: Attach TopDon TC001 to Samsung Galaxy S22 via USB-C
2. **Power On**: Ensure both devices are fully charged and powered on
3. **WiFi Setup**: Connect both mobile device and computer to the same WiFi network

#### 2. Software Installation

**Android Application:**
```bash
# Install the Android APK (from releases or build from source)
adb install bucika_gsr_mobile.apk
```

**Python Desktop Controller:**
```bash
# Clone repository and setup environment
git clone https://github.com/buccancs/bucika_gsr.git
cd bucika_gsr
pip install -r requirements.txt
python PythonApp/main.py
```

#### 3. Network Configuration
1. **Find Device IP**: Note the Android device's IP address from WiFi settings
2. **Configure Connection**: Enter the IP address in the Python desktop controller
3. **Test Connection**: Use the "Test Connection" button to verify communication

#### 4. Basic Recording Session
1. **Start Desktop Controller**: Launch Python application and connect to mobile device
2. **Configure Recording**: Set session name, duration, and sensor parameters
3. **Begin Recording**: Click "Start Recording" on both devices
4. **Monitor Data**: Watch real-time data streams and thermal camera feed
5. **Stop & Save**: End recording and save data files to designated folder

## Common Use Cases

### First-time Setup
- Follow the [System Overview](README.md#getting-started) for detailed installation
- Check [Android Application Guide](android_mobile_application_readme.md) for mobile setup
- Review [Python Controller Guide](python_desktop_controller_readme.md) for desktop configuration

### Research Session
- Use [Session Management](session_management_readme.md#user-guide) for experiment planning
- Configure [Calibration System](calibration_system_readme.md) for accurate measurements
- Set up [Multi-Device Synchronization](multi_device_synchronization_readme.md) for multiple sensors

### Data Analysis
- Export data using [Calibration System](calibration_system_readme.md#data-export)
- Process thermal data with built-in analysis tools
- Review [Testing Framework](testing_framework_readme.md) for validation procedures

## Quick Troubleshooting

### Connection Issues
- **No WiFi Connection**: Ensure both devices are on the same network
- **Port Blocked**: Check firewall settings and try different ports (8080, 8081, 8082)
- **Device Not Found**: Verify IP address and try manual IP entry

### Recording Problems
- **Thermal Camera Not Detected**: Check USB connection and restart application
- **Data Sync Issues**: Verify system time synchronization between devices
- **Storage Errors**: Ensure sufficient storage space on both devices

### Performance Issues
- **Lag in Thermal Feed**: Reduce thermal camera resolution or frame rate
- **Network Latency**: Use wired connection or improve WiFi signal strength
- **Battery Drain**: Connect devices to power during long recording sessions

## Next Steps

Once you have the basic system running:

1. **Explore Advanced Features**: Review [Architecture Diagrams](ARCHITECTURE_DIAGRAMS.md) for system understanding
2. **Customize Setup**: Check [UI Architecture](ui_architecture_readme.md) for interface customization
3. **Integration Options**: See [Shimmer Integration](shimmer_integration_readme.md) for additional sensors
4. **Development**: Follow [Testing Framework](testing_framework_readme.md) for contributing to the project

## Getting Help

- **Documentation**: Browse [Navigation Guide](NAVIGATION.md) for complete documentation index
- **Issues**: Check [TODO List](todo.md) for known limitations
- **Support**: Refer to individual component README files for detailed troubleshooting

---

**System Requirements**: Android 10+, Python 3.8+, 4GB RAM, 10GB storage space
**Network Requirements**: WiFi 802.11n or better, 1Mbps minimum bandwidth
**Recording Capacity**: Up to 8 simultaneous devices, 60 minutes continuous recording