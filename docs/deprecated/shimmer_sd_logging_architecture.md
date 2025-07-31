# Shimmer SD Logging Architecture

This document describes the architectural changes made for Shimmer SD logging integration.

## SD Logging Integration Architecture

```mermaid
graph TB
    subgraph "UI Layer"
        MA[MainActivity]
        UI[User Interface]
    end
    
    subgraph "ViewModel Layer"
        MVM[MainViewModel]
        WM1[startShimmerSDLogging]
        WM2[stopShimmerSDLogging]
        WM3[isAnyShimmerDeviceStreaming]
        WM4[isAnyShimmerDeviceSDLogging]
        WM5[getConnectedShimmerDevice]
        WM6[getShimmerBluetoothManager]
    end
    
    subgraph "Business Logic Layer"
        SR[ShimmerRecorder]
        SDL1[startSDLogging]
        SDL2[stopSDLogging]
        SDL3[isAnyDeviceStreaming]
        SDL4[isAnyDeviceSDLogging]
        SDL5[getConnectedShimmerDevice]
        SDL6[getShimmerBluetoothManager]
    end
    
    subgraph "Shimmer SDK Layer"
        SBM[ShimmerBluetoothManagerAndroid]
        SD[ShimmerDevice]
        BT[Bluetooth Communication]
    end
    
    subgraph "Hardware Layer"
        HW[Shimmer3 GSR+ Devices]
        SD_CARD[SD Card Storage]
    end
    
    %% UI to ViewModel connections
    MA --> WM1
    MA --> WM2
    MA --> WM3
    MA --> WM4
    UI --> MA
    
    %% ViewModel to Business Logic connections
    WM1 --> SDL1
    WM2 --> SDL2
    WM3 --> SDL3
    WM4 --> SDL4
    WM5 --> SDL5
    WM6 --> SDL6
    
    %% Business Logic to SDK connections
    SDL1 --> SBM
    SDL2 --> SBM
    SDL3 --> SD
    SDL4 --> SD
    SDL5 --> SD
    SDL6 --> SBM
    
    %% SDK to Hardware connections
    SBM --> BT
    SD --> BT
    BT --> HW
    HW --> SD_CARD
    
    %% Callback flow
    SDL1 -.->|Callback| WM1
    SDL2 -.->|Callback| WM2
    WM1 -.->|UI Update| MA
    WM2 -.->|UI Update| MA
    
    classDef uiLayer fill:#e1f5fe
    classDef viewModelLayer fill:#f3e5f5
    classDef businessLayer fill:#e8f5e8
    classDef sdkLayer fill:#fff3e0
    classDef hardwareLayer fill:#ffebee
    
    class MA,UI uiLayer
    class MVM,WM1,WM2,WM3,WM4,WM5,WM6 viewModelLayer
    class SR,SDL1,SDL2,SDL3,SDL4,SDL5,SDL6 businessLayer
    class SBM,SD,BT sdkLayer
    class HW,SD_CARD hardwareLayer
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant UI as MainActivity
    participant VM as MainViewModel
    participant SR as ShimmerRecorder
    participant SDK as Shimmer SDK
    participant HW as Hardware
    
    Note over UI,HW: SD Logging Start Flow
    
    UI->>VM: startShimmerSDLogging()
    VM->>VM: Check device states
    VM->>SR: startSDLogging()
    SR->>SDK: Collect connected devices
    SR->>SDK: writeConfigTime()
    SR->>SDK: startSDLogging(deviceList)
    SDK->>HW: Start SD logging
    HW-->>SDK: Logging started
    SDK-->>SR: Success response
    SR-->>VM: Return success
    VM->>VM: Execute callback
    VM-->>UI: UI update (runOnUiThread)
    UI->>UI: Show success toast
    
    Note over UI,HW: SD Logging Stop Flow
    
    UI->>VM: stopShimmerSDLogging()
    VM->>VM: Check logging state
    VM->>SR: stopSDLogging()
    SR->>SDK: Collect connected devices
    SR->>SDK: stopSDLogging(deviceList)
    SDK->>HW: Stop SD logging
    HW-->>SDK: Logging stopped
    SDK-->>SR: Success response
    SR-->>VM: Return success
    VM->>VM: Execute callback
    VM-->>UI: UI update (runOnUiThread)
    UI->>UI: Show success toast
```

## Thread Safety Architecture

```mermaid
graph LR
    subgraph "Main Thread"
        UI[UI Components]
        TOAST[Toast Messages]
        LIFECYCLE[Activity Lifecycle]
    end
    
    subgraph "ViewModel Scope"
        VMSCOPE[viewModelScope.launch]
        CALLBACK[Callback Execution]
    end
    
    subgraph "IO Thread"
        SHIMMER[ShimmerRecorder Operations]
        SDK[Shimmer SDK Calls]
        BLUETOOTH[Bluetooth Communication]
    end
    
    subgraph "Background Thread"
        LOGGING[SD Card Logging]
        DEVICE[Device Management]
    end
    
    UI --> VMSCOPE
    VMSCOPE --> SHIMMER
    SHIMMER --> SDK
    SDK --> BLUETOOTH
    BLUETOOTH --> LOGGING
    LOGGING --> DEVICE
    
    CALLBACK -.->|runOnUiThread| UI
    CALLBACK -.->|runOnUiThread| TOAST
    
    classDef mainThread fill:#ffcdd2
    classDef viewModelThread fill:#f8bbd9
    classDef ioThread fill:#c8e6c9
    classDef backgroundThread fill:#dcedc8
    
    class UI,TOAST,LIFECYCLE mainThread
    class VMSCOPE,CALLBACK viewModelThread
    class SHIMMER,SDK,BLUETOOTH ioThread
    class LOGGING,DEVICE backgroundThread
```

## Error Handling Architecture

```mermaid
graph TD
    START[User Action] --> CHECK{State Check}
    CHECK -->|Invalid State| ERROR1[Show Error Toast]
    CHECK -->|Valid State| EXECUTE[Execute Operation]
    
    EXECUTE --> TRY{Try Operation}
    TRY -->|Success| SUCCESS[Show Success Toast]
    TRY -->|Exception| CATCH[Catch Exception]
    
    CATCH --> LOG[Log Error]
    LOG --> ERROR2[Show Error Toast]
    
    SUCCESS --> END[Operation Complete]
    ERROR1 --> END
    ERROR2 --> END
    
    classDef successPath fill:#c8e6c9
    classDef errorPath fill:#ffcdd2
    classDef checkPath fill:#fff3e0
    
    class START,CHECK,EXECUTE,TRY,SUCCESS,END successPath
    class ERROR1,ERROR2,CATCH,LOG errorPath
    class CHECK,TRY checkPath
```

## Key Architectural Benefits

### 1. **Separation of Concerns**
- UI layer handles user interactions and display
- ViewModel layer manages state and coordinates operations
- Business logic layer handles Shimmer-specific operations
- SDK layer provides hardware abstraction

### 2. **Thread Safety**
- All UI updates use `runOnUiThread` for main thread safety
- Shimmer operations run on IO dispatcher
- Callback-based architecture prevents blocking

### 3. **Error Handling**
- Comprehensive state validation before operations
- Graceful error recovery with user feedback
- Detailed logging for troubleshooting

### 4. **Maintainability**
- Clear separation between layers
- Wrapper methods provide clean API
- Consistent error handling patterns

### 5. **Testability**
- ViewModel wrapper methods can be easily mocked
- Clear interfaces between layers
- Callback-based architecture supports testing