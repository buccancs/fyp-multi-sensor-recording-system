# Shimmer3 GSR+ Device: Practical User Guide

## Overview

This practical guide provides step-by-step instructions for researchers and developers to effectively use the Shimmer3 GSR+ device within the Multi-Sensor Recording System. The guide covers device setup, configuration, data collection, and analysis workflows designed for research applications requiring high-quality physiological data collection.

The Shimmer3 GSR+ enables precise measurement of galvanic skin response (GSR), photoplethysmography (PPG), and motion data, making it ideal for studies involving emotional responses, stress monitoring, and psychophysiological research.

## Pre-flight Checklist

Before beginning any recording session with the Shimmer3 GSR+, ensure all prerequisites are met to guarantee successful data collection:

### Hardware Requirements

- [ ] **Shimmer3 GSR+ Device**: Fully charged (battery level > 20%)
- [ ] **Electrode Gel**: Conductive gel for optimal skin contact
- [ ] **Skin Preparation Materials**: Alcohol wipes for electrode site cleaning
- [ ] **Shimmer Docking Station**: For device charging and data transfer
- [ ] **MicroSD Card**: Formatted and inserted (for on-device logging)
- [ ] **Bluetooth-Enabled Device**: PC with Bluetooth adapter or Android smartphone

### Software Prerequisites

- [ ] **Multi-Sensor Recording System**: Installed and configured
- [ ] **Shimmer SDK**: pyshimmer library (PC) or Shimmer Android API
- [ ] **Bluetooth Permissions**: Location and Bluetooth permissions granted (Android)
- [ ] **Device Pairing**: Shimmer3 device paired in system Bluetooth settings

### Environmental Considerations

- [ ] **Ambient Temperature**: 18-25°C (optimal for stable measurements)
- [ ] **Humidity Level**: 40-60% relative humidity (prevents electrode drying)
- [ ] **Electromagnetic Interference**: Minimal WiFi/cellular interference
- [ ] **Movement Constraints**: Stable environment for motion-sensitive measurements

## Step-by-Step Setup Guide

### Step 1: Device Preparation and Placement

#### 1.1 Device Inspection and Charging

1. **Visual Inspection**: Check device for physical damage, loose connections, or battery swelling
2. **Battery Check**: Verify battery level using device LED indicators or software interface
3. **Charging Protocol**: If battery level < 20%, charge for minimum 2 hours using official docking station
4. **Firmware Verification**: Confirm latest firmware version for optimal compatibility

#### 1.2 Electrode Preparation

1. **Skin Site Selection**: Choose appropriate measurement locations:
   - **Preferred**: Index and middle finger distal phalanges (dominant hand)
   - **Alternative**: Palm sites (thenar and hypothenar eminences)
   - **Avoid**: Areas with visible damage, excessive hair, or jewelry contact

2. **Skin Preparation Protocol**:
   ```
   Step 1: Clean electrode sites with alcohol wipe
   Step 2: Wait 30 seconds for complete evaporation
   Step 3: Gently abrade skin with fine-grit emery paper (optional)
   Step 4: Apply thin layer of conductive electrode gel
   Step 5: Attach electrodes ensuring complete skin contact
   ```

#### 1.3 Device Mounting and Positioning

1. **Secure Attachment**: Use provided straps or adhesive mounts
2. **Cable Management**: Route cables to minimize movement artifacts
3. **Positioning Verification**: Ensure electrodes maintain consistent skin contact
4. **Participant Comfort**: Verify no discomfort or circulation restriction

### Step 2: Software Configuration

#### 2.1 PC-Based Setup (Direct Connection)

For direct PC connections using the pyshimmer library:

```bash
# Activate Python environment
conda activate thermal-env

# Navigate to application directory
cd PythonApp

# Launch desktop application with Shimmer support
python src/application.py --enable-shimmer
```

**Connection Process**:
1. Open Shimmer Manager interface
2. Click "Scan for Devices" to detect available Shimmer3 devices
3. Select target device from discovered list
4. Verify connection status indicator shows "Connected"
5. Proceed to sensor configuration

#### 2.2 Android-Based Setup (Mediated Connection)

For Android-mediated connections using the Shimmer Android API:

1. **Launch Android Application**:
   - Open Multi-Sensor Recording app
   - Navigate to "Devices" tab
   - Select "Shimmer Configuration"

2. **Device Discovery**:
   - Tap "Scan for Shimmer Devices"
   - Wait for device list to populate (30-60 seconds)
   - Select target Shimmer3 GSR+ from list
   - Confirm pairing request in Android Bluetooth settings

3. **Connection Verification**:
   - Monitor connection status in app interface
   - Verify green indicator for successful connection
   - Check device information display for firmware version

#### 2.3 Hybrid Setup (PC + Android Coordination)

For multi-device setups combining PC and Android connections:

1. **PC Server Initialization**:
   ```bash
   # Start PC server for Android coordination
   python src/application.py --server-mode --port 9000
   ```

2. **Android Client Connection**:
   - Enter PC IP address in Android app settings
   - Verify socket connection status
   - Confirm bidirectional communication

3. **Device Coordination**:
   - Assign unique device IDs for each Shimmer3 unit
   - Synchronize clocks across all devices
   - Test communication paths before recording

### Step 3: Sensor Configuration

#### 3.1 GSR Range Selection

Select appropriate GSR measurement range based on participant characteristics and study requirements:

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

**Range Selection Guidelines**:
- **Range 0**: Use for high-stress paradigms, emotional induction studies
- **Range 1**: Standard setting for most research applications
- **Range 2**: Recommended for older adults, low-humidity conditions
- **Range 3**: Clinical populations, medications affecting skin conductance
- **Range 4**: Exploratory studies, unknown participant characteristics

#### 3.2 Sampling Rate Configuration

Configure sampling rate based on research requirements and battery life considerations:

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

#### 3.3 Multi-Sensor Configuration

Enable additional sensors based on research requirements:

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

### Step 4: Data Collection Workflow

#### 4.1 Pre-Recording Setup

1. **Baseline Period Configuration**:
   ```python
   # Configure baseline recording parameters
   baseline_config = {
       "duration": 300,  # 5 minutes baseline
       "sampling_rate": 51.2,
       "gsr_range": 1,
       "enabled_sensors": {"GSR", "PPG_A13"}
   }
   ```

2. **Participant Preparation**:
   - Allow 10-15 minutes adaptation period after electrode attachment
   - Instruct participant on movement restrictions
   - Verify comfortable positioning and electrode contact
   - Begin with 5-minute baseline recording for signal stabilization

#### 4.2 Recording Session Management

**Session Initialization**:
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

**Real-Time Monitoring**:
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

#### 4.3 Session Termination

**Proper Recording Termination**:
```python
# Stop recording session
stop_success = shimmer_manager.stop_recording()

if stop_success:
    # Generate session summary
    session_stats = shimmer_manager.get_session_statistics(session_id)
    print(f"Session completed: {session_stats['duration']} seconds")
    print(f"Total samples: {session_stats['sample_count']}")
    print(f"Data files: {session_stats['output_files']}")
else:
    print("Error stopping recording - manual file closure may be required")
```

### Step 5: Data Quality Assessment

#### 5.1 Real-Time Quality Monitoring

```python
# Implement real-time quality assessment
def assess_signal_quality(samples):
    """
    Assess GSR signal quality in real-time
    """
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

#### 5.2 Post-Recording Validation

```python
# Post-session data validation
def validate_session_data(session_id):
    """
    Comprehensive post-recording data validation
    """
    data_files = get_session_files(session_id)
    validation_results = {}
    
    for file_path in data_files:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            
            validation_results[file_path] = {
                "total_samples": len(df),
                "missing_values": df.isnull().sum().sum(),
                "duplicate_timestamps": df.duplicated(subset=['timestamp']).sum(),
                "gsr_range": [df['gsr_conductance'].min(), df['gsr_conductance'].max()],
                "sampling_rate_consistency": check_sampling_rate(df['timestamp'])
            }
    
    return validation_results
```

## Expected Output and Results

### File Structure

Each recording session generates a comprehensive set of data files organized in a structured directory hierarchy:

```
recordings/
└── session_20241201_143022/
    ├── metadata/
    │   ├── session_info.json
    │   ├── device_configurations.json
    │   └── quality_assessment.json
    ├── shimmer/
    │   ├── shimmer_00_06_66_66_66_66_data.csv
    │   ├── shimmer_00_06_66_66_66_67_data.csv
    │   └── shimmer_quality_metrics.json
    └── synchronized/
        ├── merged_timeline.csv
        └── synchronization_report.json
```

### CSV Data Format

The primary data files contain comprehensive sensor information with standardized timestamps:

```csv
timestamp,system_time,device_id,connection_type,session_id,
gsr_conductance,ppg_a13,accel_x,accel_y,accel_z,
gyro_x,gyro_y,gyro_z,battery_percentage,signal_strength
1701435622.125,2023-12-01T14:30:22.125Z,shimmer_00_06_66_66_66_66,direct_bluetooth,session_20241201_143022,
2.347,1024.5,0.12,-0.05,9.78,
1.2,-0.8,0.3,85,0.92
```

### JSON Metadata Format

Session metadata provides comprehensive recording context and quality metrics:

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

## Troubleshooting Guide

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

#### Software Configuration Problems

**Issue**: Permission denied errors on Android
- **Cause**: Missing Bluetooth or location permissions
- **Solution**:
  1. Grant all requested permissions in Android settings
  2. Enable location services for Bluetooth LE scanning
  3. Add app to battery optimization whitelist
  4. Restart application after permission changes

**Issue**: Python library import errors
- **Cause**: Missing dependencies, incorrect environment
- **Solution**:
  1. Verify conda environment activation: `conda activate thermal-env`
  2. Install missing packages: `pip install pyshimmer bluetooth`
  3. Check Python version compatibility (3.8+)
  4. Update dependencies: `conda env update -f environment.yml`

## Best Practices and Recommendations

### Experimental Design Considerations

1. **Adaptation Period**: Always include 10-15 minute adaptation period after electrode attachment
2. **Baseline Recording**: Record 5-10 minutes of baseline data before experimental manipulation
3. **Environmental Control**: Maintain consistent temperature and humidity throughout session
4. **Movement Minimization**: Instruct participants to minimize hand and arm movements
5. **Multiple Sites**: Consider bilateral measurement for comparison and artifact detection

### Data Analysis Workflow

1. **Pre-processing Pipeline**:
   ```python
   # Standard GSR pre-processing steps
   def preprocess_gsr_data(raw_data):
       # 1. Remove obvious artifacts (> 3 SD from mean)
       cleaned_data = remove_artifacts(raw_data)
       
       # 2. Apply low-pass filter (1 Hz cutoff for GSR)
       filtered_data = butter_lowpass_filter(cleaned_data, 1.0, 51.2)
       
       # 3. Decompose into tonic and phasic components
       tonic, phasic = decompose_gsr(filtered_data)
       
       # 4. Identify skin conductance responses (SCRs)
       scr_peaks = detect_scr_peaks(phasic)
       
       return {
           'tonic': tonic,
           'phasic': phasic,
           'scr_peaks': scr_peaks,
           'quality_score': calculate_quality_score(filtered_data)
       }
   ```

2. **Statistical Analysis Considerations**:
   - Account for individual differences in baseline GSR levels
   - Use appropriate transformations (log, square-root) for non-normal distributions
   - Consider time-series analysis methods for temporal dynamics
   - Validate results with multiple measurement sessions

### Hardware Maintenance

1. **Regular Calibration**: Perform monthly calibration using known resistance values
2. **Electrode Care**: Store electrodes in humidity-controlled environment
3. **Battery Management**: Maintain charge cycles to preserve battery longevity
4. **Firmware Updates**: Regularly update device firmware for bug fixes and improvements

## Integration with Analysis Software

### R Integration

```r
# Load and analyze Shimmer GSR data in R
library(readr)
library(dplyr)
library(ggplot2)

# Read session data
shimmer_data <- read_csv("recordings/session_20241201_143022/shimmer/shimmer_00_06_66_66_66_66_data.csv")

# Basic analysis
gsr_summary <- shimmer_data %>%
  summarise(
    mean_gsr = mean(gsr_conductance, na.rm = TRUE),
    sd_gsr = sd(gsr_conductance, na.rm = TRUE),
    min_gsr = min(gsr_conductance, na.rm = TRUE),
    max_gsr = max(gsr_conductance, na.rm = TRUE),
    scr_count = count_scr_peaks(gsr_conductance)
  )

# Visualization
ggplot(shimmer_data, aes(x = timestamp, y = gsr_conductance)) +
  geom_line() +
  labs(title = "GSR Time Series", x = "Time", y = "Conductance (μS)")
```

### MATLAB Integration

```matlab
% Load and analyze Shimmer GSR data in MATLAB
shimmer_data = readtable('recordings/session_20241201_143022/shimmer/shimmer_00_06_66_66_66_66_data.csv');

% Extract GSR signal
gsr_signal = shimmer_data.gsr_conductance;
sampling_rate = 51.2; % Hz

% Apply signal processing
[b, a] = butter(4, 1/(sampling_rate/2), 'low'); % 1 Hz lowpass filter
gsr_filtered = filtfilt(b, a, gsr_signal);

% Decompose into tonic and phasic components
tonic_component = smooth(gsr_filtered, 0.1, 'loess');
phasic_component = gsr_filtered - tonic_component;

% Identify skin conductance responses
[scr_peaks, scr_times] = findpeaks(phasic_component, 'MinPeakHeight', 0.05);

% Visualization
figure;
subplot(2,1,1);
plot(shimmer_data.timestamp, gsr_filtered);
title('Filtered GSR Signal');
xlabel('Time'); ylabel('Conductance (μS)');

subplot(2,1,2);
plot(shimmer_data.timestamp, phasic_component);
hold on;
plot(scr_times, scr_peaks, 'ro');
title('Phasic GSR with SCR Peaks');
xlabel('Time'); ylabel('Conductance (μS)');
```

## Testing and Validation

### Android Integration Testing

For comprehensive testing of the Android Shimmer integration:

```bash
# Run enhanced test suite for Shimmer recorder
./gradlew testDebugUnitTest --tests "ShimmerRecorderEnhancedTest"

# Run integration tests with real hardware
./gradlew connectedAndroidTest --tests "ShimmerIntegrationTest"
```

### Hardware Validation Steps

1. **Device Connection Test**: Verify Bluetooth pairing and communication
2. **Sensor Configuration Test**: Confirm all sensor channels respond correctly  
3. **Data Quality Validation**: Check signal ranges and sampling rates
4. **Session Recording Test**: Verify CSV file generation and data integrity

### Performance Validation

```kotlin
// Memory management for real-time data streaming
class CircularBuffer<T>(private val capacity: Int) {
    private val buffer = arrayOfNulls<Any>(capacity) as Array<T?>
    private var writeIndex = 0
    private var size = 0
    
    fun add(item: T) {
        buffer[writeIndex] = item
        writeIndex = (writeIndex + 1) % capacity
        if (size < capacity) size++
    }
    
    fun getLatest(count: Int): List<T> {
        val result = mutableListOf<T>()
        val startIdx = if (size < capacity) 0 else writeIndex
        for (i in 0 until minOf(count, size)) {
            val idx = (startIdx + size - count + i) % capacity
            buffer[idx]?.let { result.add(it) }
        }
        return result
    }
}
```

### Version Compatibility

- **Shimmer SDK**: 3.2.3_beta
- **Android API**: 24+ (Android 7.0)  
- **Bluetooth**: Classic and BLE support
- **Java**: 17+ compatibility

This comprehensive user guide provides researchers with the practical knowledge needed to effectively utilize the Shimmer3 GSR+ device for high-quality physiological data collection. Following these procedures ensures reliable data collection, proper device management, and successful integration with analysis workflows.