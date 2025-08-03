# Master Clock Synchronizer - User Guide

## Table of Contents

- [Overview](#overview)
- [What is Master Clock Synchronization?](#what-is-master-clock-synchronization)
  - [Why Precision Timing Matters](#why-precision-timing-matters)
  - [How the System Works](#how-the-system-works)
- [Pre-flight Checklist](#pre-flight-checklist)
  - [Network Requirements](#network-requirements)
  - [Hardware Setup](#hardware-setup)
  - [Software Verification](#software-verification)
- [Step-by-Step Setup Guide](#step-by-step-setup-guide)
  - [Step 1: Initialize the Master Clock System](#step-1-initialize-the-master-clock-system)
  - [Step 2: Connect and Synchronize Devices](#step-2-connect-and-synchronize-devices)
  - [Step 3: Verify Synchronization Quality](#step-3-verify-synchronization-quality)
  - [Step 4: Configure Recording Parameters](#step-4-configure-recording-parameters)
- [Recording Session Workflow](#recording-session-workflow)
  - [Starting a Synchronized Recording Session](#starting-a-synchronized-recording-session)
  - [Monitoring During Recording](#monitoring-during-recording)
  - [Stopping a Recording Session](#stopping-a-recording-session)
- [Understanding Synchronization Quality](#understanding-synchronization-quality)
  - [Quality Metrics Explained](#quality-metrics-explained)
  - [Interpreting Status Indicators](#interpreting-status-indicators)
  - [Quality Troubleshooting](#quality-troubleshooting)
- [Expected Results and Data Output](#expected-results-and-data-output)
  - [Synchronized Timestamps](#synchronized-timestamps)
  - [Session Coordination](#session-coordination)
  - [Quality Validation](#quality-validation)
- [Troubleshooting Guide](#troubleshooting-guide)
  - [Common Issues and Solutions](#common-issues-and-solutions)
  - [Advanced Troubleshooting](#advanced-troubleshooting)
  - [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)
  - [Optimal Configuration](#optimal-configuration)
  - [Network Environment](#network-environment)
  - [Session Management](#session-management)
- [Frequently Asked Questions](#frequently-asked-questions)

## Overview

The Master Clock Synchronizer ensures that all your recording devices (Android phones, thermal cameras, webcams, and physiological sensors) operate with precise timing coordination. This guide will help you set up, configure, and use the synchronization system to achieve research-grade temporal accuracy in your multi-sensor data collection.

## What is Master Clock Synchronization?

Master Clock Synchronization establishes your PC as the authoritative time source for all connected recording devices. Every sensor in your recording setup synchronizes its internal clock with the PC's master clock, ensuring that data from different devices can be precisely aligned in time.

### Why Precision Timing Matters

In multi-sensor research, even small timing discrepancies can invalidate your results:

- **Data Correlation**: Correlate physiological responses with visual stimuli across multiple sensors
- **Event Timing**: Precisely measure reaction times and stimulus-response relationships
- **Research Validity**: Maintain sub-millisecond accuracy required for scientific analysis
- **Data Integrity**: Ensure temporal alignment for post-processing and analysis

### How the System Works

```mermaid
flowchart TB
    subgraph "Master Clock System"
        PC[PC Master Clock]
        NTP[NTP Time Server]
        SYNC[Synchronization Monitor]
    end
    
    subgraph "Connected Devices"
        A1[Android Device 1]
        A2[Android Device 2]
        WC1[Webcam 1]
        WC2[Webcam 2]
        SH[Shimmer Sensor]
    end
    
    PC --> NTP
    PC --> SYNC
    NTP --> A1
    NTP --> A2
    SYNC --> WC1
    SYNC --> WC2
    SYNC --> SH
    
    PC -.->|Master Timestamp| A1
    PC -.->|Master Timestamp| A2
    PC -.->|Sync Commands| WC1
    PC -.->|Sync Commands| WC2
    
    classDef master fill:#e3f2fd,stroke:#0277bd,stroke-width:3px
    classDef device fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef sync fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    
    class PC master
    class NTP,SYNC sync
    class A1,A2,WC1,WC2,SH device
```

The PC provides the master timestamp, the NTP server handles network time synchronization, and the synchronization monitor ensures all devices maintain proper alignment.

## Pre-flight Checklist

### Network Requirements

Before starting synchronization setup, ensure:

- [ ] **Stable WiFi Network**: All Android devices connected to the same network as PC
- [ ] **Network Latency**: Ping times between PC and devices < 20ms
- [ ] **Port Availability**: Ports 8889 (NTP) and 9000 (PC Server) are available
- [ ] **Firewall Configuration**: Allow incoming connections on synchronization ports
- [ ] **Router Stability**: Ensure router doesn't frequently reassign IP addresses

### Hardware Setup

Verify your hardware configuration:

- [ ] **PC Performance**: Sufficient CPU/RAM for simultaneous device coordination
- [ ] **Android Devices**: Bucika GSR app installed and updated
- [ ] **Webcams**: Properly connected and detected by the system
- [ ] **Shimmer Sensors**: Paired and accessible (if using)
- [ ] **USB Connections**: Stable connections for all wired devices

### Software Verification

Check software prerequisites:

- [ ] **Python Environment**: Python 3.7+ with required packages
- [ ] **NTP Library**: `ntplib` package installed (`pip install ntplib`)
- [ ] **Network Libraries**: Socket and threading support available
- [ ] **Logging System**: Proper logging configuration active
- [ ] **Device Drivers**: All camera and sensor drivers installed

## Step-by-Step Setup Guide

### Step 1: Initialize the Master Clock System

**1.1 Start the Master Clock Synchronizer**

```python
from master_clock_synchronizer import initialize_master_synchronizer

# Initialize with default ports
success = initialize_master_synchronizer(
    ntp_port=8889,
    pc_server_port=9000
)

if success:
    print("✅ Master Clock Synchronizer started successfully")
else:
    print("❌ Failed to start synchronizer - check logs")
```

**1.2 Verify NTP Server Status**

The system automatically starts an NTP server for Android device synchronization. Check the logs for:

```
INFO - NTPTimeServer: Server started on port 8889
INFO - MasterClockSynchronizer: Master clock synchronization system started successfully
```

**1.3 Confirm PC Server Connectivity**

The PC server should be listening for Android device connections:

```
INFO - PCServer: Server listening on port 9000
INFO - PCServer: Ready for device connections
```

### Step 2: Connect and Synchronize Devices

**2.1 Connect Android Devices**

On each Android device:
1. Open the Bucika GSR app
2. Navigate to Settings → Network Configuration
3. Enter PC IP address and port 9000
4. Tap "Connect to PC"
5. Wait for "Connected ✅" status

**2.2 Monitor Device Registration**

Watch the PC logs for device connections:

```
INFO - Device connected: Samsung_Galaxy_S21
INFO - Sync initiated for device Samsung_Galaxy_S21
INFO - Device connected: Pixel_6_Pro
INFO - Sync initiated for device Pixel_6_Pro
```

**2.3 Automatic Webcam Registration**

Webcams are automatically registered when the system starts. No manual connection required.

### Step 3: Verify Synchronization Quality

**3.1 Check Device Status**

Use the status monitoring interface to verify synchronization:

```python
from master_clock_synchronizer import get_master_synchronizer

sync_manager = get_master_synchronizer()
devices = sync_manager.get_connected_devices()

for device_id, status in devices.items():
    print(f"Device: {device_id}")
    print(f"  Synchronized: {status.is_synchronized}")
    print(f"  Quality: {status.sync_quality:.2f}")
    print(f"  Offset: {status.time_offset_ms:.1f}ms")
```

**3.2 Quality Standards**

Aim for these synchronization quality levels:

- **Excellent** (≥0.9): Ready for high-precision research
- **Good** (0.7-0.9): Suitable for most research applications  
- **Acceptable** (0.5-0.7): Basic synchronization achieved
- **Poor** (<0.5): Requires troubleshooting

**3.3 Wait for Stabilization**

Allow 30-60 seconds for initial synchronization to stabilize before starting recording sessions.

### Step 4: Configure Recording Parameters

**4.1 Set Quality Thresholds**

Configure minimum acceptable synchronization quality:

```python
# Require high quality for critical research
sync_manager.quality_threshold = 0.8

# Set stricter tolerance for precision work
sync_manager.sync_tolerance_ms = 25.0
```

**4.2 Configure Session Parameters**

Set up recording session defaults:

```python
# Enable all sensor types
record_video = True
record_thermal = True  
record_shimmer = True

# Specify target devices (optional)
target_devices = ["Samsung_Galaxy_S21", "Pixel_6_Pro"]
```

## Recording Session Workflow

### Starting a Synchronized Recording Session

**Step 1: Verify All Devices Ready**

Before starting, ensure all devices show good synchronization quality:

```python
# Check if devices are ready for recording
devices = sync_manager.get_connected_devices()
ready_devices = [d for d, s in devices.items() if s.sync_quality >= 0.8]
print(f"Ready devices: {ready_devices}")
```

**Step 2: Start Synchronized Recording**

```python
import time

# Generate unique session ID
session_id = f"experiment_{int(time.time())}"

# Start synchronized recording across all devices
success = sync_manager.start_synchronized_recording(
    session_id=session_id,
    target_devices=None,  # Use all connected devices
    record_video=True,
    record_thermal=True,
    record_shimmer=True
)

if success:
    print(f"✅ Recording started: Session {session_id}")
else:
    print("❌ Failed to start recording - check device status")
```

**Step 3: Confirm Recording Active**

Verify that all devices have started recording:

```python
# Check active sessions
sessions = sync_manager.get_active_sessions()
session = sessions.get(session_id)

if session and session.is_active:
    print(f"Session active with {len(session.devices)} devices")
    print(f"Session quality: {session.sync_quality:.2f}")
```

### Monitoring During Recording

**Real-time Quality Monitoring**

Set up continuous monitoring during recording:

```python
def monitor_sync_quality(device_status_dict):
    """Callback for real-time quality monitoring"""
    for device_id, status in device_status_dict.items():
        if status.sync_quality < 0.7:
            print(f"⚠️ Low sync quality for {device_id}: {status.sync_quality:.2f}")
        
        if status.time_offset_ms > 40:
            print(f"⚠️ High time offset for {device_id}: {status.time_offset_ms:.1f}ms")

# Register monitoring callback
sync_manager.add_sync_status_callback(monitor_sync_quality)
```

**Session Status Updates**

Monitor session health:

```python
def session_monitor(session_id, session):
    """Monitor session status changes"""
    print(f"Session {session_id}: Quality = {session.sync_quality:.2f}")
    
    if session.sync_quality < 0.7:
        print(f"⚠️ Session quality degraded: {session.sync_quality:.2f}")

sync_manager.add_session_callback(session_monitor)
```

### Stopping a Recording Session

**Graceful Session Termination**

```python
# Stop synchronized recording
success = sync_manager.stop_synchronized_recording(session_id)

if success:
    print(f"✅ Recording stopped: Session {session_id}")
    
    # Get final session statistics
    sessions = sync_manager.get_active_sessions()
    session = sessions.get(session_id)
    
    if session:
        duration = time.time() - session.start_timestamp
        print(f"Session duration: {duration:.1f}s")
        print(f"Final quality: {session.sync_quality:.2f}")
else:
    print("❌ Failed to stop recording - check logs")
```

## Understanding Synchronization Quality

### Quality Metrics Explained

**Sync Quality Score (0.0 - 1.0)**
- Calculated based on time offset from master clock
- Higher values indicate better synchronization
- Minimum 0.8 recommended for research applications

**Time Offset (milliseconds)**
- Difference between device time and master clock
- Lower values indicate better synchronization
- Target: < 25ms for high-precision work

**Last Sync Time**
- Timestamp of most recent synchronization
- Devices re-sync every 5 seconds by default
- Stale sync times may indicate connection issues

### Interpreting Status Indicators

**Device Status Meanings:**

| Status | Sync Quality | Offset Range | Meaning |
|--------|-------------|--------------|---------|
| ✅ Excellent | 0.9 - 1.0 | < 10ms | Perfect for precision research |
| ✅ Good | 0.7 - 0.9 | 10-25ms | Suitable for most applications |
| ⚠️ Acceptable | 0.5 - 0.7 | 25-40ms | Basic sync achieved |
| ❌ Poor | < 0.5 | > 40ms | Requires immediate attention |
| ⚠️ Unsynchronized | 0.0 | N/A | No sync established |

### Quality Troubleshooting

**Poor Quality Issues:**

1. **High Network Latency**
   - Check WiFi signal strength
   - Reduce network traffic
   - Move closer to router

2. **Clock Drift**
   - Wait for automatic re-synchronization
   - Restart devices if persistent
   - Check device battery levels

3. **System Load**
   - Close unnecessary applications
   - Check CPU/memory usage
   - Reduce recording resolution if needed

## Expected Results and Data Output

### Synchronized Timestamps

**Master Timestamp Format**
```python
# All timestamps use Unix time format with microsecond precision
master_timestamp = 1644859200.123456  # Example: 2022-02-14 12:00:00.123456
```

**Synchronization Validation**
```python
# Verify timestamp alignment across devices
devices = sync_manager.get_connected_devices()

for device_id, status in devices.items():
    print(f"{device_id}: Offset = {status.time_offset_ms:.1f}ms")
    
    if abs(status.time_offset_ms) <= 25.0:
        print(f"  ✅ Within tolerance")
    else:
        print(f"  ⚠️ Outside tolerance")
```

### Session Coordination

**Recording Session Output**
```python
# Session information includes timing and device coordination
session = sync_manager.get_active_sessions()[session_id]

print(f"Session: {session.session_id}")
print(f"Start time: {session.start_timestamp}")
print(f"Devices: {list(session.devices)}")
print(f"Quality: {session.sync_quality:.2f}")
print(f"Active: {session.is_active}")
```

### Quality Validation

**Automated Quality Checks**
```python
def validate_session_quality(session_id):
    """Validate synchronization quality for a session"""
    sessions = sync_manager.get_active_sessions()
    session = sessions.get(session_id)
    
    if not session:
        return False, "Session not found"
    
    if session.sync_quality < 0.8:
        return False, f"Quality too low: {session.sync_quality:.2f}"
    
    return True, "Session quality validated"

# Check session before important recordings
valid, message = validate_session_quality(session_id)
print(f"Validation: {message}")
```

## Troubleshooting Guide

### Common Issues and Solutions

**Problem: Devices Not Connecting**

*Symptoms:* Android devices show "Connection Failed" or don't appear in device list

*Solutions:*
1. Verify PC and devices on same WiFi network
2. Check firewall settings allow port 9000
3. Confirm PC IP address in Android app settings
4. Restart PC server: `sync_manager.pc_server.restart()`

**Problem: Poor Synchronization Quality**

*Symptoms:* Sync quality consistently < 0.7, high time offsets

*Solutions:*
1. Reduce network latency:
   - Move devices closer to router
   - Switch to 5GHz WiFi band
   - Reduce network traffic
2. Check system performance:
   - Close unnecessary applications
   - Monitor CPU/memory usage
   - Restart overloaded devices

**Problem: Frequent Re-synchronization**

*Symptoms:* Devices repeatedly losing sync, frequent "re-initiating sync" messages

*Solutions:*
1. Check device battery levels (low battery affects clock stability)
2. Verify stable WiFi connection
3. Increase sync interval: `sync_manager.sync_interval = 10.0`
4. Check for background apps affecting timing

**Problem: Recording Start Failures**

*Symptoms:* `start_synchronized_recording()` returns False

*Solutions:*
1. Verify minimum quality threshold: `sync_manager.quality_threshold = 0.6`
2. Check device connection status
3. Ensure no active sessions with same ID
4. Review device logs for specific errors

### Advanced Troubleshooting

**Network Diagnostics**

```python
import socket
import time

def test_network_latency(device_ip, port=9000):
    """Test network latency to device"""
    start_time = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        result = sock.connect_ex((device_ip, port))
        latency = (time.time() - start_time) * 1000
        sock.close()
        
        if result == 0:
            print(f"✅ Connection to {device_ip}: {latency:.1f}ms")
        else:
            print(f"❌ Connection failed to {device_ip}")
    except Exception as e:
        print(f"❌ Network error: {e}")

# Test each connected device
test_network_latency("192.168.1.100")  # Replace with device IP
```

**System Performance Monitoring**

```python
import psutil

def monitor_system_performance():
    """Monitor system resources during synchronization"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    print(f"CPU Usage: {cpu_percent}%")
    print(f"Memory Usage: {memory.percent}%")
    
    if cpu_percent > 80:
        print("⚠️ High CPU usage may affect synchronization")
    
    if memory.percent > 85:
        print("⚠️ High memory usage may affect performance")

# Monitor during recording sessions
monitor_system_performance()
```

### Performance Optimization

**Optimize for High-Precision Research**

```python
# Configure for maximum precision
sync_manager.sync_tolerance_ms = 10.0      # Tighter tolerance
sync_manager.sync_interval = 2.0           # More frequent checks  
sync_manager.quality_threshold = 0.9       # Higher quality requirement

# Reduce network overhead
sync_manager.ntp_server.ntp_sync_interval = 600.0  # Less frequent NTP sync
```

**Optimize for Stability**

```python
# Configure for stable operation
sync_manager.sync_tolerance_ms = 50.0      # Relaxed tolerance
sync_manager.sync_interval = 10.0          # Less frequent checks
sync_manager.quality_threshold = 0.7       # Lower quality requirement

# Enable automatic recovery
sync_manager.auto_recovery = True
```

## Best Practices

### Optimal Configuration

**Research Environment Setup:**
1. **Dedicated Network**: Use isolated WiFi network for recording devices
2. **Quality Monitoring**: Always monitor sync quality during recordings
3. **Pre-session Validation**: Verify synchronization before starting important sessions
4. **Backup Timing**: Keep system clock synchronized with NTP servers

**Device Management:**
1. **Battery Levels**: Ensure devices have >50% battery before sessions
2. **App Priority**: Set Bucika GSR app to high priority on Android devices
3. **Background Apps**: Minimize background apps during recording
4. **Regular Restarts**: Restart devices between long recording sessions

### Network Environment

**WiFi Optimization:**
- Use 5GHz band for lower latency
- Position router centrally to all devices
- Minimize interference from other devices
- Consider mesh network for large spaces

**Bandwidth Management:**
- Reserve bandwidth for synchronization traffic
- Avoid streaming or downloads during recording
- Monitor network congestion in real-time

### Session Management

**Session Planning:**
1. **Warm-up Period**: Allow 1-2 minutes after device connection before recording
2. **Quality Validation**: Check sync quality immediately before starting
3. **Session Length**: Limit sessions to <60 minutes for optimal quality
4. **Cool-down Period**: Allow 30 seconds between sessions

**Data Validation:**
1. **Timestamp Verification**: Validate timestamp alignment in post-processing
2. **Quality Logging**: Log sync quality throughout sessions
3. **Error Recovery**: Implement automatic session restart on quality loss

## Frequently Asked Questions

**Q: What synchronization accuracy can I expect?**

A: Under optimal conditions (stable network, low latency), the system achieves synchronization accuracy within 10-25ms. In research environments, sub-10ms accuracy is possible with proper configuration.

**Q: How many devices can be synchronized simultaneously?**

A: The system supports up to 10 Android devices plus unlimited webcams. Performance depends on network capacity and PC specifications.

**Q: What happens if synchronization quality drops during recording?**

A: The system continuously monitors quality and attempts automatic re-synchronization. Session quality is tracked and logged. You can set quality thresholds to automatically stop recording if quality becomes unacceptable.

**Q: Can I use the system without NTP synchronization?**

A: Yes, the system can operate using only PC system time, but NTP synchronization significantly improves accuracy, especially for longer recording sessions.

**Q: How do I validate synchronization accuracy?**

A: Use the built-in quality metrics, monitor time offsets, and validate timestamps in post-processing. The system provides comprehensive logging for verification.

**Q: What should I do if a device keeps losing synchronization?**

A: Check network stability, device battery level, and system load. Consider adjusting sync tolerance and interval settings. Restart the problematic device if issues persist.

**Q: Can I customize synchronization parameters for different experiments?**

A: Yes, all synchronization parameters (tolerance, interval, quality thresholds) are configurable and can be adjusted based on experimental requirements.

This user guide provides comprehensive instructions for successfully operating the Master Clock Synchronizer in research environments. For technical details and development information, refer to the Technical Deep-Dive documentation.