# DeviceClient Protocol Specification v2.0

## Document Information

- **Version**: 2.0
- **Date**: January 2025
- **Authors**: Multi-Sensor Recording System Team
- **Classification**: Technical Specification
- **Status**: Active Development

## 1. Executive Summary

This document specifies the DeviceClient communication protocol for the Multi-Sensor Recording System. The protocol defines a comprehensive framework for reliable, secure, and scalable communication between Android recording devices and central controllers.

### 1.1 Protocol Scope

The DeviceClient protocol encompasses:
- Connection establishment and authentication
- Command execution with acknowledgment support
- Real-time data streaming
- Device capability negotiation
- Performance monitoring and error handling
- Security through SSL/TLS encryption

### 1.2 Compliance Requirements

Implementations MUST support all mandatory features marked with RFC 2119 keywords (MUST, SHALL, REQUIRED). Optional features are marked with MAY, SHOULD, or RECOMMENDED.

## 2. Protocol Architecture

### 2.1 Network Model

The protocol operates on a client-server architecture where:
- **Server**: Central controller (DeviceClient instance)
- **Client**: Android recording device
- **Transport**: TCP/IP with optional SSL/TLS encryption
- **Encoding**: UTF-8 JSON messages

### 2.2 Connection Lifecycle

```
Device                    Controller
  |                          |
  |-------- TCP Connect ---->|
  |<------- TCP Accept ------|
  |                          |
  |-------- Handshake ------>|
  |<------ Handshake Ack ----|
  |                          |
  |<===== Data Exchange ====>|
  |                          |
  |------- Disconnect ------>|
  |<------ Disconnect Ack ---|
  |                          |
  |-------- TCP Close ------>|
```

## 3. Message Format Specification

### 3.1 Base Message Structure

All protocol messages MUST conform to the following JSON schema:

```json
{
  "type": {
    "type": "string",
    "enum": ["handshake", "command", "acknowledgment", "frame", "status", "heartbeat", "disconnect", "error", "capability_negotiation", "capability_response"],
    "description": "Message type identifier"
  },
  "timestamp": {
    "type": "number",
    "description": "Unix timestamp in seconds with microsecond precision"
  },
  "message_id": {
    "type": "string",
    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    "description": "UUID v4 unique message identifier"
  },
  "version": {
    "type": "string",
    "default": "2.0",
    "description": "Protocol version"
  }
}
```

### 3.2 Message Size Constraints

- **Maximum message size**: 1 MB (1,048,576 bytes)
- **Recommended message size**: < 64 KB for optimal performance
- **Minimum message size**: 32 bytes (base structure)

### 3.3 Timestamp Format

Timestamps MUST be represented as Unix time in seconds with microsecond precision:
```
timestamp = seconds_since_epoch + (microseconds / 1_000_000)
```

Example: `1672531200.123456` represents January 1, 2023 00:00:00.123456 UTC

## 4. Protocol Messages

### 4.1 Handshake Messages

#### 4.1.1 Client Handshake Request

```json
{
  "type": "handshake",
  "timestamp": 1672531200.123456,
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "version": "2.0",
  "client_type": "android_recording_device",
  "device_info": {
    "model": "Samsung Galaxy S21",
    "os_version": "Android 12",
    "app_version": "1.2.3",
    "hardware_id": "device_unique_identifier"
  },
  "capabilities": ["recording", "streaming", "thermal_imaging", "gsr_monitoring"],
  "supported_features": {
    "compression": ["gzip", "lz4"],
    "encryption": ["none", "aes256"],
    "protocols": ["json", "binary"]
  }
}
```

#### 4.1.2 Server Handshake Response

```json
{
  "type": "handshake",
  "timestamp": 1672531200.234567,
  "message_id": "550e8400-e29b-41d4-a716-446655440001",
  "version": "2.0",
  "status": "accepted",
  "server_info": {
    "type": "recording_controller",
    "version": "2.0.1",
    "session_id": "session_12345"
  },
  "negotiated_capabilities": ["recording", "streaming", "thermal_imaging"],
  "configuration": {
    "heartbeat_interval": 5,
    "timeout_seconds": 30,
    "max_frame_size": 1048576,
    "compression": "gzip",
    "acknowledgment_required": true
  }
}
```

### 4.2 Command Messages

#### 4.2.1 Command Request

```json
{
  "type": "command",
  "timestamp": 1672531200.345678,
  "message_id": "550e8400-e29b-41d4-a716-446655440002",
  "version": "2.0",
  "command": "START_RECORDING",
  "parameters": {
    "mode": "synchronized",
    "duration": 300,
    "sensors": ["gsr", "thermal", "audio"],
    "sample_rate": 1000,
    "output_format": "json",
    "metadata": {
      "participant_id": "P001",
      "session_type": "experiment"
    }
  },
  "require_ack": true,
  "priority": "high",
  "timeout": 10
}
```

#### 4.2.2 Command Acknowledgment

```json
{
  "type": "acknowledgment",
  "timestamp": 1672531200.456789,
  "message_id": "550e8400-e29b-41d4-a716-446655440003",
  "version": "2.0",
  "ack_message_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "success",
  "result": {
    "recording_started": true,
    "session_id": "rec_001",
    "estimated_completion": 1672531500.0
  }
}
```

### 4.3 Data Frame Messages

#### 4.3.1 Sensor Data Frame

```json
{
  "type": "frame",
  "timestamp": 1672531200.567890,
  "message_id": "550e8400-e29b-41d4-a716-446655440004",
  "version": "2.0",
  "frame_type": "gsr_data",
  "sequence_number": 12345,
  "session_id": "rec_001",
  "metadata": {
    "sensor_id": "gsr_sensor_1",
    "sample_rate": 1000,
    "units": "microsiemens",
    "calibration_applied": true
  },
  "data": {
    "values": [0.523, 0.534, 0.541, 0.529],
    "timestamps": [1672531200.567, 1672531200.568, 1672531200.569, 1672531200.570]
  },
  "compression": "none",
  "checksum": "sha256:a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
}
```

#### 4.3.2 Image Frame

```json
{
  "type": "frame",
  "timestamp": 1672531200.678901,
  "message_id": "550e8400-e29b-41d4-a716-446655440005",
  "version": "2.0",
  "frame_type": "thermal_image",
  "sequence_number": 67890,
  "session_id": "rec_001",
  "metadata": {
    "width": 640,
    "height": 480,
    "format": "RGB",
    "color_depth": 24,
    "compression": "jpeg",
    "quality": 85
  },
  "data": "base64_encoded_image_data_here",
  "compression": "gzip",
  "size_bytes": 45678,
  "checksum": "sha256:b775a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
}
```

### 4.4 Status and Monitoring Messages

#### 4.4.1 Device Status

```json
{
  "type": "status",
  "timestamp": 1672531200.789012,
  "message_id": "550e8400-e29b-41d4-a716-446655440006",
  "version": "2.0",
  "device_status": "recording",
  "session_id": "rec_001",
  "battery_level": 85,
  "storage": {
    "available_mb": 1024,
    "used_mb": 256,
    "total_mb": 1280
  },
  "sensors": {
    "gsr": {
      "status": "active",
      "sample_rate": 1000,
      "last_reading": 0.523,
      "calibration_status": "calibrated"
    },
    "thermal": {
      "status": "active",
      "temperature": 25.3,
      "resolution": "640x480",
      "frame_rate": 30
    }
  },
  "network": {
    "signal_strength": -45,
    "connection_type": "wifi",
    "bandwidth_mbps": 100
  }
}
```

#### 4.4.2 Heartbeat

```json
{
  "type": "heartbeat",
  "timestamp": 1672531200.890123,
  "message_id": "550e8400-e29b-41d4-a716-446655440007",
  "version": "2.0",
  "device_id": "device_unique_identifier",
  "uptime_seconds": 3600,
  "message_count": 12345
}
```

### 4.5 Capability Negotiation

#### 4.5.1 Capability Request

```json
{
  "type": "capability_negotiation",
  "timestamp": 1672531200.901234,
  "message_id": "550e8400-e29b-41d4-a716-446655440008",
  "version": "2.0",
  "requested_capabilities": ["recording", "streaming", "thermal_imaging", "gsr_monitoring"],
  "supported_capabilities": ["recording", "streaming", "thermal_imaging", "gsr_monitoring", "audio_capture"],
  "feature_requirements": {
    "compression": "required",
    "encryption": "optional",
    "real_time_streaming": "required"
  }
}
```

#### 4.5.2 Capability Response

```json
{
  "type": "capability_response",
  "timestamp": 1672531201.012345,
  "message_id": "550e8400-e29b-41d4-a716-446655440009",
  "version": "2.0",
  "capabilities": ["recording", "streaming", "thermal_imaging"],
  "feature_support": {
    "compression": ["gzip", "lz4"],
    "encryption": ["aes256"],
    "real_time_streaming": true,
    "max_concurrent_streams": 3
  },
  "limitations": {
    "max_frame_rate": 30,
    "max_resolution": "1920x1080",
    "max_session_duration": 7200
  }
}
```

### 4.6 Error Messages

#### 4.6.1 Protocol Error

```json
{
  "type": "error",
  "timestamp": 1672531201.123456,
  "message_id": "550e8400-e29b-41d4-a716-446655440010",
  "version": "2.0",
  "error_code": "PROTOCOL_VIOLATION",
  "error_message": "Invalid message format: missing required field 'timestamp'",
  "severity": "error",
  "related_message_id": "550e8400-e29b-41d4-a716-446655440002",
  "recovery_suggestion": "Ensure all required fields are present in message",
  "additional_info": {
    "expected_schema": "https://schema.example.com/device_client_v2.json",
    "validation_errors": ["Missing required property: timestamp"]
  }
}
```

## 5. Security Specifications

### 5.1 SSL/TLS Configuration

#### 5.1.1 Required TLS Versions
- **Minimum Version**: TLS 1.2
- **Recommended Version**: TLS 1.3
- **Deprecated Versions**: SSLv3, TLS 1.0, TLS 1.1 (MUST NOT be used)

#### 5.1.2 Cipher Suites
```
Recommended Cipher Suites (in order of preference):
1. TLS_AES_256_GCM_SHA384 (TLS 1.3)
2. TLS_AES_128_GCM_SHA256 (TLS 1.3)
3. ECDHE-RSA-AES256-GCM-SHA384 (TLS 1.2)
4. ECDHE-RSA-AES128-GCM-SHA256 (TLS 1.2)
```

#### 5.1.3 Certificate Requirements
- **Algorithm**: RSA-2048 or ECDSA P-256 minimum
- **Validity**: Maximum 1 year for production
- **Subject Alternative Names**: MUST include all server hostnames/IPs
- **Extended Key Usage**: Server Authentication, Client Authentication

### 5.2 Authentication Mechanisms

#### 5.2.1 Device Authentication
```json
{
  "authentication": {
    "method": "certificate",
    "certificate_chain": ["device_cert.pem", "intermediate_ca.pem"],
    "private_key": "device_private_key.pem"
  }
}
```

#### 5.2.2 Token-Based Authentication (Alternative)
```json
{
  "authentication": {
    "method": "token",
    "token_type": "bearer",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "def50200a54b...",
    "expires_in": 3600
  }
}
```

## 6. Performance Requirements

### 6.1 Latency Specifications

| Operation | Target Latency | Maximum Latency |
|-----------|---------------|-----------------|
| Handshake | < 50ms | 100ms |
| Command ACK | < 15ms | 30ms |
| Frame Delivery | < 10ms | 25ms |
| Heartbeat | < 5ms | 10ms |

### 6.2 Throughput Requirements

| Metric | Minimum | Target | Maximum |
|--------|---------|--------|---------|
| Concurrent Devices | 10 | 50 | 100 |
| Messages/Second | 500 | 1200 | 2000 |
| Data Throughput | 5 MB/s | 15 MB/s | 30 MB/s |
| Connection Setup Rate | 5/s | 10/s | 20/s |

### 6.3 Reliability Metrics

- **Message Delivery Success Rate**: ≥ 99.9%
- **Connection Uptime**: ≥ 99.5%
- **Error Recovery Time**: < 10 seconds
- **Maximum Retry Attempts**: 3

## 7. Quality of Service (QoS)

### 7.1 Message Priorities

```json
{
  "priority_levels": {
    "critical": {
      "level": 0,
      "examples": ["emergency_stop", "safety_alert"],
      "max_latency": "1ms",
      "retry_attempts": 5
    },
    "high": {
      "level": 1,
      "examples": ["start_recording", "stop_recording"],
      "max_latency": "10ms",
      "retry_attempts": 3
    },
    "normal": {
      "level": 2,
      "examples": ["data_frame", "status_update"],
      "max_latency": "50ms",
      "retry_attempts": 2
    },
    "low": {
      "level": 3,
      "examples": ["heartbeat", "log_message"],
      "max_latency": "100ms",
      "retry_attempts": 1
    }
  }
}
```

### 7.2 Flow Control

#### 7.2.1 Rate Limiting
- **Default Rate Limit**: 60 requests per minute per IP
- **Burst Allowance**: 10 requests per 10-second window
- **Backoff Strategy**: Exponential backoff with jitter

#### 7.2.2 Congestion Control
```python
def calculate_backoff_delay(attempt_number, base_delay=1.0, max_delay=30.0):
    """Calculate exponential backoff with jitter"""
    delay = min(base_delay * (2 ** attempt_number), max_delay)
    jitter = random.uniform(0, 0.1 * delay)
    return delay + jitter
```

## 8. Error Handling and Recovery

### 8.1 Error Classification

#### 8.1.1 Connection Errors
- **CONN_TIMEOUT**: Connection establishment timeout
- **CONN_REFUSED**: Connection refused by server
- **CONN_LOST**: Connection lost during operation
- **CONN_RESET**: Connection reset by peer

#### 8.1.2 Protocol Errors
- **INVALID_MESSAGE**: Malformed JSON or missing fields
- **UNSUPPORTED_VERSION**: Protocol version mismatch
- **AUTHENTICATION_FAILED**: Authentication credentials invalid
- **CAPABILITY_MISMATCH**: Required capabilities not supported

#### 8.1.3 Application Errors
- **SENSOR_ERROR**: Hardware sensor malfunction
- **STORAGE_FULL**: Insufficient storage space
- **BATTERY_LOW**: Device battery critically low
- **RESOURCE_UNAVAILABLE**: Required resource not available

### 8.2 Recovery Strategies

#### 8.2.1 Automatic Recovery
```json
{
  "recovery_policies": {
    "connection_lost": {
      "action": "reconnect",
      "max_attempts": 5,
      "backoff_strategy": "exponential",
      "base_delay": 1.0
    },
    "message_timeout": {
      "action": "retry",
      "max_attempts": 3,
      "timeout_multiplier": 2.0
    },
    "authentication_failed": {
      "action": "refresh_credentials",
      "fallback": "manual_intervention"
    }
  }
}
```

## 9. Implementation Guidelines

### 9.1 Message Validation

All implementations MUST validate incoming messages against the protocol schema:

```python
def validate_message(message):
    """Validate message against protocol specification"""
    required_fields = ['type', 'timestamp', 'message_id', 'version']
    
    for field in required_fields:
        if field not in message:
            raise ProtocolError(f"Missing required field: {field}")
    
    if not is_valid_uuid(message['message_id']):
        raise ProtocolError("Invalid message_id format")
    
    if message['version'] != '2.0':
        raise ProtocolError("Unsupported protocol version")
    
    return True
```

### 9.2 Threading Considerations

#### 9.2.1 Thread Safety
- All device state modifications MUST be protected by locks
- Message queues SHOULD use thread-safe implementations
- Socket operations MUST handle concurrent access properly

#### 9.2.2 Resource Management
```python
def safe_device_operation(device_id, operation):
    """Thread-safe device operation wrapper"""
    with device_lock:
        if device_id not in devices:
            raise DeviceNotFoundError(f"Device {device_id} not found")
        
        try:
            return operation(devices[device_id])
        except Exception as e:
            logger.error(f"Operation failed for device {device_id}: {e}")
            raise
```

## 10. Testing and Validation

### 10.1 Unit Test Requirements

Implementations MUST include tests for:
- Message serialization/deserialization
- Protocol state transitions
- Error handling scenarios
- Security mechanisms
- Performance benchmarks

### 10.2 Integration Test Scenarios

```python
test_scenarios = [
    "normal_handshake_flow",
    "handshake_failure_recovery",
    "command_acknowledgment_cycle",
    "message_retry_mechanism",
    "concurrent_device_connections",
    "ssl_encrypted_communication",
    "rate_limiting_enforcement",
    "capability_negotiation",
    "graceful_disconnection",
    "error_propagation"
]
```

### 10.3 Performance Benchmarks

#### 10.3.1 Load Testing
- **Concurrent Connections**: Test with 1, 10, 50, 100 devices
- **Message Throughput**: Measure messages/second under load
- **Latency Distribution**: Record P50, P95, P99 latencies
- **Resource Usage**: Monitor CPU, memory, network utilization

#### 10.3.2 Stress Testing
- **Connection Flooding**: Rapid connection/disconnection cycles
- **Message Flooding**: High-frequency message transmission
- **Memory Pressure**: Large message payloads
- **Network Instability**: Simulated packet loss and delays

## 11. Compliance and Certification

### 11.1 Standards Compliance

- **RFC 7159**: JSON Data Interchange Format
- **RFC 5246**: TLS 1.2 Specification  
- **RFC 8446**: TLS 1.3 Specification
- **RFC 4122**: UUID Specification
- **ISO 8601**: Date and Time Format

### 11.2 Security Certifications

- **FIPS 140-2**: Cryptographic module validation
- **Common Criteria**: Security evaluation
- **HIPAA**: Healthcare data protection (if applicable)
- **GDPR**: Data protection compliance

## 12. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12 | Initial protocol specification |
| 2.0 | 2025-01 | Added acknowledgments, SSL/TLS, capability negotiation |

## 13. References

1. RFC 7159 - The JavaScript Object Notation (JSON) Data Interchange Format
2. RFC 8446 - The Transport Layer Security (TLS) Protocol Version 1.3
3. RFC 4122 - A Universally Unique IDentifier (UUID) URN Namespace
4. IEEE 802.11 - Wireless LAN Medium Access Control and Physical Layer Specifications
5. NIST SP 800-52 Rev. 2 - Guidelines for the Selection, Configuration, and Use of TLS

---

**Document Control:**
- **Classification**: Technical Specification
- **Distribution**: Development Team, QA Team, Security Team
- **Review Cycle**: Quarterly
- **Next Review**: April 2025