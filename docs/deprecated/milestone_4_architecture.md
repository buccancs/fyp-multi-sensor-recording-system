# Milestone 4 Architecture: Unified Protocol & Shared Configuration

This document provides comprehensive architectural diagrams for the Milestone 4 implementation, documenting the unified protocol system, shared configuration, and test harnesses.

## System Overview Architecture

```mermaid
graph TB
    subgraph "Monorepo Root"
        Protocol[protocol]
        Schema[message_schema.json]
        Config[config.json]
    end
    
    subgraph "Python Application"
        PyApp[PythonApp src]
        PyProtocol[protocol]
        PySchema[schema_utils.py]
        PyConfig[config_loader.py]
        PyTests[tests]
        PyFake[fake_device.py]
        PyCalib[test_calibration.py]
        PyIntegrity[test_config_schema_integrity.py]
    end
    
    subgraph "Android Application"
        AndroidApp[AndroidApp src main]
        AndroidAssets[assets]
        AndroidProtocol[java protocol]
        AndroidSchema[SchemaManager.java]
        AndroidConfig[ConfigManager.java]
        AndroidTests[androidTest]
        AndroidInstr[ProtocolIntegrationTest.kt]
    end
    
    Protocol --> PyProtocol
    Protocol --> AndroidAssets
    Schema --> PySchema
    Schema --> AndroidSchema
    Config --> PyConfig
    Config --> AndroidConfig
    
    PyProtocol --> PyTests
    AndroidProtocol --> AndroidTests
    
    style Protocol fill:#e1f5fe
    style PyProtocol fill:#f3e5f5
    style AndroidProtocol fill:#e8f5e8
```

## Unified Protocol Communication Flow

```mermaid
sequenceDiagram
    participant PC as Python PC App
    participant Schema as Schema Manager
    participant Config as Config Manager
    participant Android as Android Device
    participant MockTest as Test Harness
    
    Note over PC, Android: System Initialization
    PC->>Schema: Load message_schema.json
    PC->>Config: Load config.json
    Android->>Schema: Load from assets
    Android->>Config: Load from assets
    
    Note over PC, Android: Recording Session
    PC->>Schema: Validate start_record message
    Schema-->>PC: Validation OK
    PC->>Android: start_record{session_id, timestamp}
    Android->>Schema: Validate received message
    Schema-->>Android: Validation OK
    
    Android->>Schema: Create preview_frame message
    Schema-->>Android: Message template
    Android->>PC: preview_frame{frame_id, image_data, width, height}
    PC->>Schema: Validate preview_frame
    Schema-->>PC: Validation OK
    
    Android->>Schema: Create file_chunk message
    Schema-->>Android: Message template
    Android->>PC: file_chunk{file_id, chunk_index, chunk_data}
    
    PC->>Schema: Create stop_record message
    Schema-->>PC: Message template
    PC->>Android: stop_record{session_id, timestamp}
    
    Note over PC, Android: Testing with Mock
    MockTest->>Schema: Validate test messages
    MockTest->>PC: Simulate Android responses
    PC->>MockTest: Send commands
```

## Shared Configuration Architecture

```mermaid
graph LR
    subgraph "Shared Configuration"
        ConfigFile[config.json]
        
        subgraph "Configuration Sections"
            Network[network: host, port, timeout]
            Devices[devices: camera, frame_rate, resolution]
            UI[UI: preview_scale, overlays]
            Calibration[calibration: pattern, thresholds]
            Session[session: directories, naming]
            Performance[performance: memory, threads]
        end
    end
    
    subgraph "Python ConfigManager"
        PyLoader[config_loader.py]
        PyMethods[get_host get_port get_frame_rate]
        PyValidation[validate_config]
    end
    
    subgraph "Android ConfigManager"
        AndroidLoader[ConfigManager.java]
        AndroidMethods[getHost getPort getFrameRate]
        AndroidValidation[validateConfig]
    end
    
    ConfigFile --> PyLoader
    ConfigFile --> AndroidLoader
    
    Network --> PyMethods
    Devices --> PyMethods
    UI --> PyMethods
    Calibration --> PyMethods
    
    Network --> AndroidMethods
    Devices --> AndroidMethods
    UI --> AndroidMethods
    Calibration --> AndroidMethods
    
    PyLoader --> PyValidation
    AndroidLoader --> AndroidValidation
    
    style ConfigFile fill:#fff3e0
    style PyLoader fill:#f3e5f5
    style AndroidLoader fill:#e8f5e8
```

## Test Harnesses Architecture

```mermaid
graph TB
    subgraph "Python Test Harnesses"
        subgraph "Fake Device Simulator"
            FakeDevice[FakeAndroidDevice]
            FakeManager[FakeDeviceManager]
            MockSocket[Mock Socket Connection]
            MessageSim[Message Simulation]
        end
        
        subgraph "Calibration Tests"
            CalibData[CalibrationTestData]
            CalibTester[CalibrationTester]
            SyntheticData[Synthetic Data Generation]
            RealData[Real Data Support]
        end
        
        subgraph "Integrity Tests"
            ConfigTester[ConfigIntegrityTester]
            SchemaTester[SchemaIntegrityTester]
            CrossValidation[Cross-Validation]
        end
    end
    
    subgraph "Android Instrumentation Tests"
        subgraph "Protocol Tests"
            ProtocolTest[ProtocolIntegrationTest]
            MockConnection[MockConnectionManager]
            StateManager[MockRecordingStateManager]
        end
        
        subgraph "Test Categories"
            SchemaTests[Schema Loading & Validation]
            ConfigTests[Config Loading & Access]
            MessageTests[Message Creation & Validation]
            StateTests[State Machine Transitions]
        end
    end
    
    subgraph "Shared Resources"
        TestSchema[message_schema.json]
        TestConfig[config.json]
        TestData[Test Data Files]
    end
    
    FakeDevice --> MockSocket
    FakeDevice --> MessageSim
    FakeManager --> FakeDevice
    
    CalibData --> SyntheticData
    CalibData --> RealData
    CalibTester --> CalibData
    
    ConfigTester --> CrossValidation
    SchemaTester --> CrossValidation
    
    ProtocolTest --> MockConnection
    ProtocolTest --> StateManager
    
    SchemaTests --> TestSchema
    ConfigTests --> TestConfig
    MessageTests --> TestSchema
    StateTests --> TestConfig
    
    style FakeDevice fill:#e3f2fd
    style CalibTester fill:#f1f8e9
    style ProtocolTest fill:#fff8e1
```

## Cross-Platform Protocol Validation

```mermaid
graph LR
    subgraph "Message Schema Validation"
        SchemaFile[message_schema.json]
        
        subgraph "Python Validation"
            PySchemaManager[SchemaManager]
            PyJsonSchema[jsonschema library]
            PyBasicValidation[Basic validation fallback]
        end
        
        subgraph "Android Validation"
            AndroidSchemaManager[SchemaManager.java]
            AndroidJSONObject[JSONObject validation]
            AndroidTypeChecking[Type-specific validation]
        end
    end
    
    subgraph "Message Types"
        StartRecord[start_record]
        StopRecord[stop_record]
        PreviewFrame[preview_frame]
        FileChunk[file_chunk]
        DeviceStatus[device_status]
        Ack[ack]
        CalibrationStart[calibration_start]
        CalibrationResult[calibration_result]
    end
    
    SchemaFile --> PySchemaManager
    SchemaFile --> AndroidSchemaManager
    
    PySchemaManager --> PyJsonSchema
    PySchemaManager --> PyBasicValidation
    
    AndroidSchemaManager --> AndroidJSONObject
    AndroidSchemaManager --> AndroidTypeChecking
    
    StartRecord --> PySchemaManager
    StopRecord --> PySchemaManager
    PreviewFrame --> PySchemaManager
    FileChunk --> PySchemaManager
    DeviceStatus --> PySchemaManager
    Ack --> PySchemaManager
    CalibrationStart --> PySchemaManager
    CalibrationResult --> PySchemaManager
    
    StartRecord --> AndroidSchemaManager
    StopRecord --> AndroidSchemaManager
    PreviewFrame --> AndroidSchemaManager
    FileChunk --> AndroidSchemaManager
    DeviceStatus --> AndroidSchemaManager
    Ack --> AndroidSchemaManager
    CalibrationStart --> AndroidSchemaManager
    CalibrationResult --> AndroidSchemaManager
    
    style SchemaFile fill:#e8eaf6
    style PySchemaManager fill:#f3e5f5
    style AndroidSchemaManager fill:#e8f5e8
```

## Testing Strategy Flow

```mermaid
flowchart TD
    Start([Start Testing]) --> UnitTests{Unit Tests}
    
    UnitTests -->|Pass| IntegrationTests{Integration Tests}
    UnitTests -->|Fail| FixIssues[Fix Issues]
    FixIssues --> UnitTests
    
    IntegrationTests -->|Pass| CrossPlatform{Cross-Platform Tests}
    IntegrationTests -->|Fail| FixIntegration[Fix Integration Issues]
    FixIntegration --> IntegrationTests
    
    CrossPlatform -->|Pass| DeviceTests{Device Tests}
    CrossPlatform -->|Fail| FixProtocol[Fix Protocol Issues]
    FixProtocol --> CrossPlatform
    
    DeviceTests -->|Pass| Complete([Testing Complete])
    DeviceTests -->|Fail| FixDevice[Fix Device Issues]
    FixDevice --> DeviceTests
    
    subgraph "Test Categories"
        ConfigTests[Config Integrity Tests]
        SchemaTests[Schema Validation Tests]
        FakeDeviceTests[Fake Device Simulator Tests]
        CalibrationTests[Calibration Tests]
        AndroidInstrTests[Android Instrumentation Tests]
    end
    
    UnitTests --> ConfigTests
    UnitTests --> SchemaTests
    IntegrationTests --> FakeDeviceTests
    IntegrationTests --> CalibrationTests
    CrossPlatform --> AndroidInstrTests
    
    style Start fill:#c8e6c9
    style Complete fill:#c8e6c9
    style FixIssues fill:#ffcdd2
    style FixIntegration fill:#ffcdd2
    style FixProtocol fill:#ffcdd2
    style FixDevice fill:#ffcdd2
```

## Development Workflow Integration

```mermaid
flowchart TD
    Start([Initial Milestone 4]) --> ProtocolBranch{Create Protocol Schema}
    
    ProtocolBranch --> Schema[Create message_schema.json]
    Schema --> Config[Create config.json]
    Config --> PySchema[Python SchemaManager]
    PySchema --> PyConfig[Python ConfigManager]
    PyConfig --> ProtocolMerge[Merge Protocol Schema]
    
    ProtocolMerge --> AndroidBranch{Android Integration}
    AndroidBranch --> AndroidSchema[Android SchemaManager]
    AndroidSchema --> AndroidConfig[Android ConfigManager]
    AndroidConfig --> AssetIntegration[Asset Integration]
    AssetIntegration --> AndroidMerge[Merge Android Integration]
    
    AndroidMerge --> TestBranch{Test Harnesses}
    TestBranch --> FakeDevice[Fake Device Simulator]
    FakeDevice --> CalibTests[Calibration Tests]
    CalibTests --> IntegrityTests[Integrity Tests]
    IntegrityTests --> AndroidTests[Android Instrumentation Tests]
    AndroidTests --> TestMerge[Merge Test Harnesses]
    
    TestMerge --> Documentation[Documentation Update]
    Documentation --> Complete([Milestone 4 Complete])
    
    style Start fill:#c8e6c9
    style Complete fill:#c8e6c9
    style ProtocolBranch fill:#e1f5fe
    style AndroidBranch fill:#e8f5e8
    style TestBranch fill:#fff3e0
```

## Key Benefits of Milestone 4 Architecture

1. **Unified Protocol**: Single source of truth for message formats across platforms
2. **Shared Configuration**: Consistent parameters between Python and Android
3. **Runtime Loading**: Dynamic schema and config loading for flexibility
4. **Comprehensive Testing**: Offline testing capabilities without physical devices
5. **Cross-Platform Validation**: Consistent message validation on both platforms
6. **Maintainable Structure**: Monorepo approach for easy synchronization
7. **Development Support**: Enhanced workflow with comprehensive test harnesses

This architecture ensures reliable communication, consistent behavior, and maintainable code across the synchronized multimodal recording system.
