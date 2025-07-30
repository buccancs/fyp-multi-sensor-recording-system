# Milestone 6: Schema Synchronization Architecture

This diagram illustrates the architectural changes introduced in Milestone 6 for shared constants and schema synchronization between the Android and Python applications.

## Architecture Overview

```mermaid
graph TB
    subgraph "Shared Protocol Definition"
        CONFIG["`**protocol/config.json**
        • Protocol version: 1
        • Network settings
        • Device parameters
        • Calibration constants
        • UI configuration`"]
        
        SCHEMA["`**protocol/message_schema.json**
        • Unified message types
        • Field validation rules
        • Handshake protocol
        • Base message structure`"]
    end
    
    subgraph "Android Application"
        subgraph "Build Process"
            GRADLE["`**Gradle Build Task**
            generateConstants`"]
            CONSTANTS_KT["`**CommonConstants.kt**
            (Generated)
            • PROTOCOL_VERSION
            • Network.*
            • Devices.*
            • Calibration.*`"]
        end
        
        subgraph "Runtime Components"
            SCHEMA_MGR_A["`**SchemaManager**
            • Message validation
            • Message creation
            • Type extraction`"]
            
            HANDSHAKE_MGR_A["`**HandshakeManager**
            • Send handshake
            • Process handshake_ack
            • Version compatibility`"]
            
            CONFIG_MGR_A["`**ConfigManager**
            • Load from assets
            • Access configuration`"]
        end
    end
    
    subgraph "Python Application"
        subgraph "Runtime Components"
            CONFIG_MGR_P["`**ConfigManager**
            • Load JSON at runtime
            • Dot-notation access
            • Section getters`"]
            
            SCHEMA_MGR_P["`**SchemaManager**
            • Message validation
            • Message creation
            • Optional jsonschema`"]
            
            HANDSHAKE_MGR_P["`**HandshakeManager**
            • Process handshake
            • Send handshake_ack
            • Version checking`"]
        end
    end
    
    subgraph "Communication Flow"
        HANDSHAKE_FLOW["`**Handshake Protocol**
        1. Android → handshake
        2. Python → handshake_ack
        3. Version compatibility check
        4. Connection established`"]
        
        MESSAGE_FLOW["`**Message Exchange**
        • All messages validated
        • Schema compliance
        • Type safety
        • Error handling`"]
    end
    
    %% Relationships
    CONFIG --> GRADLE
    GRADLE --> CONSTANTS_KT
    CONSTANTS_KT --> HANDSHAKE_MGR_A
    CONSTANTS_KT --> CONFIG_MGR_A
    
    CONFIG --> CONFIG_MGR_P
    SCHEMA --> SCHEMA_MGR_A
    SCHEMA --> SCHEMA_MGR_P
    
    SCHEMA_MGR_A --> HANDSHAKE_MGR_A
    SCHEMA_MGR_P --> HANDSHAKE_MGR_P
    
    HANDSHAKE_MGR_A <--> HANDSHAKE_FLOW
    HANDSHAKE_MGR_P <--> HANDSHAKE_FLOW
    
    SCHEMA_MGR_A <--> MESSAGE_FLOW
    SCHEMA_MGR_P <--> MESSAGE_FLOW
    
    %% Styling
    classDef sharedFile fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef androidComp fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef pythonComp fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef commFlow fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef generated fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class CONFIG,SCHEMA sharedFile
    class GRADLE,CONSTANTS_KT,SCHEMA_MGR_A,HANDSHAKE_MGR_A,CONFIG_MGR_A androidComp
    class CONFIG_MGR_P,SCHEMA_MGR_P,HANDSHAKE_MGR_P pythonComp
    class HANDSHAKE_FLOW,MESSAGE_FLOW commFlow
    class CONSTANTS_KT generated
```

## Key Benefits

### 1. Single Source of Truth
- **Shared Configuration**: Both applications use identical constants from `protocol/config.json`
- **Unified Schema**: All message types defined in `protocol/message_schema.json`
- **Automatic Synchronization**: Changes propagate to both sides (Android after rebuild, Python immediately)

### 2. Version Compatibility
- **Protocol Versioning**: Explicit version checking prevents silent failures
- **Handshake Protocol**: Connection establishment with compatibility verification
- **Error Detection**: Early detection of version mismatches with clear error messages

### 3. Type Safety and Validation
- **Schema Validation**: All messages validated against unified schema
- **Generated Constants**: Android gets compile-time type safety through code generation
- **Runtime Validation**: Python validates messages at runtime with detailed error reporting

### 4. Maintainability
- **Centralized Changes**: Modify constants in one place, automatically sync everywhere
- **Clear Architecture**: Well-defined components with specific responsibilities
- **Comprehensive Testing**: Both unit and integration tests ensure reliability

## Implementation Details

### Android Side
1. **Build-Time Generation**: Gradle task generates `CommonConstants.kt` from shared config
2. **Asset Integration**: Schema and config files bundled as Android assets
3. **Manager Classes**: `SchemaManager`, `HandshakeManager`, and `ConfigManager` handle protocol logic
4. **Type Safety**: Compile-time constants with proper Kotlin types

### Python Side
1. **Runtime Loading**: Configuration loaded dynamically from JSON files
2. **Flexible Access**: Dot-notation access to nested configuration values
3. **Optional Dependencies**: Graceful degradation when optional libraries unavailable
4. **Manager Classes**: Matching functionality to Android implementation

### Communication Protocol
1. **Connection Establishment**: Handshake exchange with version verification
2. **Message Validation**: All messages validated against unified schema
3. **Error Handling**: Clear error messages and graceful failure handling
4. **Extensibility**: Forward-compatible design allows schema evolution

This architecture ensures robust, maintainable communication between the Android and Python applications while eliminating synchronization issues and providing clear upgrade paths for future enhancements.
