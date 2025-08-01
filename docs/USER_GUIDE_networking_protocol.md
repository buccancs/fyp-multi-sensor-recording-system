# Networking and Communication Protocol - User Guide

## Overview

This guide provides step-by-step instructions for using the Networking and Communication Protocol to connect Android devices to the PC controller and establish synchronized multi-device recording sessions. The protocol enables real-time communication between your Android devices and the PC application for coordinated data collection.

## Pre-flight Checklist

Before starting any network operations, ensure you have completed the following prerequisites:

### Network Environment
- [ ] All devices (PC and Android) are connected to the same Wi-Fi network
- [ ] Network allows TCP connections on port 9000 (or your configured port)
- [ ] No firewall blocking connections between devices
- [ ] Stable network connection with minimal packet loss

### PC Application Setup
- [ ] PC application is installed and configured
- [ ] Protocol configuration file (`/protocol/config.json`) is properly configured
- [ ] PC server component is accessible and ready to accept connections
- [ ] Network interface is correctly configured (check IP address)

### Android Device Setup
- [ ] Android application is installed on all recording devices
- [ ] Network permissions are granted to the Android application
- [ ] Android devices have sufficient battery level (>30% recommended)
- [ ] Storage space available for recording data
- [ ] Time synchronization is enabled on Android devices

### Hardware Requirements
- [ ] Minimum Android API level 24 (Android 7.0) for enhanced networking features
- [ ] Wi-Fi connectivity capability on all devices
- [ ] Sufficient processing power for real-time data streaming

## Step-by-Step Usage Guide

### Phase 1: PC Server Initialization

#### 1. Configure Network Settings

First, configure the network settings in the PC application:

1. **Open Configuration File**: Navigate to `/protocol/config.json`
2. **Set Network Parameters**:
   ```json
   {
     "network": {
       "host": "192.168.0.100",     // Your PC's IP address
       "port": 9000,                // Server listening port
       "timeout_seconds": 30,        // Connection timeout
       "max_connections": 10,        // Maximum concurrent devices
       "heartbeat_interval": 5       // Health check frequency
     }
   }
   ```
3. **Save Configuration**: Ensure the file is saved before starting the server

#### 2. Start PC Server

1. **Launch PC Application**: Open the Multi-Sensor Recording System PC application
2. **Initialize Server**: The server should automatically start on application launch
3. **Verify Server Status**: Look for "Server listening on port 9000" in the application logs
4. **Check Network Interface**: Ensure the correct network interface is selected

**Expected Output**: 
```
[INFO] PC Server initialized on 192.168.0.100:9000
[INFO] Waiting for device connections...
[INFO] Protocol version: 1.0.0
```

#### 3. Monitor Server Health

Use the PC application interface to monitor server health:

- **Connection Status**: Shows "Server Active" indicator
- **Device Count**: Displays number of connected devices (initially 0)
- **Network Metrics**: Shows network statistics and performance data

### Phase 2: Android Device Connection

#### 4. Configure Android Network Settings

On each Android device:

1. **Open Android Application**: Launch the Multi-Sensor Recording System app
2. **Navigate to Network Settings**: Tap on "Settings" → "Network Configuration"
3. **Enter Server Details**:
   - **Server IP**: Enter the PC's IP address (e.g., 192.168.0.100)
   - **Server Port**: Enter 9000 (or your configured port)
   - **Device Name**: Enter a unique identifier for this device

```kotlin
// Network configuration screen
Server IP: [192.168.0.100]
Port: [9000]
Device Name: [Android_Device_01]
Connection Timeout: [30 seconds]
Enable Auto-Reconnect: [✓]
```

#### 5. Establish Device Connection

1. **Initiate Connection**: Tap "Connect to Server" button
2. **Monitor Connection Status**: Watch the connection indicator in the app
3. **Verify Handshake**: Wait for successful handshake completion

**Connection Process Visualization**:
```
Android Device → PC Server
[1] TCP Connection Request
[2] Handshake Message (capabilities, version)
[3] Handshake Acknowledgment
[4] Connection Established ✓
```

**Expected Connection Flow**:
- Connection Status: "Connecting..." → "Handshake" → "Connected"
- Device appears in PC application's device list
- Green indicator shows successful connection

#### 6. Verify Device Registration

After connection establishment:

1. **Check PC Application**: Verify device appears in connected devices list
2. **Confirm Capabilities**: Ensure device capabilities are correctly detected
3. **Test Communication**: Use ping test to verify bidirectional communication

**Device Information Display**:
```
Device: Android_Device_01
Status: Connected
Capabilities: [recording, streaming, thermal_imaging]
Battery: 85%
Storage: 24.3 GB available
Latency: 12ms
```

### Phase 3: Multi-Device Coordination

#### 7. Connect Additional Devices

Repeat the connection process for each additional Android device:

1. **Device 2**: Configure with unique device name (e.g., "Android_Device_02")
2. **Device 3**: Configure with unique device name (e.g., "Android_Device_03")
3. **Verify Each Connection**: Ensure all devices appear in PC device list

#### 8. Test Synchronized Communication

Before starting recording, test the communication system:

1. **Ping All Devices**: Use the PC application's "Ping All" function
2. **Measure Latency**: Verify all devices have acceptable latency (<50ms)
3. **Test Commands**: Send test commands to verify command distribution

**Synchronization Test Results**:
```
Device 1: Latency 12ms ✓
Device 2: Latency 15ms ✓  
Device 3: Latency 18ms ✓
All devices synchronized ✓
```

### Phase 4: Recording Session Management

#### 9. Prepare Recording Session

1. **Configure Session Settings**: Set recording parameters in PC application
2. **Select Target Devices**: Choose which devices to include in recording
3. **Verify Device Readiness**: Ensure all devices show "Ready" status

#### 10. Start Synchronized Recording

1. **Initiate Recording**: Click "Start Recording" in PC application
2. **Monitor Command Distribution**: Watch commands being sent to all devices
3. **Verify Recording Status**: Confirm all devices begin recording simultaneously

**Command Distribution Process**:
```mermaid
sequenceDiagram
    participant PC as PC Controller
    participant A1 as Android Device 1
    participant A2 as Android Device 2
    participant A3 as Android Device 3
    
    PC->>A1: start_record(session_id, timestamp)
    PC->>A2: start_record(session_id, timestamp)
    PC->>A3: start_record(session_id, timestamp)
    A1->>PC: ack(success=true)
    A2->>PC: ack(success=true)
    A3->>PC: ack(success=true)
    Note over PC,A3: All devices recording synchronously
```

#### 11. Monitor Real-time Data Streaming

During recording, monitor the data flow:

1. **Preview Frames**: Watch preview frames from each device
2. **Status Updates**: Monitor device status (battery, storage, temperature)
3. **Network Performance**: Check latency and throughput metrics

**Real-time Monitoring Dashboard**:
```
┌─ Device Status ─────────────────────────────────────┐
│ Device 1: Recording | Battery: 85% | Storage: 23.1GB │
│ Device 2: Recording | Battery: 78% | Storage: 18.7GB │
│ Device 3: Recording | Battery: 92% | Storage: 29.3GB │
└─────────────────────────────────────────────────────┘

┌─ Network Performance ───────────────────────────────┐
│ Average Latency: 15ms | Throughput: 2.3 MB/s       │
│ Packet Loss: 0.1% | Jitter: 3ms                    │
└─────────────────────────────────────────────────────┘
```

#### 12. Stop Recording and Data Transfer

1. **Stop Recording**: Click "Stop Recording" to end the session
2. **Monitor File Transfer**: Watch recorded files being transferred from devices
3. **Verify Data Integrity**: Ensure all files are successfully transferred

**File Transfer Process**:
```
Device 1: Transferring video_1.mp4 [████████████] 100%
Device 2: Transferring video_2.mp4 [████████████] 100%
Device 3: Transferring video_3.mp4 [████████████] 100%
All files transferred successfully ✓
```

### Phase 5: Advanced Features

#### 13. Calibration Coordination

For synchronized calibration across devices:

1. **Start Calibration Mode**: Select "Calibration" in PC application
2. **Position Calibration Pattern**: Ensure calibration pattern is visible to all devices
3. **Execute Synchronized Calibration**: All devices capture calibration data simultaneously

#### 14. Adaptive Quality Management

The system automatically adjusts streaming quality based on network conditions:

- **Excellent Network (WiFi)**: Ultra quality (1080p@60fps)
- **Good Network (4G LTE)**: High quality (1080p@30fps)
- **Fair Network (3G)**: Medium quality (720p@30fps)
- **Poor Network**: Low quality (480p@15fps)

## Expected Output and Results

### Successful Connection Indicators

**PC Application**:
- Green connection indicators for all devices
- Device list populated with connected Android devices
- Network metrics showing healthy latency and throughput
- No error messages in the communication log

**Android Application**:
- "Connected" status indicator
- Server information displayed correctly
- Smooth preview streaming without interruptions
- Network quality indicator showing good connection

### Performance Benchmarks

**Normal Operation Targets**:
- **Latency**: <50ms for local network connections
- **Jitter**: <10ms variance
- **Packet Loss**: <1%
- **Throughput**: >1 MB/s per device for video streaming
- **Connection Uptime**: >99% during recording sessions

### Data Output Structure

After a successful recording session, expect the following data structure:

```
recording_session_20240131_143000/
├── device_1/
│   ├── video_001.mp4
│   ├── audio_001.wav
│   ├── sensor_data.json
│   └── metadata.json
├── device_2/
│   ├── video_002.mp4
│   ├── audio_002.wav
│   ├── sensor_data.json
│   └── metadata.json
├── device_3/
│   ├── video_003.mp4
│   ├── audio_003.wav
│   ├── sensor_data.json
│   └── metadata.json
└── session_metadata.json
```

## Troubleshooting Common Issues

### Connection Problems

**Issue**: Android device cannot connect to PC server
**Solutions**:
1. Verify both devices are on the same network
2. Check PC firewall settings for port 9000
3. Confirm PC IP address is correct in Android app
4. Restart both applications and try again

**Issue**: Devices connect but frequently disconnect
**Solutions**:
1. Check network stability and signal strength
2. Increase connection timeout in configuration
3. Verify power management settings on Android devices
4. Check for network interference or congestion

### Performance Issues

**Issue**: High latency or poor streaming quality
**Solutions**:
1. Move devices closer to Wi-Fi router
2. Check for other bandwidth-intensive applications
3. Reduce number of connected devices
4. Lower streaming quality manually if auto-adaptation fails

**Issue**: File transfer failures
**Solutions**:
1. Ensure sufficient storage space on PC
2. Check network stability during transfer
3. Verify file permissions on PC storage location
4. Retry transfer with smaller chunk sizes

### Synchronization Issues

**Issue**: Devices not synchronized properly
**Solutions**:
1. Verify time synchronization on all devices
2. Check network latency and jitter metrics
3. Restart synchronization process
4. Ensure all devices received start command acknowledgment

## Advanced Configuration

### Network Optimization

For optimal performance in research environments:

```json
{
  "network": {
    "buffer_size": 16384,
    "heartbeat_interval": 3,
    "reconnect_attempts": 5,
    "use_newline_protocol": false,
    "tcp_no_delay": true,
    "keep_alive": true
  }
}
```

### Quality Settings

Customize streaming quality based on your network capabilities:

```json
{
  "streaming": {
    "auto_adapt_quality": true,
    "default_quality": "HIGH",
    "quality_adaptation_threshold": 0.6,
    "max_frame_rate": 60,
    "compression_level": "medium"
  }
}
```

This user guide provides comprehensive instructions for successfully establishing and managing network communication in the Multi-Sensor Recording System. Follow each phase sequentially for best results, and refer to the troubleshooting section for resolving common issues.