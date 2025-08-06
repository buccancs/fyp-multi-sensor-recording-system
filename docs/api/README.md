# API Documentation

## Overview

This directory contains comprehensive API documentation for the Multi-Sensor Recording System.

## Components

### Python Desktop Controller APIs

#### Core Modules
- **CalibrationManager**: Camera calibration and validation APIs
- **SessionManager**: Recording session coordination APIs  
- **ShimmerManager**: Shimmer GSR sensor management APIs
- **PCServer**: Network communication server APIs
- **AndroidDeviceManager**: Android device integration APIs

#### Calibration APIs
```python
class CalibrationManager:
    def perform_complete_calibration(self, rgb_images: List[np.ndarray], 
                                   thermal_images: List[np.ndarray]) -> CalibrationResult
    def save_calibration_results(self, result: CalibrationResult, output_path: str) -> bool
    def load_calibration_results(self, file_path: str) -> Optional[CalibrationResult]
```

#### Session Management APIs
```python
class SessionManager:
    def create_session(self, session_config: Dict) -> str
    def start_recording(self, session_id: str) -> bool
    def stop_recording(self, session_id: str) -> bool
    def get_session_status(self, session_id: str) -> SessionStatus
```

#### Network Communication APIs
```python
class PCServer:
    def start_server(self, port: int = 8080) -> bool
    def stop_server(self) -> bool
    def send_command(self, device_id: str, command: JsonMessage) -> bool
    def broadcast_command(self, command: JsonMessage) -> Dict[str, bool]
```

### Android Application APIs

#### Recording Controllers
- **RecordingSessionController**: Pure recording operation management
- **DeviceConnectionManager**: Device connectivity orchestration
- **FileTransferManager**: Data transfer operations
- **CalibrationManager**: Calibration process coordination

#### Network Communication
```kotlin
class NetworkClient {
    fun connect(serverAddress: String, port: Int): Boolean
    fun sendMessage(message: JsonMessage): Boolean
    fun registerMessageHandler(handler: MessageHandler)
    fun disconnect()
}
```

#### Recording Components
```kotlin
class CameraRecorder {
    fun startRecording(config: RecordingConfig): Boolean
    fun stopRecording(): Boolean
    fun getRecordingStatus(): RecordingStatus
}

class ThermalRecorder {
    fun initialize(config: ThermalConfig): Boolean
    fun startCapture(): Boolean
    fun stopCapture(): Boolean
}
```

## Communication Protocol

### JSON Message Format
```json
{
    "type": "command|response|notification",
    "timestamp": 1234567890.123,
    "session_id": "session_uuid",
    "device_id": "device_identifier",
    "payload": {
        "command": "start_recording|stop_recording|calibrate",
        "parameters": {}
    }
}
```

### WebSocket Events
- **device_connected**: New device joins network
- **device_disconnected**: Device leaves network  
- **recording_started**: Recording session begins
- **recording_stopped**: Recording session ends
- **calibration_complete**: Calibration process finished
- **error_occurred**: Error condition detected

## Data Formats

### Calibration Data
```json
{
    "calibration_id": "cal_uuid",
    "timestamp": "2024-01-01T12:00:00Z",
    "rgb_camera_matrix": [[fx, 0, cx], [0, fy, cy], [0, 0, 1]],
    "rgb_distortion_coeffs": [k1, k2, p1, p2, k3],
    "thermal_camera_matrix": [[fx, 0, cx], [0, fy, cy], [0, 0, 1]],
    "thermal_distortion_coeffs": [k1, k2, p1, p2, k3],
    "stereo_parameters": {
        "rotation_matrix": [[r11, r12, r13], [r21, r22, r23], [r31, r32, r33]],
        "translation_vector": [tx, ty, tz]
    }
}
```

### Recording Session Data
```json
{
    "session_id": "session_uuid",
    "start_time": "2024-01-01T12:00:00Z",
    "end_time": "2024-01-01T12:30:00Z",
    "devices": [
        {
            "device_id": "device_uuid",
            "device_type": "android|shimmer|thermal",
            "data_files": ["file1.csv", "file2.mp4"],
            "calibration_id": "cal_uuid"
        }
    ],
    "synchronization_data": {
        "master_timestamps": [1234567890.123, 1234567890.456],
        "device_offsets": {"device1": 0.001, "device2": -0.002}
    }
}
```

## Error Handling

### Error Response Format
```json
{
    "type": "error",
    "timestamp": 1234567890.123,
    "error_code": "DEVICE_NOT_FOUND|CALIBRATION_FAILED|NETWORK_ERROR",
    "error_message": "Human readable error description",
    "details": {
        "device_id": "device_identifier",
        "additional_context": "Specific error details"
    }
}
```

### Common Error Codes
- **DEVICE_NOT_FOUND**: Requested device not available
- **CALIBRATION_FAILED**: Camera calibration process failed
- **NETWORK_ERROR**: Communication failure between components
- **RECORDING_ERROR**: Error during data recording
- **VALIDATION_ERROR**: Data validation failure

## Usage Examples

### Python Desktop Controller
```python
# Initialize system components
calibration_manager = CalibrationManager()
session_manager = SessionManager()
pc_server = PCServer()

# Start network server
pc_server.start_server(port=8080)

# Create and start recording session
session_id = session_manager.create_session({
    "duration": 300,  # 5 minutes
    "devices": ["android_device_1", "shimmer_device_1"]
})
session_manager.start_recording(session_id)
```

### Android Application
```kotlin
// Initialize recording components
val networkClient = NetworkClient()
val cameraRecorder = CameraRecorder()
val thermalRecorder = ThermalRecorder()

// Connect to PC controller
networkClient.connect("192.168.1.100", 8080)

// Start recording when commanded
networkClient.registerMessageHandler { message ->
    when (message.payload.command) {
        "start_recording" -> {
            cameraRecorder.startRecording(message.payload.parameters)
            thermalRecorder.startCapture()
        }
        "stop_recording" -> {
            cameraRecorder.stopRecording()
            thermalRecorder.stopCapture()
        }
    }
}
```

For complete API reference and additional examples, see the individual component documentation files.