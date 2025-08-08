# F4: Synchronized Start Trigger Timeline

```mermaid
sequenceDiagram
    participant PC as PC Master
    participant N1 as Android Node 1<br/>(Offset: -2.1ms)
    participant N2 as Android Node 2<br/>(Offset: +1.3ms)
    participant N3 as Android Node 3<br/>(Offset: -0.7ms)
    
    Note over PC,N3: t=0ms: Master Timestamp Generated
    
    PC->>N1: START_RECORDING(t=0)
    PC->>N2: START_RECORDING(t=0)
    PC->>N3: START_RECORDING(t=0)
    
    Note over N1: t=2ms: Command received<br/>Apply offset: -2.1ms
    Note over N2: t=1ms: Command received<br/>Apply offset: +1.3ms
    Note over N3: t=3ms: Command received<br/>Apply offset: -0.7ms
    
    Note over N1: t=5ms: Effective start time<br/>t + offset = 2 - 2.1 = -0.1ms
    Note over N2: t=5ms: Effective start time<br/>t + offset = 1 + 1.3 = 2.3ms
    Note over N3: t=5ms: Effective start time<br/>t + offset = 3 - 0.7 = 2.3ms
    
    par Synchronized Capture Start
        N1->>N1: Begin RGB/Thermal/GSR
    and
        N2->>N2: Begin RGB/Thermal/GSR  
    and
        N3->>N3: Begin RGB/Thermal/GSR
    end
    
    Note over PC,N3: Sync Window: ±5ms target<br/>Actual jitter: 2.4ms range
```

## Timeline Analysis
- **Master Timestamp**: t=0 (PC local time)
- **Node 1 Offset**: -2.1ms → Effective start at t=10ms
- **Node 2 Offset**: +1.3ms → Effective start at t=11ms  
- **Node 3 Offset**: -0.7ms → Effective start at t=12ms
- **Sync Jitter**: 2ms range (within ±5ms target window)

## Description
Shows temporal alignment of recording start across distributed nodes. Each device applies its calculated clock offset to achieve synchronized capture initiation within the target timing window.