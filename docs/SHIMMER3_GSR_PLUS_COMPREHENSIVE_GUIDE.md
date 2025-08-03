# Shimmer3 GSR+ Device: Comprehensive Integration Guide

## Table of Contents

- [Overview](#overview)
- [Device Specifications](#device-specifications)
- [SDK and API Integration](#sdk-and-api-integration)
- [Hardware Setup and Configuration](#hardware-setup-and-configuration)
- [Software Implementation](#software-implementation)
- [Data Collection and Processing](#data-collection-and-processing)
- [Protocol Specifications](#protocol-specifications)
- [Troubleshooting and Best Practices](#troubleshooting-and-best-practices)
- [Integration Examples](#integration-examples)
- [Performance Optimization](#performance-optimization)

## Overview

The Shimmer3 GSR+ device is a state-of-the-art wearable sensor platform that enables high-precision galvanic skin response (GSR) measurements alongside complementary physiological signals including photoplethysmography (PPG), accelerometry, and other biometric parameters. This comprehensive guide consolidates all technical information, user guidance, and protocol specifications for effective integration within the Multi-Sensor Recording System.

### Key Capabilities

- **High-Precision GSR Measurement**: Galvanic skin response with configurable range settings (10kΩ to 4.7MΩ)
- **Multi-Modal Sensor Suite**: PPG, accelerometer, gyroscope, and magnetometer integration
- **Bluetooth Connectivity**: Wireless data transmission with both Classic and BLE support
- **Configurable Sampling Rates**: From 1 Hz to 512 Hz for various research applications
- **Real-Time Data Streaming**: Live sensor data with callback system support
- **Session-Based Recording**: Organized data collection with comprehensive metadata
- **Cross-Platform Support**: Android and PC integration with unified API

### System Integration Architecture

```mermaid
graph TB
    subgraph "Shimmer3 GSR+ Integration Architecture"
        subgraph "Hardware Layer"
            SHIMMER[Shimmer3 GSR+ Device]
            ELECTRODES[GSR Electrodes]
            BATTERY[Rechargeable Battery]
            BLUETOOTH[Bluetooth Radio]
        end
        
        subgraph "Communication Layer"
            BT_CLASSIC[Bluetooth Classic]
            BT_LE[Bluetooth Low Energy]
            SDK_ANDROID[Android Shimmer SDK]
            SDK_PC[pyshimmer Library]
        end
        
        subgraph "Application Layer"
            ANDROID_APP[Android Application]
            PC_APP[PC Desktop Controller]
            DATA_PROC[Data Processing]
            SESSION_MGR[Session Manager]
        end
        
        subgraph "Data Layer"
            CSV_FILES[CSV Data Files]
            JSON_META[JSON Metadata]
            SYNC_DATA[Synchronized Timestamps]
            QUALITY_METRICS[Quality Assessment]
        end
        
        SHIMMER --> BLUETOOTH
        BLUETOOTH --> BT_CLASSIC
        BLUETOOTH --> BT_LE
        BT_CLASSIC --> SDK_PC
        BT_LE --> SDK_ANDROID
        SDK_ANDROID --> ANDROID_APP
        SDK_PC --> PC_APP
        ANDROID_APP --> DATA_PROC
        PC_APP --> DATA_PROC
        DATA_PROC --> SESSION_MGR
        SESSION_MGR --> CSV_FILES
        SESSION_MGR --> JSON_META
        SESSION_MGR --> SYNC_DATA
        SESSION_MGR --> QUALITY_METRICS
    end
```

## Device Specifications

### Hardware Capabilities

| Specification | Details |
|---------------|---------|
| **Dimensions** | 65mm x 32mm x 12mm |
| **Weight** | 23.6g (including battery) |
| **Battery Life** | 8-14 hours (depending on configuration) |
| **Sampling Rate** | 1 - 512 Hz (configurable) |
| **Memory** | 2GB MicroSD card support |
| **Connectivity** | Bluetooth 2.1 + BLE |
| **Operating Range** | 10 meters (line of sight) |
| **Operating Temperature** | 0°C to 50°C |

### GSR Sensor Specifications

The Shimmer3 GSR+ provides configurable measurement ranges optimized for different research scenarios:

| Range Setting | Resistance Range | Typical Application |
|---------------|------------------|-------------------|
| **Range 0** | 10kΩ - 56kΩ | High arousal states, stress research |
| **Range 1** | 56kΩ - 220kΩ | Normal conditions, general monitoring |
| **Range 2** | 220kΩ - 680kΩ | Dry skin, low humidity environments |
| **Range 3** | 680kΩ - 4.7MΩ | Very dry skin, special populations |
| **Range 4** | Auto-range | Adaptive measurement, long-term monitoring |

### Additional Sensors

- **PPG (Photoplethysmography)**: Heart rate and blood volume pulse measurement
- **3-Axis Accelerometer**: ±2g/±4g/±8g/±16g selectable ranges
- **3-Axis Gyroscope**: ±250/±500/±1000/±2000 dps ranges
- **3-Axis Magnetometer**: ±1.3/±1.9/±2.5/±4.0/±4.7/±5.6/±8.1 gauss ranges

## SDK and API Integration

### Android Integration

The Android integration utilizes the official Shimmer Java Android API for robust device communication:

#### Key Android Components

```kotlin
// Shimmer device management
class ShimmerRecorder(
    private val context: Context,
    private val deviceAddress: String
) {
    private var shimmerDevice: Shimmer? = null
    private val dataBuffer = CircularBuffer<ShimmerDataSample>(1000)
    
    fun connect(): Boolean {
        return try {
            shimmerDevice = Shimmer(context).apply {
                bluetoothAddress = deviceAddress
                connect()
                setEnabledSensors(
                    SENSOR_GSR or SENSOR_PPG_A13 or 
                    SENSOR_ACCEL or SENSOR_GYRO
                )
                setSamplingRateShimmer(51.2) // 51.2 Hz
                setGSRRange(1) // Normal range
            }
            true
        } catch (e: Exception) {
            Logger.e("ShimmerRecorder", "Connection failed", e)
            false
        }
    }
    
    fun startRecording(sessionId: String) {
        shimmerDevice?.startStreaming()
        // Data handling through callback system
    }
    
    fun stopRecording() {
        shimmerDevice?.stopStreaming()
        shimmerDevice?.disconnect()
    }
}
```

#### Android SDK Integration Details

```kotlin
// Enhanced Shimmer configuration with reflection-based compatibility
class ShimmerManager {
    private val connectedDevices = mutableMapOf<String, Shimmer>()
    
    fun configureDevice(deviceId: String, config: ShimmerConfig): Boolean {
        val device = connectedDevices[deviceId] ?: return false
        
        return try {
            // Configure sampling rate with SDK compatibility
            device.setSamplingRateShimmer(config.samplingRate)
            
            // Configure GSR range with validation
            device.setGSRRange(config.gsrRange)
            
            // Enable sensors based on configuration
            var enabledSensors = 0
            if (config.enableGSR) enabledSensors = enabledSensors or SENSOR_GSR
            if (config.enablePPG) enabledSensors = enabledSensors or SENSOR_PPG_A13
            if (config.enableAccel) enabledSensors = enabledSensors or SENSOR_ACCEL
            if (config.enableGyro) enabledSensors = enabledSensors or SENSOR_GYRO
            
            device.setEnabledSensors(enabledSensors)
            true
        } catch (e: Exception) {
            Logger.e("ShimmerManager", "Configuration failed for device $deviceId", e)
            false
        }
    }
}
```

### PC Integration

The PC integration provides both direct pyshimmer connections and Android-mediated connections:

#### Direct PC Connection (pyshimmer)

```python
# Enhanced ShimmerManager with multi-library support
class ShimmerManager:
    def __init__(self):
        self.connected_devices = {}
        self.data_callbacks = {}
        self.session_data = {}
        
    def connect_device(self, device_id: str, port: str = None) -> bool:
        """Connect to Shimmer device via direct Bluetooth or serial"""
        try:
            if self._has_pyshimmer():
                device = self._connect_pyshimmer(device_id, port)
            elif self._has_bluetooth():
                device = self._connect_bluetooth(device_id)
            else:
                self.logger.warning("No Shimmer libraries available")
                return False
                
            if device:
                self.connected_devices[device_id] = device
                return True
        except Exception as e:
            self.logger.error(f"Failed to connect device {device_id}: {e}")
        return False
    
    def _connect_pyshimmer(self, device_id: str, port: str) -> Optional[Any]:
        """Direct pyshimmer connection"""
        try:
            from pyshimmer import ShimmerBluetooth
            device = ShimmerBluetooth(port)
            device.connect()
            return device
        except ImportError:
            self.logger.warning("pyshimmer library not available")
        except Exception as e:
            self.logger.error(f"pyshimmer connection failed: {e}")
        return None
    
    def start_recording(self, session_id: str) -> bool:
        """Start recording session for all connected devices"""
        success = True
        for device_id, device in self.connected_devices.items():
            try:
                device.start_streaming()
                self.session_data[device_id] = {
                    'session_id': session_id,
                    'start_time': datetime.now(),
                    'samples': []
                }
            except Exception as e:
                self.logger.error(f"Failed to start recording for {device_id}: {e}")
                success = False
        return success
```

#### Android-Mediated PC Connection

```python
# Network-based Shimmer integration via Android
class AndroidShimmerProxy:
    def __init__(self, android_manager):
        self.android_manager = android_manager
        self.shimmer_data_queue = queue.Queue()
        
    def request_shimmer_connection(self, device_address: str) -> bool:
        """Request Android app to connect to Shimmer device"""
        message = {
            'type': 'shimmer_connect',
            'device_address': device_address,
            'timestamp': time.time()
        }
        return self.android_manager.send_command(message)
    
    def configure_shimmer_settings(self, device_id: str, config: dict) -> bool:
        """Configure Shimmer device via Android"""
        message = {
            'type': 'shimmer_configure',
            'device_id': device_id,
            'config': config,
            'timestamp': time.time()
        }
        return self.android_manager.send_command(message)
    
    def start_shimmer_recording(self, session_id: str) -> bool:
        """Start Shimmer recording via Android"""
        message = {
            'type': 'shimmer_start_recording',
            'session_id': session_id,
            'timestamp': time.time()
        }
        return self.android_manager.send_command(message)
```

## Hardware Setup and Configuration

### Pre-Flight Checklist

Before beginning any recording session with the Shimmer3 GSR+, ensure all prerequisites are met:

#### Hardware Requirements
- [ ] **Shimmer3 GSR+ Device**: Fully charged (battery level > 20%)
- [ ] **Electrode Gel**: Conductive gel for optimal skin contact
- [ ] **Skin Preparation Materials**: Alcohol wipes for electrode site cleaning
- [ ] **Shimmer Docking Station**: For device charging and data transfer
- [ ] **MicroSD Card**: Formatted and inserted (for on-device logging)
- [ ] **Bluetooth-Enabled Device**: PC with Bluetooth adapter or Android smartphone

#### Software Prerequisites
- [ ] **Multi-Sensor Recording System**: Installed and configured
- [ ] **Shimmer SDK**: pyshimmer library (PC) or Shimmer Android API
- [ ] **Bluetooth Permissions**: Location and Bluetooth permissions granted (Android)
- [ ] **Device Pairing**: Shimmer3 device paired in system Bluetooth settings

#### Environmental Considerations
- [ ] **Ambient Temperature**: 18-25°C (optimal for stable measurements)
- [ ] **Humidity Level**: 40-60% relative humidity (prevents electrode drying)
- [ ] **Electromagnetic Interference**: Minimal WiFi/cellular interference
- [ ] **Movement Constraints**: Stable environment for motion-sensitive measurements

### Device Setup Workflow

```mermaid
flowchart TD
    A[Start Setup] --> B[Hardware Inspection]
    B --> C{Device Charged?}
    C -->|No| D[Charge Device]
    D --> C
    C -->|Yes| E[Prepare Electrodes]
    
    E --> F[Clean Skin with Alcohol]
    F --> G[Apply Conductive Gel]
    G --> H[Attach Electrodes]
    
    H --> I[Choose Connection Method]
    I --> J[PC Direct Connection]
    I --> K[Android Mediated]
    I --> L[Hybrid PC+Android]
    
    J --> M[Start pyshimmer]
    K --> N[Launch Android App]
    L --> O[Coordinate Both Systems]
    
    M --> P[Device Discovery]
    N --> P
    O --> P
    
    P --> Q{Device Found?}
    Q -->|No| R[Check Bluetooth/Pairing]
    R --> P
    Q -->|Yes| S[Configure Sensors]
    
    S --> T[Set Sampling Rate]
    T --> U[Enable GSR Channel]
    U --> V[Start Recording]
    V --> W[Monitor Data Quality]
    
    classDef hardware fill:#ffe6cc
    classDef software fill:#e6f3ff
    classDef decision fill:#fff2e6
    classDef action fill:#e6ffe6
    
    class B,E,F,G,H hardware
    class M,N,O,S,T,U software
    class C,Q decision
    class A,D,I,P,V,W action
```

### Electrode Preparation and Placement

#### Skin Site Selection

Choose appropriate measurement locations for optimal GSR data quality:

- **Preferred Sites**: Index and middle finger distal phalanges (dominant hand)
- **Alternative Sites**: Palm sites (thenar and hypothenar eminences)
- **Avoid**: Areas with visible damage, excessive hair, or jewelry contact

#### Skin Preparation Protocol

```
Step 1: Clean electrode sites with alcohol wipe
Step 2: Wait 30 seconds for complete evaporation
Step 3: Gently abrade skin with fine-grit emery paper (optional)
Step 4: Apply thin layer of conductive electrode gel
Step 5: Attach electrodes ensuring complete skin contact
```

## Software Implementation

### Configuration Management

#### GSR Range Selection

```python
# Range selection based on expected skin conductance
gsr_ranges = {
    0: "10kΩ - 56kΩ",    # High arousal states, stress research
    1: "56kΩ - 220kΩ",   # Normal conditions, general monitoring  
    2: "220kΩ - 680kΩ",  # Dry skin, low humidity environments
    3: "680kΩ - 4.7MΩ",  # Very dry skin, special populations
    4: "Auto-range"      # Adaptive measurement, long-term monitoring
}

# Configuration example
shimmer_manager.set_gsr_range(device_id="shimmer_001", range_setting=1)
```

#### Sampling Rate Configuration

```python
# Sampling rate options and applications
sampling_rates = {
    1.0: "Ultra low-power, 24+ hour monitoring",
    10.0: "Low-power baseline studies",
    51.2: "Standard research applications", 
    128.0: "High-resolution emotional responses",
    256.0: "Research-grade temporal precision",
    512.0: "Specialized high-frequency analysis"
}

# Configuration example
shimmer_manager.set_sampling_rate(device_id="shimmer_001", rate=51.2)
```

#### Multi-Sensor Configuration

```python
# Sensor combination examples
sensor_configs = {
    "gsr_only": {"GSR"},
    "gsr_ppg": {"GSR", "PPG_A13"},
    "gsr_motion": {"GSR", "ACCEL_X", "ACCEL_Y", "ACCEL_Z"},
    "comprehensive": {
        "GSR", "PPG_A13", 
        "ACCEL_X", "ACCEL_Y", "ACCEL_Z",
        "GYRO_X", "GYRO_Y", "GYRO_Z"
    }
}

# Apply configuration
enabled_channels = sensor_configs["gsr_ppg"]
shimmer_manager.set_enabled_channels(device_id="shimmer_001", channels=enabled_channels)
```

## Data Collection and Processing

### Session Management

#### Session Initialization

```python
# Start recording session
session_id = f"participant_001_condition_A_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
recording_success = shimmer_manager.start_recording(session_id)

if recording_success:
    print(f"Recording started: {session_id}")
    # Proceed with experimental protocol
else:
    print("Recording failed - check device connections")
```

#### Real-Time Data Monitoring

```python
# Monitor data quality during recording
def monitor_data_quality():
    for device_id in shimmer_manager.get_connected_devices():
        status = shimmer_manager.get_shimmer_status()[device_id]
        
        print(f"Device: {device_id}")
        print(f"  Battery: {status.battery_level}%")
        print(f"  Samples: {status.samples_recorded}")
        print(f"  Connection: {status.device_state.value}")
        
        # Check for data quality issues
        if status.battery_level < 15:
            print("  WARNING: Low battery level")
        if status.samples_recorded == 0:
            print("  WARNING: No data received")
```

### Data Quality Assessment

#### Real-Time Quality Monitoring

```python
# Implement real-time quality assessment
def assess_signal_quality(samples):
    """Assess GSR signal quality in real-time"""
    if len(samples) < 10:
        return "insufficient_data"
    
    # Calculate signal stability
    signal_variance = np.var(samples)
    signal_range = max(samples) - min(samples)
    
    # Detect artifacts
    artifact_threshold = 3 * np.std(samples)
    artifacts = sum(1 for s in samples if abs(s - np.mean(samples)) > artifact_threshold)
    
    # Quality classification
    if artifacts > len(samples) * 0.1:
        return "poor_quality"
    elif signal_variance > 10.0:
        return "high_noise"
    elif signal_range < 0.1:
        return "low_signal"
    else:
        return "good_quality"

# Monitor quality during recording
quality_status = assess_signal_quality(recent_gsr_samples)
```

## Protocol Specifications

### Data Structures and Formats

#### Shimmer Data Sample Structure

```python
@dataclass
class ShimmerDataSample:
    timestamp: float
    system_time: str
    device_id: str
    connection_type: str
    session_id: str
    gsr_conductance: float
    ppg_a13: Optional[float] = None
    accel_x: Optional[float] = None
    accel_y: Optional[float] = None
    accel_z: Optional[float] = None
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    battery_percentage: Optional[int] = None
    signal_strength: Optional[float] = None
```

#### Network Communication Messages

| Message Type | Purpose | Required Fields |
|--------------|---------|----------------|
| `shimmer_connect` | Device connection request | `device_address`, `timestamp` |
| `shimmer_configure` | Device configuration | `device_id`, `config`, `timestamp` |
| `shimmer_start_recording` | Begin data recording | `session_id`, `timestamp` |
| `shimmer_stop_recording` | End data recording | `session_id`, `timestamp` |
| `shimmer_data_sample` | Real-time data transmission | `sample_data`, `timestamp` |
| `shimmer_status_update` | Device status information | `device_id`, `status`, `timestamp` |

#### JSON Message Format

```json
{
    "type": "shimmer_data_sample",
    "timestamp": 1701435622.125,
    "device_id": "shimmer_00_06_66_66_66_66",
    "session_id": "session_20241201_143022",
    "data": {
        "gsr_conductance": 2.347,
        "ppg_a13": 1024.5,
        "accel_x": 0.12,
        "accel_y": -0.05,
        "accel_z": 9.78,
        "battery_percentage": 85,
        "signal_strength": 0.92
    }
}
```

### File Output Formats

#### CSV Data Format

The primary data files contain comprehensive sensor information with standardized timestamps:

```csv
timestamp,system_time,device_id,connection_type,session_id,
gsr_conductance,ppg_a13,accel_x,accel_y,accel_z,
gyro_x,gyro_y,gyro_z,battery_percentage,signal_strength
1701435622.125,2023-12-01T14:30:22.125Z,shimmer_00_06_66_66_66_66,direct_bluetooth,session_20241201_143022,
2.347,1024.5,0.12,-0.05,9.78,
1.2,-0.8,0.3,85,0.92
```

#### Session Metadata Format

```json
{
    "session_info": {
        "session_id": "session_20241201_143022",
        "start_time": "2023-12-01T14:30:22.125Z",
        "end_time": "2023-12-01T14:35:22.125Z",
        "duration_seconds": 300,
        "participant_id": "P001",
        "condition": "baseline"
    },
    "device_configurations": {
        "shimmer_00_06_66_66_66_66": {
            "gsr_range": 1,
            "sampling_rate": 51.2,
            "enabled_sensors": ["GSR", "PPG_A13", "ACCEL_X", "ACCEL_Y", "ACCEL_Z"],
            "firmware_version": "0.7.0",
            "battery_start": 95,
            "battery_end": 87
        }
    },
    "quality_metrics": {
        "total_samples": 15360,
        "missing_samples": 0,
        "artifact_percentage": 2.1,
        "signal_to_noise_ratio": 24.5,
        "electrode_contact_quality": "excellent"
    }
}
```

### Error Codes and Status Messages

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `SHIMMER_001` | Device not found during scan | Check Bluetooth pairing and proximity |
| `SHIMMER_002` | Connection timeout | Verify device power and Bluetooth status |
| `SHIMMER_003` | Configuration failed | Check SDK compatibility and device firmware |
| `SHIMMER_004` | Data streaming interrupted | Check connection stability and battery level |
| `SHIMMER_005` | Low battery warning | Charge device or replace battery |
| `SHIMMER_006` | Electrode disconnection | Check electrode contact and gel application |
| `SHIMMER_007` | Sampling rate error | Verify supported sampling rates for device |
| `SHIMMER_008` | Memory card full | Replace or format MicroSD card |

## Troubleshooting and Best Practices

### Common Issues and Solutions

#### Connection Problems

**Issue**: Device not discovered during scanning
- **Cause**: Bluetooth interference, device not in pairing mode, range issues
- **Solution**: 
  1. Move closer to device (< 5 meters)
  2. Reset Bluetooth adapter: `sudo systemctl restart bluetooth`
  3. Clear Bluetooth cache on Android devices
  4. Ensure device is charged and powered on

**Issue**: Connection drops during recording
- **Cause**: Power management, interference, battery depletion
- **Solution**:
  1. Disable power management for Bluetooth adapter
  2. Check battery level and replace if necessary
  3. Reduce distance between devices
  4. Implement automatic reconnection logic

#### Data Quality Issues

**Issue**: Noisy GSR signal with high variability
- **Cause**: Poor electrode contact, movement artifacts, electrical interference
- **Solution**:
  1. Re-prepare electrode sites with fresh gel
  2. Secure cables to minimize movement
  3. Check for nearby electrical equipment
  4. Increase electrode contact pressure (if comfortable)

**Issue**: Flat or unchanging GSR signal
- **Cause**: Incorrect range setting, electrode failure, device malfunction
- **Solution**:
  1. Switch to appropriate GSR range
  2. Replace electrodes and verify contact
  3. Test with different measurement sites
  4. Validate device functionality with known signals

### Best Practices

#### Experimental Design Considerations

1. **Adaptation Period**: Always include 10-15 minute adaptation period after electrode attachment
2. **Baseline Recording**: Record 5-10 minutes of baseline data before experimental manipulation
3. **Environmental Control**: Maintain consistent temperature and humidity throughout session
4. **Movement Minimization**: Instruct participants to minimize hand and arm movements
5. **Multiple Sites**: Consider bilateral measurement for comparison and artifact detection

#### Hardware Maintenance

1. **Regular Calibration**: Perform monthly calibration using known resistance values
2. **Electrode Care**: Store electrodes in humidity-controlled environment
3. **Battery Management**: Maintain charge cycles to preserve battery longevity
4. **Firmware Updates**: Regularly update device firmware for bug fixes and improvements

## Integration Examples

### Complete Recording Session Example

```python
def run_shimmer_recording_session():
    """Complete example of Shimmer recording session"""
    
    # Initialize Shimmer manager
    shimmer_manager = ShimmerManager()
    
    # Device configuration
    config = ShimmerConfig(
        sampling_rate=51.2,
        gsr_range=1,
        enable_gsr=True,
        enable_ppg=True,
        enable_accel=True
    )
    
    try:
        # Connect to device
        device_id = "shimmer_00_06_66_66_66_66"
        if not shimmer_manager.connect_device(device_id):
            raise ConnectionError("Failed to connect to Shimmer device")
        
        # Configure device
        if not shimmer_manager.configure_device(device_id, config):
            raise ConfigurationError("Failed to configure Shimmer device")
        
        # Start recording session
        session_id = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if not shimmer_manager.start_recording(session_id):
            raise RecordingError("Failed to start recording session")
        
        print(f"Recording session {session_id} started successfully")
        
        # Monitor recording for specified duration
        recording_duration = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < recording_duration:
            # Check device status
            status = shimmer_manager.get_device_status(device_id)
            if status.battery_level < 15:
                print("WARNING: Low battery level")
            
            # Assess data quality
            recent_samples = shimmer_manager.get_recent_samples(device_id, count=50)
            quality = assess_signal_quality([s.gsr_conductance for s in recent_samples])
            print(f"Signal quality: {quality}")
            
            time.sleep(10)  # Check every 10 seconds
        
        # Stop recording
        if shimmer_manager.stop_recording():
            print("Recording session completed successfully")
        
        # Generate session report
        session_stats = shimmer_manager.get_session_statistics(session_id)
        print(f"Session duration: {session_stats['duration']} seconds")
        print(f"Total samples: {session_stats['sample_count']}")
        print(f"Data files: {session_stats['output_files']}")
        
    except Exception as e:
        print(f"Recording session failed: {e}")
        shimmer_manager.stop_recording()  # Ensure cleanup
    
    finally:
        # Cleanup connections
        shimmer_manager.disconnect_all_devices()
```

### Android Integration Example

```kotlin
class ShimmerIntegrationExample {
    private val shimmerManager = ShimmerManager()
    private var currentSession: String? = null
    
    fun demonstrateShimmerIntegration() {
        lifecycleScope.launch {
            try {
                // Scan for devices
                val devices = shimmerManager.scanForDevices(timeout = 30_000)
                if (devices.isEmpty()) {
                    showError("No Shimmer devices found")
                    return@launch
                }
                
                // Connect to first available device
                val device = devices.first()
                val connected = shimmerManager.connectDevice(device.address)
                if (!connected) {
                    showError("Failed to connect to device: ${device.name}")
                    return@launch
                }
                
                // Configure device for research session
                val config = ShimmerConfig(
                    samplingRate = 51.2,
                    gsrRange = 1,
                    enabledSensors = setOf(
                        ShimmerSensor.GSR,
                        ShimmerSensor.PPG_A13,
                        ShimmerSensor.ACCEL
                    )
                )
                
                shimmerManager.configureDevice(device.address, config)
                
                // Start recording session
                currentSession = "session_${System.currentTimeMillis()}"
                shimmerManager.startRecording(currentSession!!)
                
                updateUI("Recording started: $currentSession")
                
                // Monitor session in background
                monitorRecordingSession()
                
            } catch (e: Exception) {
                Log.e("ShimmerDemo", "Integration example failed", e)
                showError("Shimmer integration failed: ${e.message}")
            }
        }
    }
    
    private suspend fun monitorRecordingSession() {
        // Collect data for demonstration
        shimmerManager.dataFlow.collect { sample ->
            // Update UI with real-time data
            updateGSRDisplay(sample.gsrConductance)
            updatePPGDisplay(sample.ppgA13)
            
            // Check data quality
            val quality = assessDataQuality(sample)
            updateQualityIndicator(quality)
        }
    }
}
```

## Performance Optimization

### Memory Management

```python
# Efficient data buffering for real-time streaming
class CircularBuffer:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.write_index = 0
        self.size = 0
    
    def add(self, item):
        self.buffer[self.write_index] = item
        self.write_index = (self.write_index + 1) % self.capacity
        if self.size < self.capacity:
            self.size += 1
    
    def get_latest(self, count: int):
        if count > self.size:
            count = self.size
        
        result = []
        for i in range(count):
            index = (self.write_index - count + i) % self.capacity
            result.append(self.buffer[index])
        
        return result
```

### Battery Optimization

```python
# Intelligent sampling rate adjustment for battery conservation
def optimize_sampling_rate(session_duration: int, battery_level: int) -> float:
    """Optimize sampling rate based on session duration and battery level"""
    
    # Base sampling rates for different scenarios
    if session_duration <= 1800:  # <= 30 minutes
        if battery_level > 50:
            return 51.2  # Standard rate
        elif battery_level > 25:
            return 25.6  # Reduced rate
        else:
            return 12.8  # Conservative rate
    
    elif session_duration <= 7200:  # <= 2 hours
        if battery_level > 75:
            return 25.6  # Moderate rate
        elif battery_level > 40:
            return 12.8  # Conservative rate
        else:
            return 6.4   # Very conservative
    
    else:  # > 2 hours
        if battery_level > 80:
            return 12.8  # Conservative rate
        else:
            return 6.4   # Very conservative rate
```

### Network Optimization

```python
# Efficient data transmission with compression
def compress_shimmer_data(samples: List[ShimmerDataSample]) -> bytes:
    """Compress Shimmer data for efficient network transmission"""
    
    # Convert to structured array for efficient compression
    data_array = np.array([
        [s.timestamp, s.gsr_conductance, s.ppg_a13 or 0, 
         s.accel_x or 0, s.accel_y or 0, s.accel_z or 0]
        for s in samples
    ])
    
    # Use delta encoding for timestamps
    if len(data_array) > 1:
        data_array[1:, 0] = np.diff(data_array[:, 0])
    
    # Compress using zlib
    compressed = zlib.compress(data_array.tobytes())
    
    return compressed
```

This comprehensive guide provides all necessary information for integrating the Shimmer3 GSR+ device within the Multi-Sensor Recording System, covering hardware setup, software implementation, data processing, protocol specifications, and optimization strategies for research-grade physiological data collection.
