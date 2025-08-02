# Testing and Quality Assurance Framework - Protocol and Data Contract

## Table of Contents

- [Overview](#overview)
- [Test Execution Protocol](#test-execution-protocol)
- [Test Data Formats](#test-data-formats)
- [Network Communication Protocol](#network-communication-protocol)
- [Quality Assurance Protocols](#quality-assurance-protocols)
- [Cross-Platform Communication Protocols](#cross-platform-communication-protocols)
- [Performance Monitoring Protocol](#performance-monitoring-protocol)
- [Test Reporting API](#test-reporting-api)

## Overview

This document defines the data contracts, APIs, and communication protocols used within the Testing and Quality Assurance Framework of the Multi-Sensor Recording System. It serves as the authoritative reference for test data formats, validation protocols, and quality assurance interfaces.

## Test Execution Protocol

### Test Runner API Contract

#### Test Configuration Schema
```json
{
  "testConfiguration": {
    "type": "object",
    "required": ["testSuite", "environment", "parameters"],
    "properties": {
      "testSuite": {
        "type": "string",
        "enum": ["unit", "integration", "performance", "resilience", "comprehensive"],
        "description": "Test suite category to execute"
      },
      "environment": {
        "type": "object",
        "properties": {
          "pythonVersion": {"type": "string", "pattern": "^3\\.[8-9]"},
          "androidApiLevel": {"type": "integer", "minimum": 24},
          "deviceCount": {"type": "integer", "minimum": 1, "maximum": 8},
          "networkMode": {"type": "string", "enum": ["normal", "degraded", "offline"]}
        }
      },
      "parameters": {
        "type": "object",
        "properties": {
          "duration": {"type": "integer", "description": "Test duration in seconds"},
          "timeout": {"type": "integer", "description": "Test timeout in seconds"},
          "verboseLogging": {"type": "boolean", "default": false},
          "performanceMonitoring": {"type": "boolean", "default": true},
          "errorInjection": {"type": "boolean", "default": false}
        }
      }
    }
  }
}
```

#### Test Result Schema
```json
{
  "testResult": {
    "type": "object",
    "required": ["testId", "status", "timestamp", "metrics", "details"],
    "properties": {
      "testId": {"type": "string", "description": "Unique test execution identifier"},
      "status": {
        "type": "string", 
        "enum": ["PASS", "FAIL", "SKIP", "ERROR"],
        "description": "Overall test execution status"
      },
      "timestamp": {
        "type": "object",
        "properties": {
          "started": {"type": "string", "format": "date-time"},
          "completed": {"type": "string", "format": "date-time"},
          "duration": {"type": "number", "description": "Duration in seconds"}
        }
      },
      "metrics": {
        "type": "object",
        "properties": {
          "testsExecuted": {"type": "integer"},
          "testsPassed": {"type": "integer"},
          "testsFailed": {"type": "integer"},
          "testsSkipped": {"type": "integer"},
          "successRate": {"type": "number", "minimum": 0, "maximum": 100},
          "coveragePercentage": {"type": "number", "minimum": 0, "maximum": 100}
        }
      },
      "performance": {
        "type": "object",
        "properties": {
          "memoryUsage": {
            "type": "object",
            "properties": {
              "peak": {"type": "integer", "description": "Peak memory usage in MB"},
              "average": {"type": "integer", "description": "Average memory usage in MB"},
              "leakDetected": {"type": "boolean"}
            }
          },
          "cpuUsage": {
            "type": "object",
            "properties": {
              "peak": {"type": "number", "description": "Peak CPU usage percentage"},
              "average": {"type": "number", "description": "Average CPU usage percentage"}
            }
          },
          "networkMetrics": {
            "type": "object",
            "properties": {
              "throughput": {"type": "number", "description": "Average throughput in Mbps"},
              "latency": {"type": "number", "description": "Average latency in ms"},
              "packetLoss": {"type": "number", "description": "Packet loss percentage"}
            }
          }
        }
      },
      "details": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "testName": {"type": "string"},
            "category": {"type": "string"},
            "status": {"type": "string"},
            "executionTime": {"type": "number"},
            "errorMessage": {"type": "string"},
            "stackTrace": {"type": "string"}
          }
        }
      }
    }
  }
}
```

## Test Data Formats

### Python Test Data Contract

#### Session Test Data Schema
```json
{
  "sessionTestData": {
    "type": "object",
    "required": ["sessionId", "devices", "sensors", "configuration"],
    "properties": {
      "sessionId": {
        "type": "string",
        "pattern": "^session_[0-9]{8}_[0-9]{6}$",
        "description": "Unique session identifier"
      },
      "devices": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "deviceId": {"type": "string"},
            "deviceType": {"type": "string", "enum": ["android", "pc", "usb_camera"]},
            "status": {"type": "string", "enum": ["connected", "disconnected", "error"]},
            "capabilities": {
              "type": "array",
              "items": {"type": "string"}
            },
            "sensorData": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "timestamp": {"type": "number"},
                  "sensorType": {"type": "string"},
                  "value": {"type": "number"},
                  "unit": {"type": "string"},
                  "quality": {"type": "string", "enum": ["excellent", "good", "fair", "poor"]}
                }
              }
            }
          }
        }
      },
      "sensors": {
        "type": "object",
        "properties": {
          "shimmer": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "deviceId": {"type": "string"},
                "batteryLevel": {"type": "integer", "minimum": 0, "maximum": 100},
                "samplingRate": {"type": "integer"},
                "sensors": {
                  "type": "array",
                  "items": {"type": "string", "enum": ["gsr", "ppg", "accelerometer", "gyroscope"]}
                }
              }
            }
          },
          "thermal": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "deviceId": {"type": "string"},
                "resolution": {"type": "string"},
                "frameRate": {"type": "integer"},
                "temperatureRange": {
                  "type": "object",
                  "properties": {
                    "min": {"type": "number"},
                    "max": {"type": "number"}
                  }
                }
              }
            }
          }
        }
      },
      "configuration": {
        "type": "object",
        "properties": {
          "recordingDuration": {"type": "integer", "description": "Duration in seconds"},
          "synchronizationMode": {"type": "string", "enum": ["hardware", "software", "ntp"]},
          "dataFormat": {"type": "string", "enum": ["csv", "json", "binary"]},
          "qualityLevel": {"type": "string", "enum": ["research", "clinical", "consumer"]}
        }
      }
    }
  }
}
```

#### Performance Benchmark Data Schema
```json
{
  "performanceBenchmark": {
    "type": "object",
    "required": ["benchmarkId", "metrics", "baseline", "thresholds"],
    "properties": {
      "benchmarkId": {"type": "string"},
      "testEnvironment": {
        "type": "object",
        "properties": {
          "osVersion": {"type": "string"},
          "pythonVersion": {"type": "string"},
          "hardwareSpecs": {
            "type": "object",
            "properties": {
              "cpu": {"type": "string"},
              "memory": {"type": "string"},
              "storage": {"type": "string"},
              "network": {"type": "string"}
            }
          }
        }
      },
      "metrics": {
        "type": "object",
        "properties": {
          "executionTime": {
            "type": "object",
            "properties": {
              "initialization": {"type": "number", "description": "Initialization time in ms"},
              "recording": {"type": "number", "description": "Recording time per second"},
              "processing": {"type": "number", "description": "Data processing time in ms"},
              "cleanup": {"type": "number", "description": "Cleanup time in ms"}
            }
          },
          "resourceUsage": {
            "type": "object",
            "properties": {
              "memory": {
                "type": "object",
                "properties": {
                  "peak": {"type": "integer", "description": "Peak memory in MB"},
                  "average": {"type": "integer", "description": "Average memory in MB"},
                  "baseline": {"type": "integer", "description": "Baseline memory in MB"}
                }
              },
              "cpu": {
                "type": "object",
                "properties": {
                  "peak": {"type": "number", "description": "Peak CPU percentage"},
                  "average": {"type": "number", "description": "Average CPU percentage"}
                }
              },
              "storage": {
                "type": "object",
                "properties": {
                  "writeSpeed": {"type": "number", "description": "Write speed in MB/s"},
                  "readSpeed": {"type": "number", "description": "Read speed in MB/s"},
                  "spaceUsed": {"type": "integer", "description": "Storage space used in MB"}
                }
              }
            }
          },
          "networkPerformance": {
            "type": "object",
            "properties": {
              "bandwidth": {"type": "number", "description": "Bandwidth utilization in Mbps"},
              "latency": {"type": "number", "description": "Average latency in ms"},
              "jitter": {"type": "number", "description": "Latency jitter in ms"},
              "packetLoss": {"type": "number", "description": "Packet loss percentage"}
            }
          }
        }
      },
      "baseline": {
        "type": "object",
        "description": "Baseline performance metrics for comparison"
      },
      "thresholds": {
        "type": "object",
        "properties": {
          "responseTime": {"type": "number", "description": "Maximum acceptable response time in ms"},
          "memoryUsage": {"type": "integer", "description": "Maximum memory usage in MB"},
          "cpuUsage": {"type": "number", "description": "Maximum CPU usage percentage"},
          "regressionThreshold": {"type": "number", "description": "Maximum acceptable performance regression percentage"}
        }
      }
    }
  }
}
```

### Android Test Data Contract

#### Device State Schema
```json
{
  "deviceState": {
    "type": "object",
    "required": ["deviceId", "timestamp", "state", "capabilities"],
    "properties": {
      "deviceId": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"},
      "state": {
        "type": "object",
        "properties": {
          "connectionStatus": {"type": "string", "enum": ["connected", "connecting", "disconnected", "error"]},
          "batteryLevel": {"type": "integer", "minimum": 0, "maximum": 100},
          "storageAvailable": {"type": "integer", "description": "Available storage in MB"},
          "networkQuality": {"type": "string", "enum": ["excellent", "good", "fair", "poor", "none"]},
          "thermalState": {"type": "string", "enum": ["normal", "warm", "hot", "critical"]}
        }
      },
      "capabilities": {
        "type": "object",
        "properties": {
          "camera": {
            "type": "object",
            "properties": {
              "resolution": {"type": "string"},
              "frameRate": {"type": "integer"},
              "videoCodec": {"type": "string"},
              "supportedFormats": {"type": "array", "items": {"type": "string"}}
            }
          },
          "thermal": {
            "type": "object",
            "properties": {
              "available": {"type": "boolean"},
              "resolution": {"type": "string"},
              "frameRate": {"type": "integer"},
              "temperatureRange": {
                "type": "object",
                "properties": {
                  "min": {"type": "number"},
                  "max": {"type": "number"}
                }
              }
            }
          },
          "sensors": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "type": {"type": "string"},
                "available": {"type": "boolean"},
                "samplingRate": {"type": "integer"},
                "accuracy": {"type": "string"}
              }
            }
          }
        }
      },
      "errors": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "errorCode": {"type": "string"},
            "errorMessage": {"type": "string"},
            "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
            "recoverable": {"type": "boolean"}
          }
        }
      }
    }
  }
}
```

#### UI Test State Schema
```json
{
  "uiTestState": {
    "type": "object",
    "required": ["testId", "screenState", "interactions", "assertions"],
    "properties": {
      "testId": {"type": "string"},
      "screenState": {
        "type": "object",
        "properties": {
          "currentActivity": {"type": "string"},
          "currentFragment": {"type": "string"},
          "orientation": {"type": "string", "enum": ["portrait", "landscape"]},
          "visibleElements": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "elementId": {"type": "string"},
                "elementType": {"type": "string"},
                "visible": {"type": "boolean"},
                "enabled": {"type": "boolean"},
                "text": {"type": "string"},
                "bounds": {
                  "type": "object",
                  "properties": {
                    "left": {"type": "integer"},
                    "top": {"type": "integer"},
                    "right": {"type": "integer"},
                    "bottom": {"type": "integer"}
                  }
                }
              }
            }
          }
        }
      },
      "interactions": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "action": {"type": "string", "enum": ["click", "longClick", "swipe", "type", "scroll"]},
            "targetElement": {"type": "string"},
            "parameters": {"type": "object"},
            "result": {"type": "string", "enum": ["success", "failure", "timeout"]},
            "responseTime": {"type": "number", "description": "Response time in ms"}
          }
        }
      },
      "assertions": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "assertionType": {"type": "string"},
            "expected": {"type": "string"},
            "actual": {"type": "string"},
            "result": {"type": "boolean"},
            "errorMessage": {"type": "string"}
          }
        }
      }
    }
  }
}
```

## Network Communication Protocol

### Test Communication Messages

#### Test Command Protocol
```mermaid
sequenceDiagram
    participant TF as Test Framework
    participant PC as PC Controller
    participant AD as Android Device
    
    TF->>PC: TestCommand
    Note over TF,PC: {"command": "start_test", "testId": "test_001", "parameters": {...}}
    
    PC->>AD: DeviceCommand
    Note over PC,AD: {"command": "initialize", "deviceId": "android_001", "config": {...}}
    
    AD->>PC: StatusUpdate
    Note over AD,PC: {"status": "ready", "deviceId": "android_001", "timestamp": "..."}
    
    PC->>TF: TestProgress
    Note over PC,TF: {"testId": "test_001", "progress": 25, "status": "running"}
    
    loop Test Execution
        AD->>PC: DataStream
        Note over AD,PC: {"sensorData": [...], "timestamp": "...", "quality": "good"}
        
        PC->>TF: TestMetrics
        Note over PC,TF: {"metrics": {...}, "performance": {...}}
    end
    
    PC->>TF: TestComplete
    Note over PC,TF: {"testId": "test_001", "result": "PASS", "finalMetrics": {...}}
```

#### Message Format Specifications

**Test Command Message:**
| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| command | string | Yes | Command type (start_test, stop_test, pause_test, resume_test) |
| testId | string | Yes | Unique test identifier |
| timestamp | string | Yes | ISO 8601 timestamp |
| parameters | object | No | Test-specific parameters |
| timeout | integer | No | Command timeout in seconds |
| priority | string | No | Command priority (low, normal, high, critical) |

**Status Update Message:**
| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| deviceId | string | Yes | Device identifier |
| status | string | Yes | Current device status |
| timestamp | string | Yes | ISO 8601 timestamp |
| batteryLevel | integer | No | Battery level percentage |
| memoryUsage | integer | No | Memory usage in MB |
| errorCount | integer | No | Number of errors since last update |
| lastError | string | No | Description of most recent error |

**Data Stream Message:**
| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| deviceId | string | Yes | Source device identifier |
| streamType | string | Yes | Data stream type (sensor, video, thermal) |
| timestamp | string | Yes | Data timestamp |
| sequenceNumber | integer | Yes | Sequence number for ordering |
| data | array | Yes | Actual sensor data |
| quality | string | No | Data quality indicator |
| checksum | string | No | Data integrity checksum |

## Quality Assurance Protocols

### Code Quality Metrics Schema
```json
{
  "codeQualityMetrics": {
    "type": "object",
    "required": ["projectId", "timestamp", "metrics", "violations"],
    "properties": {
      "projectId": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"},
      "codebase": {
        "type": "object",
        "properties": {
          "linesOfCode": {"type": "integer"},
          "filesAnalyzed": {"type": "integer"},
          "testFiles": {"type": "integer"},
          "documentationFiles": {"type": "integer"}
        }
      },
      "metrics": {
        "type": "object",
        "properties": {
          "coverage": {
            "type": "object",
            "properties": {
              "linesCovered": {"type": "number"},
              "branchesCovered": {"type": "number"},
              "functionsCovered": {"type": "number"},
              "overallCoverage": {"type": "number"}
            }
          },
          "complexity": {
            "type": "object",
            "properties": {
              "cyclomaticComplexity": {"type": "number"},
              "cognitiveComplexity": {"type": "number"},
              "maintainabilityIndex": {"type": "number"}
            }
          },
          "quality": {
            "type": "object",
            "properties": {
              "duplicatedLines": {"type": "integer"},
              "techDebt": {"type": "string"},
              "reliabilityRating": {"type": "string"},
              "securityRating": {"type": "string"}
            }
          }
        }
      },
      "violations": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "file": {"type": "string"},
            "line": {"type": "integer"},
            "rule": {"type": "string"},
            "severity": {"type": "string", "enum": ["info", "minor", "major", "critical", "blocker"]},
            "message": {"type": "string"},
            "category": {"type": "string"}
          }
        }
      }
    }
  }
}
```

### Security Scan Results Schema
```json
{
  "securityScanResults": {
    "type": "object",
    "required": ["scanId", "timestamp", "vulnerabilities", "summary"],
    "properties": {
      "scanId": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"},
      "scanTool": {"type": "string"},
      "scanDuration": {"type": "integer", "description": "Scan duration in seconds"},
      "filesScanned": {"type": "integer"},
      "vulnerabilities": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "string"},
            "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
            "category": {"type": "string"},
            "description": {"type": "string"},
            "file": {"type": "string"},
            "line": {"type": "integer"},
            "column": {"type": "integer"},
            "cwe": {"type": "string", "description": "Common Weakness Enumeration ID"},
            "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
            "recommendation": {"type": "string"}
          }
        }
      },
      "summary": {
        "type": "object",
        "properties": {
          "totalVulnerabilities": {"type": "integer"},
          "criticalCount": {"type": "integer"},
          "highCount": {"type": "integer"},
          "mediumCount": {"type": "integer"},
          "lowCount": {"type": "integer"},
          "riskScore": {"type": "number", "minimum": 0, "maximum": 100}
        }
      }
    }
  }
}
```

## Cross-Platform Communication Protocols

### PC-Android Recording Session Protocol

#### Session Lifecycle Messages

**Session Initialization Request**
```json
{
  "type": "session_init_request",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "sessionId": "session_12345",
  "participantId": "P001",
  "experimentConfig": {
    "duration": 300,
    "samplingRate": 50,
    "enabledSensors": ["gsr", "ppg", "accelerometer", "gyroscope", "magnetometer"],
    "recordingTypes": {
      "video": true,
      "thermal": true,
      "sensor": true
    }
  },
  "deviceRequirements": {
    "minDevices": 1,
    "maxDevices": 8,
    "requiredCapabilities": ["sensor_recording", "video_capture"]
  }
}
```

**Session Initialization Response**
```json
{
  "type": "session_init_response",
  "timestamp": "2025-01-01T12:00:01.000Z",
  "sessionId": "session_12345",
  "deviceId": "android_device_001",
  "status": "success",
  "deviceCapabilities": {
    "sensorTypes": ["gsr", "ppg", "accelerometer", "gyroscope", "magnetometer"],
    "videoFormats": ["mp4", "avi"],
    "thermalSupport": true,
    "maxRecordingDuration": 3600,
    "availableStorage": 2147483648
  },
  "deviceStatus": {
    "batteryLevel": 85,
    "cpuUsage": 15.2,
    "memoryUsage": 512.0,
    "temperature": 35.0
  }
}
```

#### Real-Time Data Streaming Protocol

**Sensor Data Stream Message**
```json
{
  "type": "sensor_data_stream",
  "timestamp": "2025-01-01T12:05:30.125Z",
  "sessionId": "session_12345",
  "deviceId": "android_device_001",
  "sequenceNumber": 15032,
  "sensorData": {
    "gsr": {
      "value": 8.45,
      "unit": "microsiemens",
      "quality": "good",
      "timestamp": "2025-01-01T12:05:30.125Z"
    },
    "ppg": {
      "value": 1024,
      "heartRate": 72,
      "unit": "arbitrary_units",
      "quality": "excellent",
      "timestamp": "2025-01-01T12:05:30.125Z"
    },
    "accelerometer": {
      "x": 0.12,
      "y": -9.78,
      "z": 0.05,
      "unit": "m/s²",
      "timestamp": "2025-01-01T12:05:30.125Z"
    },
    "gyroscope": {
      "x": 0.01,
      "y": -0.02,
      "z": 0.00,
      "unit": "rad/s",
      "timestamp": "2025-01-01T12:05:30.125Z"
    },
    "magnetometer": {
      "x": 25.4,
      "y": -12.8,
      "z": 48.9,
      "unit": "μT",
      "timestamp": "2025-01-01T12:05:30.125Z"
    }
  }
}
```

#### Device Control Protocol

**Recording Control Command**
```json
{
  "type": "recording_control",
  "timestamp": "2025-01-01T12:00:05.000Z",
  "sessionId": "session_12345",
  "command": "start_recording",
  "parameters": {
    "recordingTypes": ["video", "sensor", "thermal"],
    "videoSettings": {
      "resolution": "1920x1080",
      "framerate": 30,
      "codec": "h264"
    },
    "sensorSettings": {
      "samplingRate": 50,
      "bufferSize": 1000
    },
    "synchronization": {
      "masterDevice": "pc_controller",
      "timeSyncProtocol": "ntp",
      "maxClockDrift": 10
    }
  }
}
```

**Command Acknowledgment**
```json
{
  "type": "command_acknowledgment",
  "timestamp": "2025-01-01T12:00:05.500Z",
  "sessionId": "session_12345",
  "deviceId": "android_device_001",
  "commandType": "recording_control",
  "status": "success",
  "executionTime": 450,
  "result": {
    "recordingStarted": true,
    "activeSensors": ["gsr", "ppg", "accelerometer", "gyroscope", "magnetometer"],
    "videoRecording": true,
    "thermalRecording": false,
    "estimatedDuration": 300,
    "dataOutputPath": "/storage/emulated/0/MultiSensorRecording/session_12345/"
  }
}
```

#### Error Handling Protocol

**Error Notification**
```json
{
  "type": "error_notification",
  "timestamp": "2025-01-01T12:10:15.000Z",
  "sessionId": "session_12345",
  "deviceId": "android_device_001",
  "errorCode": "SENSOR_CONNECTION_LOST",
  "severity": "high",
  "errorDetails": {
    "description": "Connection to Shimmer3 GSR sensor lost",
    "affectedSensors": ["gsr"],
    "errorTimestamp": "2025-01-01T12:10:14.850Z",
    "recoveryAttempts": 3,
    "automaticRecovery": false,
    "userActionRequired": true
  },
  "recoveryOptions": [
    {
      "action": "reconnect_sensor",
      "description": "Attempt automatic sensor reconnection",
      "estimatedTime": 10
    },
    {
      "action": "continue_without_sensor",
      "description": "Continue recording without GSR sensor",
      "impact": "Loss of GSR data for remainder of session"
    },
    {
      "action": "abort_session",
      "description": "Stop recording session",
      "impact": "Complete session termination"
    }
  ]
}
```

### Android Test Framework Communication Protocol

#### Test Execution Control Messages

**Test Suite Execution Request**
```json
{
  "type": "test_suite_execution_request",
  "timestamp": "2025-01-01T10:00:00.000Z",
  "testSuiteId": "comprehensive_android_test_suite",
  "executionConfig": {
    "testCategories": ["unit", "integration", "performance", "stress"],
    "parallel": true,
    "maxConcurrency": 4,
    "timeout": 3600,
    "reportFormat": ["json", "html"],
    "performanceThresholds": {
      "maxExecutionTime": 5000,
      "maxMemoryUsage": 104857600
    }
  },
  "deviceConfig": {
    "targetDevice": "emulator-5554",
    "apiLevel": 30,
    "architecture": "x86_64"
  }
}
```

**Test Execution Progress Update**
```json
{
  "type": "test_execution_progress",
  "timestamp": "2025-01-01T10:15:30.000Z",
  "testSuiteId": "comprehensive_android_test_suite",
  "progress": {
    "totalTests": 156,
    "completedTests": 89,
    "passedTests": 85,
    "failedTests": 4,
    "skippedTests": 0,
    "currentTest": "SessionManagerIntegrationTest.testRecordingLifecycle",
    "percentComplete": 57.05
  },
  "performance": {
    "averageExecutionTime": 2850,
    "peakMemoryUsage": 89456640,
    "currentCpuUsage": 45.2,
    "estimatedTimeRemaining": 1245
  }
}
```

## Performance Monitoring Protocol

### Real-time Metrics Collection

#### System Performance Schema
```json
{
  "systemPerformance": {
    "type": "object",
    "required": ["timestamp", "system", "application", "network"],
    "properties": {
      "timestamp": {"type": "string", "format": "date-time"},
      "system": {
        "type": "object",
        "properties": {
          "cpu": {
            "type": "object",
            "properties": {
              "usage": {"type": "number", "description": "CPU usage percentage"},
              "cores": {"type": "integer"},
              "frequency": {"type": "number", "description": "CPU frequency in GHz"},
              "temperature": {"type": "number", "description": "CPU temperature in Celsius"}
            }
          },
          "memory": {
            "type": "object",
            "properties": {
              "total": {"type": "integer", "description": "Total memory in MB"},
              "used": {"type": "integer", "description": "Used memory in MB"},
              "available": {"type": "integer", "description": "Available memory in MB"},
              "percentage": {"type": "number", "description": "Memory usage percentage"}
            }
          },
          "storage": {
            "type": "object",
            "properties": {
              "total": {"type": "integer", "description": "Total storage in GB"},
              "used": {"type": "integer", "description": "Used storage in GB"},
              "available": {"type": "integer", "description": "Available storage in GB"},
              "ioReadSpeed": {"type": "number", "description": "Read speed in MB/s"},
              "ioWriteSpeed": {"type": "number", "description": "Write speed in MB/s"}
            }
          }
        }
      },
      "application": {
        "type": "object",
        "properties": {
          "processId": {"type": "integer"},
          "memoryUsage": {"type": "integer", "description": "Application memory usage in MB"},
          "cpuUsage": {"type": "number", "description": "Application CPU usage percentage"},
          "threadCount": {"type": "integer"},
          "openFiles": {"type": "integer"},
          "networkConnections": {"type": "integer"}
        }
      },
      "network": {
        "type": "object",
        "properties": {
          "interfaceName": {"type": "string"},
          "bytesReceived": {"type": "integer"},
          "bytesSent": {"type": "integer"},
          "packetsReceived": {"type": "integer"},
          "packetsSent": {"type": "integer"},
          "errors": {"type": "integer"},
          "drops": {"type": "integer"}
        }
      }
    }
  }
}
```

## Test Reporting API

### Report Generation Schema
```json
{
  "testReport": {
    "type": "object",
    "required": ["reportId", "generatedAt", "testSummary", "sections"],
    "properties": {
      "reportId": {"type": "string"},
      "generatedAt": {"type": "string", "format": "date-time"},
      "reportType": {"type": "string", "enum": ["executive", "technical", "performance", "security"]},
      "testSummary": {
        "type": "object",
        "properties": {
          "totalTests": {"type": "integer"},
          "passedTests": {"type": "integer"},
          "failedTests": {"type": "integer"},
          "skippedTests": {"type": "integer"},
          "executionTime": {"type": "number", "description": "Total execution time in minutes"},
          "overallStatus": {"type": "string", "enum": ["PASS", "FAIL", "WARNING"]}
        }
      },
      "sections": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "sectionName": {"type": "string"},
            "status": {"type": "string"},
            "summary": {"type": "string"},
            "details": {"type": "object"},
            "recommendations": {"type": "array", "items": {"type": "string"}},
            "attachments": {"type": "array", "items": {"type": "string"}}
          }
        }
      },
      "qualityGates": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "gateName": {"type": "string"},
            "status": {"type": "string", "enum": ["PASS", "FAIL"]},
            "threshold": {"type": "number"},
            "actualValue": {"type": "number"},
            "description": {"type": "string"}
          }
        }
      }
    }
  }
}
```

## Error Handling and Recovery Protocol

### Error Classification Schema
```json
{
  "errorClassification": {
    "type": "object",
    "required": ["errorId", "category", "severity", "recoverable"],
    "properties": {
      "errorId": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"},
      "category": {
        "type": "string",
        "enum": ["network", "hardware", "software", "data", "configuration", "security"]
      },
      "severity": {
        "type": "string",
        "enum": ["low", "medium", "high", "critical"]
      },
      "recoverable": {"type": "boolean"},
      "description": {"type": "string"},
      "stackTrace": {"type": "string"},
      "context": {
        "type": "object",
        "properties": {
          "testId": {"type": "string"},
          "deviceId": {"type": "string"},
          "operation": {"type": "string"},
          "parameters": {"type": "object"}
        }
      },
      "recovery": {
        "type": "object",
        "properties": {
          "attempted": {"type": "boolean"},
          "successful": {"type": "boolean"},
          "method": {"type": "string"},
          "duration": {"type": "number", "description": "Recovery time in seconds"},
          "fallbackUsed": {"type": "boolean"}
        }
      }
    }
  }
}
```

## Output File Formats and Data Export Specifications

### Test Result Export Formats

The Testing and Quality Assurance Framework generates multiple output file formats for test results, reports, and performance data analysis.

#### 1. Test Execution Report Files

**JUnit XML Format (junit-results.xml):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="MultiSensorRecordingSystem" tests="245" failures="3" errors="1" time="1847.25">
  <testsuite name="unit_tests" tests="150" failures="2" errors="0" time="425.75" hostname="test-runner-01">
    <testcase classname="com.thermal.ThermalCameraTest" name="testFrameCapture" time="2.45"/>
    <testcase classname="com.shimmer.ShimmerConnectionTest" name="testBluetoothPairing" time="5.12">
      <failure message="Bluetooth pairing timeout" type="TimeoutException">
        Expected successful pairing within 10 seconds, but got timeout
      </failure>
    </testcase>
  </testsuite>
  <testsuite name="integration_tests" tests="75" failures="1" errors="1" time="1245.80" hostname="test-runner-02">
    <testcase classname="com.integration.MultiDeviceSyncTest" name="testTimeSync" time="45.67"/>
    <testcase classname="com.integration.NetworkingTest" name="testDataTransfer" time="120.33">
      <error message="Network connection lost" type="NetworkException">
        java.net.ConnectException: Connection timed out after 30000ms
      </error>
    </testcase>
  </testsuite>
</testsuites>
```

#### 2. Performance Metrics CSV Files

**Performance Report (performance-metrics.csv):**
```csv
Timestamp,TestID,DeviceID,CPUUsage,MemoryUsage,NetworkThroughput,FrameRate,ErrorCount,ResponseTime
2024-01-31T10:30:00.000Z,test_001,android_device_001,45.2,512.8,12.5,25.0,0,250
2024-01-31T10:30:01.000Z,test_001,android_device_001,47.1,515.2,11.8,24.8,0,255
2024-01-31T10:30:02.000Z,test_001,android_device_001,43.8,518.1,12.2,25.0,0,248
2024-01-31T10:30:03.000Z,test_001,android_device_002,52.3,628.4,15.2,30.0,1,280
```

**Column Specifications:**
- `Timestamp`: ISO 8601 format timestamp
- `TestID`: Unique test execution identifier
- `DeviceID`: Device identifier (android_device_xxx, pc_controller, shimmer_xxx)
- `CPUUsage`: CPU usage percentage (0-100)
- `MemoryUsage`: Memory usage in MB
- `NetworkThroughput`: Network throughput in MB/s
- `FrameRate`: Video/data capture frame rate
- `ErrorCount`: Cumulative error count since test start
- `ResponseTime`: Response time in milliseconds

#### 3. Test Coverage Reports

**Coverage Summary (coverage-summary.json):**
```json
{
  "coverageReport": {
    "generated": "2024-01-31T10:45:00.000Z",
    "toolVersion": "pytest-cov 4.0.0",
    "overallCoverage": {
      "lines": {
        "total": 15420,
        "covered": 13876,
        "percentage": 89.98
      },
      "branches": {
        "total": 3245,
        "covered": 2891,
        "percentage": 89.09
      },
      "functions": {
        "total": 1156,
        "covered": 1089,
        "percentage": 94.20
      }
    },
    "moduleBreakdown": [
      {
        "module": "python_desktop_controller",
        "path": "PythonApp/src/",
        "lines": {"total": 8420, "covered": 7856, "percentage": 93.30},
        "branches": {"total": 1845, "covered": 1701, "percentage": 92.19}
      },
      {
        "module": "android_mobile_app",
        "path": "AndroidApp/app/src/main/java/",
        "lines": {"total": 7000, "covered": 6020, "percentage": 86.00},
        "branches": {"total": 1400, "covered": 1190, "percentage": 85.00}
      }
    ]
  }
}
```

#### 4. Quality Gates Status Files

**Quality Assessment (quality-gates.json):**
```json
{
  "qualityGates": {
    "evaluatedAt": "2024-01-31T10:45:00.000Z",
    "overallStatus": "PASS",
    "gates": [
      {
        "gateName": "unit_test_coverage",
        "status": "PASS",
        "threshold": 85.0,
        "actualValue": 89.98,
        "description": "Unit test line coverage must be >= 85%"
      },
      {
        "gateName": "integration_test_success_rate",
        "status": "PASS",
        "threshold": 95.0,
        "actualValue": 97.33,
        "description": "Integration tests must have >= 95% success rate"
      },
      {
        "gateName": "performance_regression",
        "status": "WARNING",
        "threshold": 5.0,
        "actualValue": 3.2,
        "description": "Performance regression must be < 5% from baseline"
      },
      {
        "gateName": "security_vulnerabilities",
        "status": "PASS",
        "threshold": 0,
        "actualValue": 0,
        "description": "No high or critical security vulnerabilities allowed"
      }
    ]
  }
}
```

#### 5. Log Files Structure

**Test Execution Logs (test-execution.log):**
```
2024-01-31T10:30:00.000Z [INFO] [TestRunner] Starting comprehensive test suite execution
2024-01-31T10:30:00.125Z [INFO] [Setup] Initializing test environment with 4 Android devices
2024-01-31T10:30:05.250Z [INFO] [DeviceManager] Connected to android_device_001 (Samsung S22)
2024-01-31T10:30:07.380Z [INFO] [DeviceManager] Connected to android_device_002 (Samsung S21)
2024-01-31T10:30:12.500Z [INFO] [TestExecution] Starting unit tests - 150 test cases
2024-01-31T10:35:18.750Z [WARN] [ThermalTest] Frame capture timeout on device android_device_001
2024-01-31T10:35:25.880Z [ERROR] [NetworkTest] Connection lost to android_device_002: java.net.ConnectException
2024-01-31T10:40:30.000Z [INFO] [TestExecution] Unit tests completed: 148 PASS, 2 FAIL, 0 SKIP
```

**Error Detail Logs (error-details.log):**
```
2024-01-31T10:35:25.880Z [ERROR] [NetworkTest.testDataTransfer] 
Test ID: integration_test_005
Device ID: android_device_002
Error Type: NetworkException
Error Message: Connection timed out after 30000ms
Stack Trace:
  at java.net.SocketInputStream.socketRead0(Native Method)
  at java.net.SocketInputStream.socketRead(SocketInputStream.java:116)
  at java.net.SocketInputStream.read(SocketInputStream.java:171)
Context:
  - Operation: TCP socket data transfer
  - Expected Bytes: 1048576
  - Actual Bytes: 524288
  - Network Interface: wlan0
  - Signal Strength: -65 dBm
Recovery Attempted: true
Recovery Successful: false
Fallback Method: UDP transfer protocol
```

This protocol documentation serves as the authoritative reference for all data contracts and communication interfaces within the Testing and Quality Assurance Framework, ensuring consistency and interoperability across all system components.