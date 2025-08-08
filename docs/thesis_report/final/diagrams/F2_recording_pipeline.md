# F2: Recording Pipeline & Session Flow

```mermaid
sequenceDiagram
    participant PC as PC Controller
    participant AN1 as Android Node 1
    participant AN2 as Android Node 2
    participant ANn as Android Node N
    
    Note over PC,ANn: Session Initialization
    PC->>AN1: Discovery & Handshake
    PC->>AN2: Discovery & Handshake
    PC->>ANn: Discovery & Handshake
    
    AN1-->>PC: Capabilities Response
    AN2-->>PC: Capabilities Response
    ANn-->>PC: Capabilities Response
    
    Note over PC,ANn: Synchronization Setup
    PC->>AN1: Time Sync Request
    PC->>AN2: Time Sync Request
    PC->>ANn: Time Sync Request
    
    AN1-->>PC: Sync Response (offset)
    AN2-->>PC: Sync Response (offset)
    ANn-->>PC: Sync Response (offset)
    
    Note over PC,ANn: Coordinated Recording Start
    PC->>PC: Generate Master Timestamp
    
    par Simultaneous Broadcast
        PC->>AN1: START_RECORDING(master_ts)
        PC->>AN2: START_RECORDING(master_ts)
        PC->>ANn: START_RECORDING(master_ts)
    end
    
    Note over AN1,ANn: Local Recording Phase
    
    par Parallel Capture
        AN1->>AN1: RGB Video Capture
        AN1->>AN1: Thermal Video Capture
        AN1->>AN1: GSR Data Logging
    and
        AN2->>AN2: RGB Video Capture
        AN2->>AN2: Thermal Video Capture
        AN2->>AN2: GSR Data Logging
    and
        ANn->>ANn: RGB Video Capture
        ANn->>ANn: Thermal Video Capture
        ANn->>ANn: GSR Data Logging
    end
    
    Note over PC,ANn: Session Termination
    PC->>AN1: STOP_RECORDING
    PC->>AN2: STOP_RECORDING
    PC->>ANn: STOP_RECORDING
    
    AN1-->>PC: Recording Complete
    AN2-->>PC: Recording Complete
    ANn-->>PC: Recording Complete
    
    Note over PC,ANn: Data Transfer Phase
    par File Transfer
        AN1->>PC: Transfer Video Files
        AN1->>PC: Transfer GSR Data
        AN1->>PC: Transfer Metadata
    and
        AN2->>PC: Transfer Video Files
        AN2->>PC: Transfer GSR Data
        AN2->>PC: Transfer Metadata
    and
        ANn->>PC: Transfer Video Files
        ANn->>PC: Transfer GSR Data
        ANn->>PC: Transfer Metadata
    end
    
    PC->>PC: Consolidate Session Data
```

## Description
Illustrates the complete recording workflow from device discovery through data consolidation. Shows parallel capture coordination and the offline-first approach with post-session file transfer.